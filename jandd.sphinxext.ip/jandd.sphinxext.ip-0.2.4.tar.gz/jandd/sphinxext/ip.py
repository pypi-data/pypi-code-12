# -*- coding: utf-8 -*-
"""
    jandd.sphinxext.ip
    ~~~~~~~~~~~~~~~~~~

    The IP domain.

    :copyright: Copyright (c) 2016 Jan Dittberner
    :license: GPLv3+, see COPYING file for details.
"""

import re

from ipcalc import Network

from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.environment import NoUri
from sphinx.locale import l_
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

__version__ = '0.2.4'


def ip_object_anchor(typ, path):
    path = re.sub(r'[.:/]', '-', path)
    return typ.lower() + '-' + path


class ip_node(nodes.Inline, nodes.TextElement):
    pass


class ip_range(nodes.General, nodes.Element):
    pass


class IPXRefRole(XRefRole):
    """
    Cross referencing role for the IP domain.
    """
    def __init__(self, method, index_type, **kwargs):
        self.method = method
        self.index_type = index_type
        innernodeclass = None
        if method in ('v4', 'v6'):
            innernodeclass = ip_node
        super(IPXRefRole, self).__init__(
            innernodeclass=innernodeclass, **kwargs)

    def __call__(self, typ, rawtext, text, lineno, inliner,
                 options={}, content=[]):
        try:
            Network(text)
        except ValueError as e:
            env = inliner.document.settings.env
            env.warn(env.docname, "invalid ip address/range %s" % text, lineno)
            return [nodes.literal(text, text), []]
        return super(IPXRefRole, self).__call__(
            typ, rawtext, text, lineno, inliner, options, content)

    def process_link(self, env, refnode, has_explicit_title, title, target):
        domaindata = env.domaindata['ip']
        domaindata[self.method][target] = (target, refnode)
        return title, target

    def result_nodes(self, document, env, node, is_ref):
        try:
            node['typ'] = self.method
            indexnode = addnodes.index()
            targetid = 'index-%s' % env.new_serialno('index')
            targetnode = nodes.target('', '', ids=[targetid])
            doctitle = document.traverse(nodes.title)[0].astext()
            idxtext = "%s; %s" % (node.astext(), doctitle)
            idxtext2 = "%s; %s" % (self.index_type, node.astext())
            indexnode['entries'] = [
                ('single', idxtext, targetid, '', None),
                ('single', idxtext2, targetid, '', None),
            ]
            return [indexnode, targetnode, node], []
        except KeyError as e:
            return [node], [e.args[0]]


