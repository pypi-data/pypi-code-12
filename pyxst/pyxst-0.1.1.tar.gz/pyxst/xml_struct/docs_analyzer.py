# -*- coding: utf-8 -*-

from traceback import format_exc
import os, sys
from os import path as osp
from lxml import etree
from .utils import DTD, XML_SCHEMA, split_qname


class XMLDocsGraphAnalyzer(object):
    def __init__(self, graph):
        self.title = graph.name
        self.graph = graph
        self.validation_method = u""
        self.validator=None
        if graph.source != u"" and graph.source is not None:
            self.validation_method = \
                        u"{0} {1}".format(graph.source_type, graph.source)
            filename = osp.abspath(graph.source)
            if graph.source_type == DTD:
                self.validator = etree.DTD(filename)
            elif graph.source_type == XML_SCHEMA:
                schema_tree = etree.parse(filename)
                self.validator = etree.XMLSchema(schema_tree)
            else:
                self.validation_method = u""
        self.val_results = {} # {filename: validation_result}
        self.graph.reset_uses()

    def analyze_xml_library(self, base_dir, suffixes=(u".xml",)):
        for path, sub_dirs, files in os.walk(base_dir):
            for filename in  [fn for fn in files
                              if osp.splitext(fn)[1] in suffixes]:
                filepath = osp.join(path, filename)
                self.analyze_xml_doc(base_dir, osp.relpath(filepath, base_dir))

    def analyze_xml_doc(self, base_dir, filename):
        if filename in self.val_results:
            return
        sys.stdout.write(u"analyzing {0}\n".format(filename))
        xml_tree = etree.parse(osp.join(base_dir, filename))
        if self.validator is not None:
            self.val_results[filename] = self.validator.validate(xml_tree)
        else:
            self.val_results[filename] = None
        if self.val_results[filename] is False:
            sys.stderr.write(
                u"### ERROR: {0} XML document is not valid against {1}\n===>"
                u" Skipping it\n".format(filename, self.validation_method))
            return
        self.visit_elt(xml_tree.getroot(), filename)

    def visit_elt(self, elt, filename, curr_gr_parent=None):
        elt_qname = self._get_elt_name(elt.tag)
        if curr_gr_parent is None:
            gr_elts = self.graph.find_high_level_elts(elt_qname)
        else:
            gr_elts = curr_gr_parent.find_children(elt_qname)
        if len(gr_elts) == 0:
            sys.stderr.write(
                u"### ERROR while analyzing {0}\nCan't find the graph "
                u"element corresponding to <{1}> inside the graph structure "
                u"describing the XML documents\n".format(filename, elt.tag))
            return
        elif len(gr_elts) > 1:
            sys.stderr.write(
                u"### WARNING while analyzing {0}\nFound more than one "
                u"graph element corresponding to <{1}> inside the graph "
                u"structure describing the XML documents\n===> Choosing the "
                u"first one\n".format(filename, elt.tag))
        gr_elt = gr_elts[0]
        gr_elt.actual_uses.setdefault(filename, 0)
        gr_elt.actual_uses[filename] += 1
        if curr_gr_parent is None:
            self.graph.root_uses[gr_elt].setdefault(filename, 0)
            self.graph.root_uses[gr_elt][filename] += 1
        else:
            curr_gr_parent.sub_elt_uses[gr_elt].setdefault(filename, 0)
            curr_gr_parent.sub_elt_uses[gr_elt][filename] += 1
        for attr_name in elt.attrib:
            attr_qname = self._get_attr_name(attr_name)
            gr_attrs = gr_elt.find_attributes(attr_qname)
            if len(gr_attrs) == 0:
                sys.stderr.write(
                    u"### ERROR while analyzing {0}\nCan't find the graph "
                    u"attribute corresponding to @{1} inside the graph "
                    u"structure describing the XML documents"
                    u"\n".format(filename, att_name))
                continue
            elif len(gr_attrs) > 1:
                sys.stderr.write(
                    u"### ERROR while analyzing {0}\nFound more than one "
                    u"graph attribute corresponding to @{1} inside the "
                    u"graph structure describing the XML documents\n===> "
                    u"Choosing the first one\n".format(filename, att_name))
            gr_attr = gr_attrs[0]
            gr_elt.attr_uses[gr_attr].setdefault(filename, 0)
            gr_elt.attr_uses[gr_attr][filename] += 1
        for child_elt in elt:
            if child_elt.tag is etree.Comment or child_elt.tag is etree.PI:
                continue
            self.visit_elt(child_elt, filename, curr_gr_parent=gr_elt)

    def _get_elt_name(self, elt_name):
        if self.graph.source_type == DTD and self.graph.dtd_qualif_local_elt:
            namespace, local_name = split_qname(elt_name)
            if namespace is None or namespace == u"":
                namespace = self.graph.dtd_ns_mapping.get(u"")
                if namespace is None:
                    return local_name
                else:
                    return u"{{{0}}}{1}".format(namespace, local_name)
        return elt_name

    def _get_attr_name(self, attr_name):
        if self.graph.source_type == DTD and self.graph.dtd_qualif_local_attr:
            namespace, local_name = split_qname(attr_name)
            if namespace is None or namespace == u"":
                namespace = self.graph.dtd_ns_mapping.get(u"")
                if namespace is None:
                    return local_name
                else:
                    return u"{{{0}}}{1}".format(namespace, local_name)
        return attr_name
