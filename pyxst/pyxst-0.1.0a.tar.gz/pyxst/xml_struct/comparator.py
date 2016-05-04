# -*- coding: utf-8 -*-

import operator
from .utils import (ABSENT, DIFFERENT, SAME,
                              TEXT_ONLY, MIXED, ANY, ELEMENTS_ONLY, UNKNOWN)
from .graph_nodes import XMLElement, Group


class GraphComparator(object):
    def __init__(self, graph1, graph2):
        self.title1 = graph1.name
        self.title2 = graph2.name
        self.graph1 = graph1
        self.graph2 = graph2
        self.elt_cmprs = []
        self.cmpt_index = {}

    def compare(self):
        self.elt_cmprs = []
        self.cmpr_index = {}
        self.pair_elements()
        self.sort()
        for elt_cmpr in self.elt_cmprs:
            elt_cmpr.compare()

    def pair_elements(self):
        avail_elts1 = set(self.graph1.elements)
        avail_elts2 = set(self.graph2.elements)
        for elt1 in list(avail_elts1):
            poss_elts2 = self.graph2.find_all_elts(elt1.qname)
            if len(poss_elts2) == 0:
                self.add_elt_comparison(elt1, None)
            elif len(poss_elts2) == 1:
                self.add_elt_comparison(elt1, poss_elts2[0])
                avail_elts2.remove(poss_elts2[0])
            else:
                # There are several elements in graph2 with the same qname
                # as elt1. Chooses the one that has the most parents in common
                # with elt1 (better choice methods could be imagined).
                parents1 = set([elt.qname for elt in elt1.parent_elts])
                scores = []
                for elt2 in poss_elts2:
                    parents2 = set([elt.qname for elt in elt2.parent_elts])
                    comm_parents = parents1.intersection(parents2)
                    score = ( float(len(comm_parents)) / len(parents1)
                              + float(len(comm_parents)) / len(parents2) )
                    scores.append( (score, elt2) )
                scores.sort(key=operator.itemgetter(0), reverse=True)
                chosen_elt2 = scores[0][1]
                self.add_elt_comparison(elt1, chosen_elt2)
                avail_elts2.remove(chosen_elt2)
            avail_elts1.remove(elt1)
        for elt2 in list(avail_elts2):
            self.add_elt_comparison(None, elt2)
            avail_elts2.remove(elt2)
        assert len(avail_elts1) + len(avail_elts2) == 0

    def add_elt_comparison(self, elt1, elt2):
        assert elt1 is None or elt1 not in self.cmpr_index, \
            u"First element {0} already in a comparison".format(elt1)
        assert elt2 is None or elt2 not in self.cmpr_index, \
            u"Second element {0} already in a comparison".format(elt2)
        elt_cmpr = ElementComparator(self, elt1, elt2)
        self.elt_cmprs.append(elt_cmpr)
        if elt1 is not None:
            self.cmpr_index[elt1] = elt_cmpr
        if elt2 is not None:
            self.cmpr_index[elt2] = elt_cmpr

    def find_elt_cmpr(self, elt):
        return self.cmpr_index[elt]

    def sort(self):
        self.elt_cmprs.sort(key=operator.attrgetter(u"qname"))

    def __len__(self):
        return len(self.elts_comparisons)

    def __iter__(self):
        return iter(self.elts_comparisons)


