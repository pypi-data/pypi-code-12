#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2016 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Herve BREDIN - http://herve.niderb.fr


import networkx as nx
from pyannote.core.util import pairwise


class Scene(object):
    """Segmentation into scenes"""

    def __init__(self):
        super(Scene, self).__init__()

    def __call__(self, video, threads=None):

        if threads is None:
            raise NotImplementedError('threads must be precomputed.')

        g = nx.Graph()

        # connect adjacent shots
        for shot1, shot2 in pairwise(threads.itertracks()):
            g.add_edge(shot1, shot2)

        # connect threaded shots
        for label in threads.labels():
            for shot1, shot2 in pairwise(threads.subset([label]).itertracks()):
                g.add_edge(shot1, shot2)

        scenes = threads.copy()

        # group all shots of intertwined threads
        for shots in sorted(sorted(bc) for bc in nx.biconnected_components(g)):

            if len(shots) < 3:
                continue

            common_label = scenes[shots[0]]
            for shot in shots:
                scenes[shot] = common_label

        return scenes

# def find_cut_edge(graph):
#
#     edges = nx.minimum_edge_cut(graph)
#     if len(edges) != 1:
#         return
#
#     cut_edge = edges.pop()
#     yield cut_edge
#
#     # remove cut edge and process resulting (2) subgraphs
#     graph.remove_edge(*cut_edge)
#     for subgraph in nx.connected_component_subgraphs(graph):
#         for cut_edge in find_cut_edge(subgraph):
#             yield cut_edge
