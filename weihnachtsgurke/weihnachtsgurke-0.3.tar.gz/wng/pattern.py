# -*- coding: utf-8 -*-

# Copyright 2015 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.

import re


def parse_term(s):
    if re.match("^#", s):
        # Comment line
        return ""
    m = re.match("^([^{} ]+)?(?:{([^ ]*)})?(?: ([*?+]))?(?: as ([a-zA-Z0-9]+))?$", s)
    if not m:
        raise Exception("Couldn't match term %s" % s)
    if m.group(1) is None and m.group(2) is None:
        # Empty matcher, return nothing
        return ""
    if m.group(4) is not None:
        if m.group(3) in ("*", "+"):
            word = "(?:%s)" % m.group(2) or ".*"
            tag = "(?:%s)" % m.group(1) or ".*"
            capture = "P<%s_all>" % m.group(4)
        else:
            word = "(?P<%s_word>%s)" % (m.group(4), m.group(2) or ".*")
            tag = "(?P<%s_tag>%s)" % (m.group(4), m.group(1) or ".*")
            capture = ":"
    else:
        word = "(?:%s)" % (m.group(2) or ".*")
        tag = "(?:%s)" % (m.group(1) or ".*")
        capture = ":"
    return "(?%s(?:%s)\t(?:%s)\n)%s" % (capture, word, tag, m.group(3) or "")


def parse_name_and_terms(s):
    name_match = re.match("^[\n]*([a-zA-Z0-9]+):\n", s)
    if name_match is None:
        name = None
        terms = s
    else:
        name = name_match.group(1)
        terms = s[name_match.end(0):]
    # TODO: Test the bug that triggered this: the first term in a pattern
    # could match only a siffix of the word.
    rx = re.compile("(^|\n)" + "".join(map(parse_term, terms.split("\n"))))
    return (name, rx)


def parse_groups(s):
    s = "\n".join(map(lambda s: s.strip(), s.split("\n")))
    terms = s.split("\n==\n")
    if terms[-1].strip() == "":
        terms = terms[:-1]
    if terms[0].strip() == "":
        terms = terms[0:]
    names_and_terms = list(map(parse_name_and_terms, terms))
    if any(map(lambda x: x[0] is None, names_and_terms)):
        if len(names_and_terms) == 1:
            names_and_terms = (("default", names_and_terms[0][1]),)
        else:
            raise Exception("Missing name for some pattern(s)")
    return names_and_terms


def process_capture(capture):
    if capture[0] in ("*", "+"):
        return (capture[1] + "_all",)
    else:
        return (capture[1] + "_tag", capture[1] + "_word")


def get_all_captures(s):
    captures = re.findall("(?: ([*+]))? as ([a-zA-Z0-9]+)$", s, re.MULTILINE)
    captures_aug = map(process_capture, captures)
    return sorted([x for tuple in captures_aug for x in tuple])