class IPRange(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def handle_rangespec(self, node):
        titlenode = nodes.title()
        node.append(titlenode)
        titlenode.append(nodes.inline('', self.get_prefix_title()))
        titlenode.append(nodes.literal('', self.rangespec))
        ids = ip_object_anchor(self.typ, self.rangespec)
        node['ids'].append(ids)
        self.env.domaindata[self.domain][self.typ][ids] = (
            self.env.docname,
            self.options.get('synopsis', ''))
        return ids

    def run(self):
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        self.rangespec = self.arguments[0]
        node = nodes.section()
        name = self.handle_rangespec(node)
        if self.env.docname in self.env.titles:
            doctitle = self.env.titles[self.env.docname]
        else:
            doctitle = self.state.document.traverse(nodes.title)[0].astext()
        idx_text = "%s; %s" % (self.rangespec, doctitle)
        self.indexnode = addnodes.index(entries=[
            ('single', idx_text, name, '', None),
            ('single', self.get_index_text(), name, '', None)
        ])

        if self.content:
            contentnode = nodes.paragraph('')
            node.append(contentnode)
            self.state.nested_parse(
                self.content, self.content_offset, contentnode)

        iprange = ip_range()
        node.append(iprange)
        iprange['rangespec'] = self.rangespec
        return [self.indexnode, node]


class IPv4Range(IPRange):
    typ = 'v4range'

    def get_prefix_title(self):
        return l_('IPv4 address range ')

    def get_index_text(self):
        return "%s; %s" % (l_('IPv4 range'), self.rangespec)


class IPv6Range(IPRange):
    typ = 'v6range'

    def get_prefix_title(self):
        return l_('IPv6 address range ')

    def get_index_text(self):
        return "%s; %s" % (l_('IPv6 range'), self.rangespec)


class IPDomain(Domain):
    """
    IP address and range domain.
    """
    name = 'ip'
    label = 'IP addresses and ranges.'

    object_types = {
        'v4':      ObjType(l_('v4'), 'v4', 'obj'),
        'v6':      ObjType(l_('v6'), 'v6', 'obj'),
        'v4range': ObjType(l_('v4range'), 'v4range', 'obj'),
        'v6range': ObjType(l_('v6range'), 'v6range', 'obj'),
    }

    directives = {
        'v4range': IPv4Range,
        'v6range': IPv6Range,
    }

    roles = {
        'v4':      IPXRefRole('v4', l_('IPv4 address')),
        'v6':      IPXRefRole('v6', l_('IPv6 address')),
        'v4range': IPXRefRole('v4range', l_('IPv4 range')),
        'v6range': IPXRefRole('v6range', l_('IPv6 range')),
    }

    initial_data = {
        'v4': {},
        'v6': {},
        'v4range': {},
        'v6range': {},
        'ips': [],
    }

    def clear_doc(self, docname):
        to_remove = []
        for key, value in self.data['v4range'].items():
            if docname == value[0]:
                to_remove.append(key)
        for key in to_remove:
            del self.data['v4range'][key]

        to_remove = []
        for key, value in self.data['v6range'].items():
            if docname == value[0]:
                to_remove.append(key)
        for key in to_remove:
            del self.data['v6range'][key]
        self.data['ips'] = [
            item for item in self.data['ips'] if item['docname'] != docname
        ]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        key = ip_object_anchor(typ, target)
        try:
            info = self.data[typ][key]
        except KeyError:
            text = contnode.rawsource
            role = self.roles.get(typ)
            if role is None:
                return None
            resnode = role.result_nodes(env.get_doctree(fromdocname),
                                        env, node, True)[0][2]
            if isinstance(resnode, addnodes.pending_xref):
                text = node[0][0]
                reporter = env.get_doctree(fromdocname).reporter
                reporter.warning('Cannot resolve reference to %r' % text,
                                 line=node.line)
                return node.children
            return resnode
        else:
            title = typ.upper() + ' ' + target
            return make_refnode(builder, fromdocname, info[0], key,
                                contnode, title)

    @property
    def items(self):
        return dict((key, self.data[key]) for key in self.object_types)

    def get_objects(self):
        for typ, items in self.items.items():
            for path, info in items.items():
                anchor = ip_object_anchor(typ, path)
                yield (path, path, typ, info[0], anchor, 1)


def process_ips(app, doctree):
    env = app.builder.env
    domaindata = env.domaindata[IPDomain.name]

    for node in doctree.traverse(ip_node):
        ip = node.astext()
        domaindata['ips'].append({
            'docname': env.docname,
            'source': node.parent.source or env.doc2path(env.docname),
            'lineno': node.parent.line,
            'ip': ip,
            'typ': node.parent['typ'],
        })
        replacement = nodes.literal(ip, ip)
        node.replace_self(replacement)


def sort_ip(item):
    return Network(item).ip


def create_table_row(rowdata):
    row = nodes.row()
    for cell in rowdata:
        entry = nodes.entry()
        row += entry
        entry += cell
    return row


def process_ip_nodes(app, doctree, fromdocname):
    env = app.builder.env
    domaindata = env.domaindata[IPDomain.name]

    header = (l_('IP address'), l_('Used by'))
    colwidths = (1, 3)

    for node in doctree.traverse(ip_range):
        content = []
        net = Network(node['rangespec'])
        ips = {}
        for key, value in [
            (ip_info['ip'], ip_info) for ip_info in
            domaindata['ips'] if ip_info['ip'] in net
        ]:
            addrlist = ips.get(key, [])
            addrlist.append(value)
            ips[key] = addrlist
        if ips:
            table = nodes.table()
            tgroup = nodes.tgroup(cols=len(header))
            table += tgroup
            for colwidth in colwidths:
                tgroup += nodes.colspec(colwidth=colwidth)
            thead = nodes.thead()
            tgroup += thead
            thead += create_table_row([
                nodes.paragraph(text=label) for label in header])
            tbody = nodes.tbody()
            tgroup += tbody
            for ip, ip_info in [
                (ip, ips[ip]) for ip in sorted(ips, key=sort_ip)
            ]:
                para = nodes.paragraph()
                para += nodes.literal('', ip)
                refnode = nodes.paragraph()
                refuris = set()
                refnodes = []
                for item in ip_info:
                    ids = ip_object_anchor(item['typ'], item['ip'])
                    if ids not in para['ids']:
                        para['ids'].append(ids)

                    domaindata[item['typ']][ids] = (fromdocname, '')
                    newnode = nodes.reference('', '', internal=True)
                    try:
                        newnode['refuri'] = app.builder.get_relative_uri(
                            fromdocname, item['docname'])
                        if newnode['refuri'] in refuris:
                            continue
                        refuris.add(newnode['refuri'])
                    except NoUri:
                        pass
                    title = env.titles[item['docname']]
                    innernode = nodes.Text(title.astext())
                    newnode.append(innernode)
                    refnodes.append(newnode)
                for count in range(len(refnodes)):
                    refnode.append(refnodes[count])
                    if count < len(refnodes) - 1:
                        refnode.append(nodes.Text(", "))
                tbody += create_table_row([para, refnode])
            content.append(table)
        else:
            para = nodes.paragraph(l_('No IP addresses in this range'))
            content.append(para)
        node.replace_self(content)


def setup(app):
    app.add_domain(IPDomain)
    app.connect('doctree-read', process_ips)
    app.connect('doctree-resolved', process_ip_nodes)
    return {'version': __version__}
