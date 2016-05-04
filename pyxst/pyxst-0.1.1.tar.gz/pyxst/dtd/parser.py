# -*- coding: utf-8 -*-
"""
Module containing the parser function that can read a DTD file and
return a :class:`~dtd.root.DtdDefinition` object.

.. autofunction:: parse_dtd
"""

from traceback import format_exc
from os import path as osp

from lxml import etree

from ..xsd.utils import split_qname
from .errors import DtdError
from .root import DtdDefinition
from .nodes import DtdElement, DtdAttribute
from .groups import DtdSequence, DtdChoice
from .utils import resolve_xml_qname, DtdUsage
from . import constants


IMPLIED = u"IMPLIED"
FIXED = u"FIXED"
EMPTY = u"EMPTY"
ANY = u"ANY"
MIXED = u"MIXED"
ELEMENT = u"ELEMENT"
PCDATA = u"PCDATA"
OPTIONAL = u"OPT"
MULTIPLE = u"MULT"
PLUS = u"PLUS"
CHOICE = u"OR"
SEQUENCE = u"SEQ"

CONTENT_TYPE_MAPPING = {
    EMPTY : constants.EMPTY,
    ANY: constants.ANY,
    MIXED: constants.MIXED,
    ELEMENT: constants.ELEMENTS_ONLY
}

GROUP_MAPPING = {
    CHOICE: DtdChoice,
    SEQUENCE: DtdSequence,
}