class ElementComparator(object):
    def __init__(self, graph_cmpr, elt1, elt2):
        assert elt1 is not None or elt2 is not None
        self.graph_cmpr = graph_cmpr
        self.elt1 = elt1
        self.elt2 = elt2
        # Attributes
        self.attrs1_equality = {} # {XMLAttribute: CompResult}
        self.attrs2_equality = {} # {XMLAttribute: CompResult}
        # Content type
        self.ctype1_equality = None # CompResult
        self.ctype2_equality = None # CompResult
        self.text1_equality = None # CompResult
        self.text2_equality = None # CompResult
        # Sub-content
        self.subcnt1_equality = None # CompResult
        self.subcnt2_equality = None # CompResult
        # Parents
        self.parents1_equality = {} # {XMLElement: CompResult}
        self.parents2_equality = {} # {XMLElement: CompResult}

    @property
    def qname(self):
        if self.elt1 is not None:
            return self.elt1.qname
        else:
            return self.elt2.qname

    def compare(self):
        self.compare_attributes()
        self.compare_content_type()
        self.compare_textual_content()
        self.compare_sub_content()
        self.compare_parents()

    def compare_attributes(self):
        if self.elt1 is None:
            for att_occ2 in self.elt2.attributes.values():
                self.attrs2_equality[att_occ2.target] = CompResult(ABSENT)
        elif self.elt2 is None:
            for att_occ1 in self.elt1.attributes.values():
                self.attrs1_equality[att_occ1.target] = CompResult(ABSENT)
        else:
            for att_occ1 in self.elt1.attributes.values():
                att_occ2 = self.elt2.attributes.get(att_occ1.qname)
                if att_occ2 is None:
                    self.attrs1_equality[att_occ1.target] = CompResult(ABSENT)
                elif att_occ1 == att_occ2:
                    self.attrs1_equality[att_occ1.target] = CompResult(SAME)
                    self.attrs2_equality[att_occ2.target] = CompResult(SAME)
                else:
                    self.attrs1_equality[att_occ1.target] = \
                                                        CompResult(DIFFERENT)
                    self.attrs2_equality[att_occ2.target] = \
                                                        CompResult(DIFFERENT)
            for att_occ2 in self.elt2.attributes.values():
                if att_occ2.target in self.attrs2_equality:
                    continue
                self.attrs2_equality[att_occ2.target] = CompResult(ABSENT)

    def compare_content_type(self):
        if self.elt1 is None:
            self.ctype2_equality = CompResult(ABSENT)
        elif self.elt2 is None:
            self.ctype1_equality = CompResult(ABSENT)
        else:
            if ( self.elt1.content_type == self.elt2.content_type and
                 self.elt1.content_type != UNKNOWN):
                self.ctype1_equality = CompResult(SAME)
                self.ctype2_equality = CompResult(SAME)
            elif (self.elt2.content_type
                  in COMPATIBLE_CTYPES.get(self.elt1.content_type, [])):
                self.ctype1_equality = CompResult(DIFFERENT)
                self.ctype2_equality = CompResult(DIFFERENT)
            elif (self.elt1.content_type
                  in COMPATIBLE_CTYPES.get(self.elt2.content_type, [])):
                self.ctype1_equality = CompResult(DIFFERENT)
                self.ctype2_equality = CompResult(DIFFERENT)
            else:
                self.ctype1_equality = CompResult(ABSENT)
                self.ctype2_equality = CompResult(ABSENT)

    def compare_textual_content(self):
        if self.elt1 is None:
            self.text2_equality = CompResult(ABSENT)
        elif self.elt2 is None:
            self.text1_equality = CompResult(ABSENT)
        else:
            if ( self.elt1.content_type in (TEXT_ONLY, MIXED, ANY)
                 and self.elt2.content_type in (TEXT_ONLY, MIXED, ANY)):
                if ( (self.elt1.textual_content_type
                      == self.elt2.textual_content_type) and
                     (self.elt1.textual_content_is_list
                      == self.elt2.textual_content_is_list) and
                     (self.elt1.textual_content_values
                      == self.elt2.textual_content_values) ):
                    self.text1_equality = CompResult(SAME)
                    self.text2_equality = CompResult(SAME)
                else:
                    self.text1_equality = CompResult(DIFFERENT)
                    self.text2_equality = CompResult(DIFFERENT)
            else:
                self.text1_equality = CompResult(ABSENT)
                self.text2_equality = CompResult(ABSENT)

    def compare_sub_content(self):
        if self.elt1 is not None and self.elt1.content is not None:
            self.subcnt1_equality = \
                            build_results_struct(self.elt1.content.target)
        else:
            self.subcnt1_equality = CompResult(ABSENT)
        if self.elt2 is not None and self.elt2.content is not None:
            self.subcnt2_equality = \
                            build_results_struct(self.elt2.content.target)
        else:
            self.subcnt2_equality = CompResult(ABSENT)
        if self.elt1 is None or self.elt2 is None:
            return
        if ( not self.elt1.content_type in (MIXED, ELEMENTS_ONLY)
             or not self.elt2.content_type in (MIXED, ELEMENTS_ONLY) ):
            return
        self._compare_groups(self.elt1.content, self.elt2.content,
                             self.subcnt1_equality, self.subcnt2_equality)

    def _compare_groups(self, occur1, occur2, result1, result2,
                        differents=False):
        node1 = occur1.target
        node2 = occur2.target
        if occur1 == occur2:
            if not differents:
                result1.result = SAME
                result2.result = SAME
            else:
                result1.result = DIFFERENT
                result2.result = DIFFERENT
        elif node1.__class__ == node2.__class__:
            result1.result = DIFFERENT
            result2.result = DIFFERENT
        elif len(node1) == 1 or len(node2) == 1:
            if ( occur1.minimum == occur2.minimum
                 and occur1.maximum == occur2.maximum
                 and not differents):
                result1.result = SAME
                result2.result = SAME
            else:
                result1.result = DIFFERENT
                result2.result = DIFFERENT
        else:
            differents = True
        not_found1 = dict([(sub_occur, result1.sub_results[idx])
                           for (idx, sub_occur) in enumerate(node1)])
        not_found2 = dict([(sub_occur, result2.sub_results[idx])
                           for (idx, sub_occur) in enumerate(node2)])
        sub_not_found1 = {}
        sub_not_found2 = {}
        idx2 = -1
        for sub_occur1 in node1:
            sub_node1 = sub_occur1.target
            sub_node2_match, sub_nodes_compare = \
                                self._build_match_compare_functions(sub_node1)
            for tmp_idx in range(idx2+1, len(node2)):
                if sub_node2_match(node2[tmp_idx].target):
                    idx2 = tmp_idx
                    sub_result1 = not_found1.pop(sub_occur1)
                    sub_result2 = not_found2.pop(node2[tmp_idx])
                    nfnd1, nfnd2 = sub_nodes_compare(
                        sub_occur1, node2[tmp_idx],
                        sub_result1, sub_result2, differents)
                    sub_not_found1.update(nfnd1)
                    sub_not_found2.update(nfnd2)
                    break
            else:
                # Search corresponding element before current index (idx2)
                for tmp_idx in range(0, idx2):
                    if ( sub_node2_match(node2[tmp_idx].target)
                         and node2[tmp_idx] in not_found2):
                        sub_result1 = not_found1.pop(sub_occur1)
                        sub_result2 = not_found2.pop(node2[tmp_idx])
                        nfnd1, nfnd2 = sub_nodes_compare(
                            sub_occur1, node2[tmp_idx],
                            sub_result1, sub_result2, differents)
                        if isinstance(node1, Sequence):
                            # Order matters and we found elt2 before current
                            # index (idx2) so the result can't be "SAME"
                            sub_result1.result = DIFFERENT
                            sub_result2.result = DIFFERENT
                        sub_not_found1.update(nfnd1)
                        sub_not_found2.update(nfnd2)
                        break
        # Collect the elements not found in the sub-groups that didn't match
        # anything (sub-elt1 and sub-elt2)
        for sub_occur1, sub_result1 in not_found1.items():
            if isinstance(sub_occur1.target, Group):
                sub_not_found1.update(
                    self._collect_all_not_found(sub_occur1, sub_result1))
        for sub_occur2, sub_result2 in not_found2.items():
            if isinstance(sub_occur2.target, Group):
                sub_not_found2.update(
                    self._collect_all_not_found(sub_occur2, sub_result2))
        # Try to match the not found elements (elt1) with the elements not
        # found in the sub-groups (sub-elt2)
        for sub_occur1 in not_found1.keys():
            sub_node1 = sub_occur1.target
            if isinstance(sub_node1, Group):
                continue
            sub_node2_match, sub_nodes_compare = \
                                self._build_match_compare_functions(sub_node1)
            for sub_occur2 in sub_not_found2.keys():
                if sub_node2_match(sub_occur2.target):
                    sub_result1 = not_found1.pop(sub_occur1)
                    sub_result2 = sub_not_found2.pop(sub_occur2)
                    _, _ = sub_nodes_compare(sub_occur1, sub_occur2,
                                             sub_result1, sub_result2, True)
                    break
        # Try to match the elements not found in the sub-groups (sub-elt1) with
        # the not found elements (elt2)
        for sub_occur1 in sub_not_found1.keys():
            sub_node1 = sub_occur1.target
            if isinstance(sub_node1, Group):
                continue
            sub_node2_match, sub_nodes_compare = \
                                self._build_match_compare_functions(sub_node1)
            for sub_occur2 in not_found2.keys():
                if sub_node2_match(sub_occur2.target):
                    sub_result1 = sub_not_found1.pop(sub_occur1)
                    sub_result2 = not_found2.pop(sub_occur2)
                    _, _ = sub_nodes_compare(sub_occur1, sub_occur2,
                                             sub_result1, sub_result2, True)
                    break
        # Add the elements not found in the sub-groups to the elements not
        # found in this group; return them
        not_found1.update(sub_not_found1)
        not_found2.update(sub_not_found2)
        return not_found1, not_found2

    def _compare_elts(self, occur1, occur2, result1, result2, differents=False):
        if occur1 == occur2 and not differents:
            result1.result = SAME
            result2.result = SAME
        else:
            result1.result = DIFFERENT
            result2.result = DIFFERENT
        return [], []

    def _build_match_compare_functions(self, sub_node1, groups=True):
        if isinstance(sub_node1, XMLElement):
            assoc_elt2 = self.graph_cmpr.find_elt_cmpr(sub_node1).elt2
            def sub_node2_match(sub_node2):
                return  sub_node2 == assoc_elt2
            sub_nodes_compare = self._compare_elts
        elif groups and isinstance(sub_node1, Group):
            class2 = sub_node1.__class__
            def sub_node2_match(sub_node2):
                return isinstance(sub_node2, class2)
            sub_nodes_compare = self._compare_groups
        else:
            def sub_node2_match(subnode_idx):
                return False
            def sub_nodes_compare(s, o1, o2, r1, r2):
                return None
        return sub_node2_match, sub_nodes_compare

    def _collect_all_not_found(self, occur, result):
        gr_node = occur.target
        if not isinstance(gr_node, Group):
            return {}
        not_found = {}
        for idx, sub_occur in enumerate(gr_node):
            not_found[sub_occur] = result.sub_results[idx]
            if isinstance(sub_occur.target, Group):
                not_found.update(
                    self._collect_all_not_found(sub_occur,
                                                result.sub_results[idx]))
        return not_found

    def compare_parents(self):
        if self.elt1 is None:
            for parent2 in self.elt2.parent_elts:
                self.parents2_equality[parent2] = CompResult(ABSENT)
        elif self.elt2 is None:
            for parent1 in self.elt1.parent_elts:
                self.parents1_equality[parent1] = CompResult(ABSENT)
        else:
            for parent1 in self.elt1.parent_elts:
                poss_par2 = self.elt2.find_parents(parent1.qname)
                if len(poss_par2) == 0:
                    self.parents1_equality[parent1] = CompResult(ABSENT)
                else:
                    assoc_par2 = self.graph_cmpr.find_elt_cmpr(parent1).elt2
                    if assoc_par2 in poss_par2:
                        self.parents1_equality[parent1] = CompResult(SAME)
                        self.parents2_equality[assoc_par2] = CompResult(SAME)
                    else:
                        self.parents1_equality[parent1] = CompResult(ABSENT)
            for parent2 in self.elt2.parent_elts:
                if parent2 in self.parents2_equality:
                    continue
                self.parents2_equality[parent2] = CompResult(ABSENT)


COMPATIBLE_CTYPES = {
    TEXT_ONLY: (MIXED, ANY),
    ELEMENTS_ONLY: (MIXED, ANY),
    MIXED: (TEXT_ONLY, ELEMENTS_ONLY, ANY),
    ANY: (TEXT_ONLY, ELEMENTS_ONLY, MIXED)
}


class CompResult(object):
    def __init__(self, result, is_group=False):
        assert result in (SAME, ABSENT, DIFFERENT)
        self.is_group = is_group
        self.result = result
        self.sub_results = []

    def __eq__(self, other):
        return self.result == other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return u"<Comparison: {0} {1}>".format(self.result, self.sub_results)

def build_results_struct(group):
    result = CompResult(ABSENT, True)
    for sub_occur in group:
        if isinstance(sub_occur.target, XMLElement):
            result.sub_results.append(CompResult(ABSENT))
        elif isinstance(sub_occur.target, Group):
            result.sub_results.append(build_results_struct(sub_occur.target))
    return result


