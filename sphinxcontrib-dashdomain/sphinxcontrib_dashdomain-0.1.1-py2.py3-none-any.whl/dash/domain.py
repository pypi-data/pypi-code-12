# -*- coding: utf-8 -*-
"""
    sphinx.domains.dash
    ~~~~~~~~~~~~~~~~~~~

    The DASH documentation domain

    :copyright: Copyright 2016 by @togakushi
    :license: BSD, see LICENSE for details.
"""

from six import iteritems

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class DashDirective(ObjectDescription):
    """
    Description of dash directive.
    """
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig

    def add_target_and_index(self, name, sig, signode):
        targetname = self.objtype + '-' + name
        if targetname not in self.state.document.ids:
            signode['names'].append(targetname)
            signode['ids'].append(targetname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

            objects = self.env.domaindata['dash']['objects']
            key = (self.objtype, name)
            if key in objects:
                self.state_machine.reporter.warning(
                    'duplicate description of %s %s, ' % (self.objtype, name) +
                    'other instance in ' + self.env.doc2path(objects[key]),
                    line=self.lineno)
            objects[key] = self.env.docname

        indextext = _('%s (%s)') % (name, self.objtype.title())
        self.indexnode['entries'].append(('single', indextext, targetname, ''))


class DashDomain(Domain):
    """Dash documentation  domain."""
    name = 'dash'
    label = 'Dash documentation'

    object_types = {
        'annotation': ObjType(l_('annotation'), 'annotation', 'obj'),
        'attribute': ObjType(l_('attribute'), 'attribute', 'obj'),
        'binding': ObjType(l_('binding'), 'binding', 'obj'),
        'builtin': ObjType(l_('builtin'), 'builtin', 'obj'),
        'callback': ObjType(l_('callback'), 'callback', 'obj'),
        'category': ObjType(l_('category'), 'category', 'obj'),
        'class': ObjType(l_('class'), 'class', 'obj'),
        'command': ObjType(l_('command'), 'command', 'obj'),
        'component': ObjType(l_('component'), 'component', 'obj'),
        'constant': ObjType(l_('constant'), 'constant', 'obj'),
        'constructor': ObjType(l_('constructor'), 'constructor', 'obj'),
        'define': ObjType(l_('define'), 'define', 'obj'),
        'delegate': ObjType(l_('delegate'), 'delegate', 'obj'),
        'diagram': ObjType(l_('diagram'), 'diagram', 'obj'),
        'directive': ObjType(l_('directive'), 'directive', 'obj'),
        'element': ObjType(l_('element'), 'element', 'obj'),
        'entry': ObjType(l_('entry'), 'entry', 'obj'),
        'enum': ObjType(l_('enum'), 'enum', 'obj'),
        'environment': ObjType(l_('environment'), 'environment', 'obj'),
        'error': ObjType(l_('error'), 'error', 'obj'),
        'event': ObjType(l_('event'), 'event', 'obj'),
        'exception': ObjType(l_('exception'), 'exception', 'obj'),
        'extension': ObjType(l_('extension'), 'extension', 'obj'),
        'field': ObjType(l_('field'), 'field', 'obj'),
        'file': ObjType(l_('file'), 'file', 'obj'),
        'filter': ObjType(l_('filter'), 'filter', 'obj'),
        'framework': ObjType(l_('framework'), 'framework', 'obj'),
        'function': ObjType(l_('function'), 'function', 'obj'),
        'global': ObjType(l_('global'), 'global', 'obj'),
        'guide': ObjType(l_('guide'), 'guide', 'obj'),
        'hook': ObjType(l_('hook'), 'hook', 'obj'),
        'instance': ObjType(l_('instance'), 'instance', 'obj'),
        'instruction': ObjType(l_('instruction'), 'instruction', 'obj'),
        'interface': ObjType(l_('interface'), 'interface', 'obj'),
        'keyword': ObjType(l_('keyword'), 'keyword', 'obj'),
        'library': ObjType(l_('library'), 'library', 'obj'),
        'literal': ObjType(l_('literal'), 'literal', 'obj'),
        'macro': ObjType(l_('macro'), 'macro', 'obj'),
        'method': ObjType(l_('method'), 'method', 'obj'),
        'mixin': ObjType(l_('mixin'), 'mixin', 'obj'),
        'modifier': ObjType(l_('modifier'), 'modifier', 'obj'),
        'module': ObjType(l_('module'), 'module', 'obj'),
        'namespace': ObjType(l_('namespace'), 'namespace', 'obj'),
        'notation': ObjType(l_('notation'), 'notation', 'obj'),
        'object': ObjType(l_('object'), 'object', 'obj'),
        'operator': ObjType(l_('operator'), 'operator', 'obj'),
        'option': ObjType(l_('option'), 'option', 'obj'),
        'package': ObjType(l_('package'), 'package', 'obj'),
        'parameter': ObjType(l_('parameter'), 'parameter', 'obj'),
        'plugin': ObjType(l_('plugin'), 'plugin', 'obj'),
        'procedure': ObjType(l_('procedure'), 'procedure', 'obj'),
        'property': ObjType(l_('property'), 'property', 'obj'),
        'protocol': ObjType(l_('protocol'), 'protocol', 'obj'),
        'provider': ObjType(l_('provider'), 'provider', 'obj'),
        'provisioner': ObjType(l_('provisioner'), 'provisioner', 'obj'),
        'query': ObjType(l_('query'), 'query', 'obj'),
        'record': ObjType(l_('record'), 'record', 'obj'),
        'resource': ObjType(l_('resource'), 'resource', 'obj'),
        'sample': ObjType(l_('sample'), 'sample', 'obj'),
        'section': ObjType(l_('section'), 'section', 'obj'),
        'service': ObjType(l_('service'), 'service', 'obj'),
        'setting': ObjType(l_('setting'), 'setting', 'obj'),
        'shortcut': ObjType(l_('shortcut'), 'shortcut', 'obj'),
        'statement': ObjType(l_('statement'), 'statement', 'obj'),
        'struct': ObjType(l_('struct'), 'struct', 'obj'),
        'style': ObjType(l_('style'), 'style', 'obj'),
        'subroutine': ObjType(l_('subroutine'), 'subroutine', 'obj'),
        'tag': ObjType(l_('tag'), 'tag', 'obj'),
        'test': ObjType(l_('test'), 'test', 'obj'),
        'trait': ObjType(l_('trait'), 'trait', 'obj'),
        'type': ObjType(l_('type'), 'type', 'obj'),
        'union': ObjType(l_('union'), 'union', 'obj'),
        'value': ObjType(l_('value'), 'value', 'obj'),
        'variable': ObjType(l_('variable'), 'variable', 'obj'),
        'word': ObjType(l_('word'), 'word', 'obj'),
    }
    directives = {
        'annotation': DashDirective,
        'attribute': DashDirective,
        'binding': DashDirective,
        'builtin': DashDirective,
        'callback': DashDirective,
        'category': DashDirective,
        'class': DashDirective,
        'command': DashDirective,
        'component': DashDirective,
        'constant': DashDirective,
        'constructor': DashDirective,
        'define': DashDirective,
        'delegate': DashDirective,
        'diagram': DashDirective,
        'directive': DashDirective,
        'element': DashDirective,
        'entry': DashDirective,
        'enum': DashDirective,
        'environment': DashDirective,
        'error': DashDirective,
        'event': DashDirective,
        'exception': DashDirective,
        'extension': DashDirective,
        'field': DashDirective,
        'file': DashDirective,
        'filter': DashDirective,
        'framework': DashDirective,
        'function': DashDirective,
        'global': DashDirective,
        'guide': DashDirective,
        'hook': DashDirective,
        'instance': DashDirective,
        'instruction': DashDirective,
        'interface': DashDirective,
        'keyword': DashDirective,
        'library': DashDirective,
        'literal': DashDirective,
        'macro': DashDirective,
        'method': DashDirective,
        'mixin': DashDirective,
        'modifier': DashDirective,
        'module': DashDirective,
        'namespace': DashDirective,
        'notation': DashDirective,
        'object': DashDirective,
        'operator': DashDirective,
        'option': DashDirective,
        'package': DashDirective,
        'parameter': DashDirective,
        'plugin': DashDirective,
        'procedure': DashDirective,
        'property': DashDirective,
        'protocol': DashDirective,
        'provider': DashDirective,
        'provisioner': DashDirective,
        'query': DashDirective,
        'record': DashDirective,
        'resource': DashDirective,
        'sample': DashDirective,
        'section': DashDirective,
        'service': DashDirective,
        'setting': DashDirective,
        'shortcut': DashDirective,
        'statement': DashDirective,
        'struct': DashDirective,
        'style': DashDirective,
        'subroutine': DashDirective,
        'tag': DashDirective,
        'test': DashDirective,
        'trait': DashDirective,
        'type': DashDirective,
        'union': DashDirective,
        'value': DashDirective,
        'variable': DashDirective,
        'word': DashDirective,
    }
    roles = {
        'annotation': XRefRole(),
        'attribute': XRefRole(),
        'binding': XRefRole(),
        'builtin': XRefRole(),
        'callback': XRefRole(),
        'category': XRefRole(),
        'class': XRefRole(),
        'command': XRefRole(),
        'component': XRefRole(),
        'constant': XRefRole(),
        'constructor': XRefRole(),
        'define': XRefRole(),
        'delegate': XRefRole(),
        'diagram': XRefRole(),
        'directive': XRefRole(),
        'element': XRefRole(),
        'entry': XRefRole(),
        'enum': XRefRole(),
        'environment': XRefRole(),
        'error': XRefRole(),
        'event': XRefRole(),
        'exception': XRefRole(),
        'extension': XRefRole(),
        'field': XRefRole(),
        'file': XRefRole(),
        'filter': XRefRole(),
        'framework': XRefRole(),
        'function': XRefRole(),
        'global': XRefRole(),
        'guide': XRefRole(),
        'hook': XRefRole(),
        'instance': XRefRole(),
        'instruction': XRefRole(),
        'interface': XRefRole(),
        'keyword': XRefRole(),
        'library': XRefRole(),
        'literal': XRefRole(),
        'macro': XRefRole(),
        'method': XRefRole(),
        'mixin': XRefRole(),
        'modifier': XRefRole(),
        'module': XRefRole(),
        'namespace': XRefRole(),
        'notation': XRefRole(),
        'object': XRefRole(),
        'operator': XRefRole(),
        'option': XRefRole(),
        'package': XRefRole(),
        'parameter': XRefRole(),
        'plugin': XRefRole(),
        'procedure': XRefRole(),
        'property': XRefRole(),
        'protocol': XRefRole(),
        'provider': XRefRole(),
        'provisioner': XRefRole(),
        'query': XRefRole(),
        'record': XRefRole(),
        'resource': XRefRole(),
        'sample': XRefRole(),
        'section': XRefRole(),
        'service': XRefRole(),
        'setting': XRefRole(),
        'shortcut': XRefRole(),
        'statement': XRefRole(),
        'struct': XRefRole(),
        'style': XRefRole(),
        'subroutine': XRefRole(),
        'tag': XRefRole(),
        'test': XRefRole(),
        'trait': XRefRole(),
        'type': XRefRole(),
        'union': XRefRole(),
        'value': XRefRole(),
        'variable': XRefRole(),
        'word': XRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
    }

    def clear_doc(self, docname):
        for (typ, name), doc in list(self.data['objects'].items()):
            if doc == docname:
                del self.data['objects'][typ, name]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        objects = self.data['objects']
        objtypes = self.objtypes_for_role(typ)
        for objtype in objtypes:
            if (objtype, target) in objects:
                return make_refnode(builder, fromdocname,
                                    objects[objtype, target],
                                    objtype + '-' + target,
                                    contnode, target + ' ' + objtype)

    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        objects = self.data['objects']
        results = []
        for objtype in self.object_types:
            if (objtype, target) in self.data['objects']:
                results.append(('dash:' + self.role_for_objtype(objtype),
                                make_refnode(builder, fromdocname,
                                             objects[objtype, target],
                                             objtype + '-' + target,
                                             contnode, target + ' ' + objtype)))
        return results

    def get_objects(self):
        for (typ, name), docname in iteritems(self.data['objects']):
            yield name, name, typ, docname, typ + '-' + name, 1


def setup(app):
    app.add_domain(DashDomain)
