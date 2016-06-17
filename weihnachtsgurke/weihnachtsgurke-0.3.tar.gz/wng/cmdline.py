#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.

"""A search program for the PYCCLE-TCP corpus."""

from __future__ import print_function

# from wng import metadata
from wng import pattern, util

import click
import sys
import csv
import os
import multiprocessing
import functools
import glob

# TODO: code coverage

# TODO: ideas
# - factor out search code into an api for programmatic use
# - parallelize (done in cli)
# - benchmark cpython vs pypy vs nuitka
# - for repeater + capture: wrap the whole match (word+tag) in a named group;
#   then extract the match for this group from the string and get the
#   words/tags from it (by splitting on \n and \t).  Benchmark this to see how
#   much speed it costs.  Perhaps only activate the slower strategy if the
#   query contains a repeater + capture? (and print warning to stderr)
# - web viewer/search tool


def search_one_file(patterns, file):
    results = []
    fname = os.path.basename(file).split(".")[0]
    with open(file) as f:
        sentences = f.read().split("\n\n")
        for sentence in sentences:
            # The sentence needs to have a final newline, in case the pattern
            # is supposed to match its last word.  TODO: test the bug that
            # originally triggered this.
            sentence += "\n"
            for name, pat_rx in patterns:
                m = pat_rx.search(sentence)
                if m:
                    gps = m.groupdict()
                    gps["file"] = fname
                    gps["sentence"] = util.pyccle_to_text(sentence)
                    gps["match"] = util.pyccle_to_text(m.group(0))
                    gps["rule"] = name
                    results.append(gps)
    return results


@click.command()
@click.option("--search-file", "-s", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.File("w"), default=sys.stdout)
@click.option("--parallel", "-p", type=int, default=1)
@click.argument("paths", nargs=-1, type=str)
def main(search_file, paths, output, parallel):
    """This program searches the PYCCLE corpus for a Part-of-Speech/text
    sequence.

    The argument SEARCH_FILE specifies the path to a search file; consult the
    program's documentation for the details of this format.  The remaining
    arguments are taken to be the path to corpus directories.  Files located
    in these directories with names ending in ".tag" will be searched.

    """
    if output is None:
        output = open("".join(os.path.splitext(search_file)[:-1]) + ".out", "w")
    with open(search_file) as sf:
        search_text = sf.read()
        pat = pattern.parse_groups(search_text)
        captures = pattern.get_all_captures(search_text)
    writer = csv.DictWriter(output,
                            fieldnames=["file", "rule"] + captures +
                            ["match", "sentence"])
    files = []
    for path in paths:
        if os.path.isdir(path):
            for f in glob.iglob(os.path.join(path, "*.tag")):
                files.append(f)
        else:
            files.append(path)
    writer.writeheader()
    if parallel > 1:
        mapfn = multiprocessing.Pool(parallel).imap_unordered
    else:
        mapfn = map
    for res in mapfn(functools.partial(search_one_file, pat), files):
        for row in res:
            if row is not None:
                writer.writerow(row)
    output.flush()


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    main()
