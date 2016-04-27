import os
import re

from django.core.management.base import NoArgsCommand
from django.db import models

"""Management command for generating graphviz .DOT files of model relationships."""

class DotGraph(object):
    def __init__(self, node_label_callback=repr):
        self.nodes = set()
        self.edges = {}
        self.edge_classes = {}
        self.node_label_callback = node_label_callback

    def create_edge_class(self, type):
        id = len(self.edge_classes) + 1
        self.edge_classes[id] = type
        return id

    def add_edge(self, edge_class, source, dest, label=None):
        self.nodes.add(source)
        self.nodes.add(dest)
        try:
            self.edges[edge_class].add((source, dest, label))
        except KeyError:
            self.edges[edge_class] = set([(source, dest, label)])

    def as_dot(self):
        s = """digraph template_tree {
graph [rankdir=LR];
node [shape=box,fontname="Arial",fontsize=10,style="filled",fillcolor="#EEEEFF",color="#8888CC"];"""

        node_map = {}
        for i, n in enumerate(self.nodes):
            s += 'node%d [label="%s"];\n' % (i, self.node_label_callback(n))
            node_map[n] = i

        for k, type in self.edge_classes.items():
            try:
                es = self.edges[k]
            except KeyError:
                continue

            s += 'edge [%s];\n' % type
            for source, dest, label in es:
                if label:
                    s += 'node%d -> node%d [label="%s"];\n' % (node_map[source], node_map[dest], label)
                else:
                    s += 'node%d -> node%d;\n' % (node_map[source], node_map[dest])

        s += '}'
        return s

    def display(self):
        import os
        import subprocess
        import tempfile
        dotfd, dotname = tempfile.mkstemp(suffix='.dot')
        dot = os.fdopen(dotfd, 'w')
        dot.write(self.as_dot())
        dot.close()
        outfile = dotname.replace('.dot', '.svgz')
        graphviz = subprocess.Popen(['dot', '-Tsvgz', '-o' + outfile, dotname], close_fds=True)
        graphviz.wait()
        eog = subprocess.Popen(['eog', outfile])
        eog.wait()
        os.unlink(outfile)
        os.unlink(dotname)


def create_model_graph():
    g = DotGraph(node_label_callback=lambda m: m._meta.app_label + '.' + m._meta.object_name)
    FOREIGNKEY = g.create_edge_class('color=blue,fontname="Arial",fontsize=8,fontcolor=blue')
    MANY_TO_MANY = g.create_edge_class('color=red,fontname="Arial",fontsize=8,fontcolor=red')
    ONE_TO_ONE = g.create_edge_class('color=green,fontname="Arial",fontsize=8,fontcolor=green')
    for m in models.get_models():
        for f in m._meta.fields:
            if isinstance(f, models.ForeignKey):
                def_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', f.rel.to._meta.object_name).lower()
                if f.name == def_name:
                    g.add_edge(FOREIGNKEY, m, f.rel.to)
                else:
                    g.add_edge(FOREIGNKEY, m, f.rel.to, label=f.name)

        for f in m._meta.local_many_to_many:
            g.add_edge(MANY_TO_MANY, m, f.rel.to, label=f.name)

        if m._meta.one_to_one_field:
            g.add_edge(ONE_TO_ONE, m, m._meta.one_to_one_field.rel.to)
    return g



class Command(NoArgsCommand):
    requires_model_validation = True

    def handle_noargs(self, **options):
        graph = create_model_graph()
        graph.display()
