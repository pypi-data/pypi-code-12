import os
import re

from django.core.management.base import NoArgsCommand
from django.conf import settings

"""Management command for generating graphviz .DOT files of the template
inheritance path, for template debugging and maintenance"""

class InvalidTemplate(Exception):
    """Because we cannot determine which files we encounter genuinely are
    Django templates, we must attempt to read them and consider them if
    they are valid Django templates in the correct character set.

    This Exception is raised when a template is not valid."""


class InheritanceGraph(object):
    def __init__(self):
        self.templates = {}

    def add_template(self, name, extends=None, includes=[], calls=[]):
        self.templates[name] = extends, includes, calls

    def as_dot(self):
        node_defs = ''
        nodes = {}
        i = 1
        for k, v in self.templates.items():
            extends, includes, calls = v
            nodes[k] = 'node%d' % i, extends, includes, calls
            i += 1

        ks = nodes.keys()
        ks.sort()

        for k in ks:
            node, extends, includes, calls = nodes[k]
            node_defs += "\t%s [label=\"%s\"];\n" % (node, k)

        inheritance_edges = ''
        inclusion_edges = ''
        call_edges = ''

        for t, v in nodes.items():
            node, extends, includes, calls = v
            if extends is not None:
                e = nodes.get(extends.encode('utf8'), None)
                if e:
                    inheritance_edges += "\t%s -> %s;\n" % (node, e[0])
            for include in includes:
                e = nodes.get(include.encode('utf8'), None)
                if e:
                    inclusion_edges += "\t%s -> %s;\n" % (node, e[0])
            for call in calls:
                e = nodes.get(call.encode('utf8'), None)
                if e:
                    call_edges += "\t%s -> %s;\n" % (node, e[0])

        return """digraph template_tree {
graph [rankdir=LR];
node [shape=box,fontname="Arial",fontsize=10,style="filled",fillcolor="#EEEEFF",color="#8888CC",height=0.3];
%s
%s
edge [color=blue];
%s
edge [color=red];
%s
}""" % (node_defs, inheritance_edges, inclusion_edges, call_edges)

def display_graph(graph):
    import os
    import subprocess
    import tempfile
    dotfd, dotname = tempfile.mkstemp(suffix='.dot')
    dot = os.fdopen(dotfd, 'w')
    dot.write(graph.as_dot())
    dot.close()
    outfile = dotname.replace('.dot', '.svgz')
    graphviz = subprocess.Popen(['dot', '-Tsvgz', '-o' + outfile, dotname], close_fds=True)
    graphviz.wait()
    eog = subprocess.Popen(['eog', outfile])
    eog.wait()
    os.unlink(outfile)
    os.unlink(dotname)


class Command(NoArgsCommand):
    requires_model_validation = False

    def handle_noargs(self, **options):
        graph = InheritanceGraph()

        if 'django.template.loaders.app_directories.load_template_source' in settings.TEMPLATE_LOADERS:
            self.search_app_directories(graph)

        if 'django.template.loaders.filesystem.load_template_source' in settings.TEMPLATE_LOADERS:
            self.search_filesystem(graph)

        display_graph(graph)

    def inspect_template(self, path):
        f = open(path, 'rU')
        try:
            templ = f.read().decode(settings.FILE_CHARSET)
        except UnicodeDecodeError:
            raise InvalidTemplate('%s is not a valid Django template' % path)
        finally:
            f.close()

        templ = re.sub(r'{#.*?#}', '', templ)
        templ = re.sub(r'\{%\s*comment\s*%\}[.\n]*?\{%\s*endcomment\s*%\}', '', templ)

        mo = re.match(r'^\s*\{%\s*extends\s+"([^"]+)"\s*%\}', templ)

        if mo:
            extends = mo.group(1)
        else:
            extends = None

        includes = []
        for mo in re.finditer(r'\{%\s*include\s+"([^"]+)"\s*%\}', templ):
            includes.append(mo.group(1))

        calls = []
        for mo in re.finditer(r'\{%\s*call\s+"([^"]+)"\s*%\}', templ):
            calls.append(mo.group(1))

        return extends, includes, calls

    def search_app_directories(self, graph):
        from django.template.loaders.app_directories import app_template_dirs
        for d in app_template_dirs:
            for f in self.search_directory(d):
                try:
                    extends, includes, calls = self.inspect_template(f)
                except InvalidTemplate:
                    continue
                fname = f[len(d):]
                if fname.startswith('/'):
                    fname = fname[1:]
                graph.add_template(fname, extends, includes, calls)

    def search_filesystem(self, graph):
        for d in settings.TEMPLATE_DIRS:
            for f in self.search_directory(d):
                try:
                    extends, includes, calls = self.inspect_template(f)
                except InvalidTemplate:
                    continue
                fname = f[len(d):]
                if fname.startswith('/'):
                    fname = fname[1:]
                graph.add_template(fname, extends, includes, calls)

    def search_directory(self, dir):
        for root, dirs, files in os.walk(dir):
            for excl in ['.svn', 'CVS']:
                if excl in dirs:
                    dirs.remove(excl)
            for f in files:
                yield os.path.join(root, f)
