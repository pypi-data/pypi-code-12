#!/usr/bin/env python
# vim:fileencoding=utf-8
#Author: Shinya Suzuki
#Created: 2016-05-24

import unittest
import networkx as nx
import numpy as np
from metrics import *

class TestGraphGenerator(unittest.TestCase):
    def setUp(self):
        dag = nx.DiGraph()
        h1 = ["A"]
        h2 = ["B", "C", "D", "E"]
        h3 = ["F", "G"]
        h4 = ["H"]
        h5 = ["I", "J", "K"]
        dag.add_nodes_from(h1+h2+h3+h4+h5)
        dag.add_edges_from(list(product(h2, h1)) +
                           list(product(h4,["B"])) +
                           list(product(h3,["C"])) +
                           list(product(h5,["E"])))
        self.reference_graph = dag

    def test_matrix2multi_label(self):
        y_matrix = [[0,0,0,0,0,0,0,0,0,0,1],[0,0,0,0,0,1,0,0,0,0,1]]
        label_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        self.assertEqual(
                np.all(matrix2multi_label(y_matrix, label_list)),
                np.all(np.array([["K"],["F", "K"]])))

if __name__ =='__main__':
    unittest.main()