class DtdParser(object):
    def __init__(self, ns_mapping=None):
        if ns_mapping is None:
            self.ns_mapping = {}
        else:
            self.ns_mapping = ns_mapping
        self.qualif_local_elt = True
        self.qualif_local_att = False
        self.dtd_def = None

    def parse_dtd(self, dtd_file, qualify_local_elements=False,
                  qualify_local_attributes=False):
        self.qualif_local_elt = qualify_local_elements
        self.qualif_local_att = qualify_local_attributes
        # Opens the XML Schema file
        try:
            dtd_file = osp.abspath(dtd_file)
        except Exception:
            pass
        try:
            dtd_decl = etree.DTD(dtd_file)
        except etree.DTDParseError, exc:
            raise DtdError("Found a syntax error while reading the %s DTD "
                           "file\n%s" % (dtd_file, format_exc()))
        self.dtd_def = DtdDefinition()
        for elt_decl in dtd_decl.iterelements():
            elt_obj = self.build_element(elt_decl)
            self.dtd_def.add_element(elt_obj)
        for elt_decl in dtd_decl.iterelements():
            self.fill_element(elt_decl)

    def build_element(self, elt_decl, uid_prefix=u""):
        elt_name = self.build_name(elt_decl, self.qualif_local_elt)
        elt_obj = DtdElement(elt_name, uid_prefix=uid_prefix)
        # Attributes
        for att_decl in elt_decl.iterattributes():
            att_obj = self.build_attribute(att_decl, uid_prefix=elt_obj.uid)
            min_occur = 1
            if att_decl.default.upper() == IMPLIED:
                min_occur = 0
            elt_obj.add_attribute(att_obj, min_occur, 1)
        return elt_obj

    def build_attribute(self, att_decl, uid_prefix):
        att_name = self.build_name(att_decl, self.qualif_local_att)
        att_obj = DtdAttribute(att_name, uid_prefix=uid_prefix)
        att_obj.dtd_type = att_decl.type.upper()
        att_obj.fixed_value = (att_decl.default.upper() == FIXED)
        if att_decl.default_value is not None:
            att_obj.default_value = att_decl.default_value
        poss_vals = [unicode(val) for val in att_decl.values()]
        if len(poss_vals) > 0:
            att_obj.dtd_type = u"CDATA"
            att_obj.possible_values = poss_vals
        return att_obj

    def fill_element(self, elt_decl, uid_prefix=u""):
        elt_name = self.build_name(elt_decl, self.qualif_local_elt)
        elt_obj = self.dtd_def.elements.get(
            u"{0}/{1}".format(uid_prefix, elt_name))
        if elt_obj is None:
            raise DtdError(u"{0} should have been already built"
                           u"".format(elt_name))
        # Sub-content
        elt_obj.content_type = CONTENT_TYPE_MAPPING.get(elt_decl.type.upper())
        if elt_decl.content is not None:
            elt_obj.sub_content = self.build_group(elt_decl.content,
                                                   uid_prefix=elt_obj.uid)
        if ( elt_obj.content_type == constants.MIXED
             and elt_obj.sub_content is None):
            elt_obj.content_type = constants.TEXT_ONLY

    def build_group(self, content_decl, uid_prefix=u"", parent_grp=None,
                    sub_grp_counts=None):
        if content_decl.type.upper() == PCDATA:
            return
        min_occur = 1
        if content_decl.occur.upper() in (OPTIONAL, MULTIPLE):
            min_occur = 0
        max_occur = 1
        if content_decl.occur.upper() in (MULTIPLE, PLUS):
            max_occur = constants.INFINITY
        if content_decl.type.upper() == ELEMENT:
            ns_map = self.ns_mapping.copy()
            if not(self.qualif_local_elt):
                if None in ns_map:
                    ns_map.pop(None)
                if u"" in ns_map:
                    ns_map.pop(u"")
            elt_name = resolve_xml_qname(content_decl.name, ns_map)
            elt_obj = self.dtd_def.elements.get(u"/{0}".format(elt_name))
            if elt_obj is None:
                raise DtdError(
                    u"In {0}, the content refers to {1} element that can't be "
                    u"found".format(uid_prefix, elt_name))
            if parent_grp is None:
                # Happens when there is only one child element inside the
                # element
                grp = DtdSequence(u"sequence", uid_prefix=uid_prefix)
                grp.add_item(elt_obj, min_occur, max_occur)
                return DtdUsage(grp, 1, 1)
            else:
                parent_grp.add_item(elt_obj, min_occur, max_occur)
        elif content_decl.type.upper() in (CHOICE, SEQUENCE):
            cnt_type = content_decl.type.upper()
            cnt_class = GROUP_MAPPING[cnt_type]
            if parent_grp is None:
                grp = cnt_class(u"{0}0".format(cnt_type.lower()),
                                uid_prefix=uid_prefix)
                cnts = {CHOICE: 0, SEQUENCE: 0}
                self.build_group(content_decl.left, uid_prefix=uid_prefix,
                                 parent_grp=grp, sub_grp_counts=cnts)
                self.build_group(content_decl.right, uid_prefix=uid_prefix,
                                 parent_grp=grp, sub_grp_counts=cnts)
                return DtdUsage(grp, min_occur, max_occur)
            elif (isinstance(parent_grp, cnt_class) and min_occur == 1
                  and max_occur == 1):
                # Adds the group content directly inside the parent group
                # cf. tree structure of the content in lxml.DTD
                self.build_group(
                    content_decl.left, uid_prefix=uid_prefix,
                    parent_grp=parent_grp, sub_grp_counts=sub_grp_counts)
                self.build_group(
                    content_decl.right, uid_prefix=uid_prefix,
                    parent_grp=parent_grp, sub_grp_counts=sub_grp_counts)
            else:
                # Builds a new group and inserts it in the parent group
                grp = cnt_class(
                    u"{0}{1}".format(cnt_type.lower(),sub_grp_counts[cnt_type]),
                                uid_prefix=parent_grp.uid)
                sub_grp_counts[cnt_type] += 1
                cnts = {CHOICE: 0, SEQUENCE: 0}
                self.build_group(
                    content_decl.left, uid_prefix=uid_prefix,
                    parent_grp=grp, sub_grp_counts=cnts)
                self.build_group(
                    content_decl.right, uid_prefix=uid_prefix,
                    parent_grp=grp, sub_grp_counts=cnts)
                parent_grp.add_item(grp, min_occur, max_occur)
        else:
            raise DtdError(u"Unexpected type of content in {0}: {1}"
                           u"".format(uid_prefix, content_decl.type))

    def build_name(self, decl, qualif_item):
        """
        Builds the name of an element of an attribute using the namespace
        mapping
        """
        if decl.prefix != u"" and decl.prefix is not None:
            namespace = self.ns_mapping.get(decl.prefix, u"")
        elif qualif_item:
            namespace = self.ns_mapping.get(u"", self.ns_mapping.get(None, u""))
        else:
            namespace = u""
        if namespace == u"":
            return unicode(decl.name)
        else:
            return u"{{{0}}}{1}".format(namespace, decl.name)
