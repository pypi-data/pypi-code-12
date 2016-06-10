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
        h6 = ["L"]
        dag.add_nodes_from(h1+h2+h3+h4+h5)
        dag.add_edges_from(list(product(h2, h1)) +
                           list(product(h4,["B"])) +
                           list(product(h3,["C"])) +
                           list(product(h5,["E"])) +
                           list(product(h6,["I"])) +
                           list(product(h6,["D"])))
        self.graph_generator = GraphGenerator(dag)
        self.graph_ex = GraphEx()
        self.label_list = h1+h2+h3+h4+h5+h6

    def test_matrix2multi_label(self):
        y_matrix_1 = [[0,0,0,0,0,0,0,0,0,0,1],[0,0,0,0,0,1,0,0,0,0,1]]
        y_matrix_2 = [[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,1]]
        y_matrix_3 = [[2,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,1]]
        y_matrix_4 = [[-2,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,1]]
        y_matrix_5 = [["a",0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,1]]
        label_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

        self.assertEqual(
                np.all(matrix2multi_label(y_matrix_1, label_list)),
                np.all(np.array([["K"],["F", "K"]])))
        self.assertEqual(
                np.all(matrix2multi_label(y_matrix_2, label_list)),
                np.all(np.array([[],["F", "K"]])))
        self.assertRaises(
                ValueError,
                matrix2multi_label,
                y_matrix_3, label_list)
        self.assertRaises(
                ValueError,
                matrix2multi_label,
                y_matrix_4, label_list)
        self.assertRaises(
                ValueError,
                matrix2multi_label,
                y_matrix_5, label_list)

    def test_calc_lca(self):
        self.assertEqual(self.graph_generator.calc_lca("A", "A", "A"),
                ("A", 0))
        self.assertEqual(self.graph_generator.calc_lca("A", "B", "A"),
                ("A", 1))
        self.assertEqual(self.graph_generator.calc_lca("F", "H", "A"),
                ("A", 4))
        self.assertEqual(self.graph_generator.calc_lca("I", "K", "A"),
                ("E", 2))
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_lca,
                "A", "D", "C")
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_lca,
                "A", "D", "D")
        self.assertRaises(
                nx.exception.NetworkXError,
                self.graph_generator.calc_lca,
                "A", "", "A")

    def test_calc_extended_lca(self):
        self.assertEqual(
                self.graph_generator.calc_extended_lca("G", ["H", "D"], "A"),
                set(["A"]))
        self.assertEqual(
                self.graph_generator.calc_extended_lca("G", ["B", "D"], "A"),
                set(["A"]))
        self.assertEqual(
                self.graph_generator.calc_extended_lca("L", ["J", "B"], "A"),
                set(["A", "E"]))
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_extended_lca,
                "G", ["C", "D"], "I")
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_extended_lca,
                "G", [], "A")

    def test_calc_lca_all(self):
        self.assertEqual(
                self.graph_generator.calc_lca_all(
                    ["L", "G", "K"],
                    ["C", "F"],
                    "A"),
                (set(["C", "A"]), {"C":set(["G"]), "A":set(["L", "K"])}))
        self.assertEqual(
                self.graph_generator.calc_lca_all(
                    ["C", "F"],
                    ["L", "G", "K"],
                    "A"),
                (set(["C"]), {"C":set(["C", "F"])}))
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_lca_all,
                ["H", "C"],
                ["A"],
                "C")
        self.assertRaises(
                ValueError,
                self.graph_generator.calc_lca_all,
                ["H", "C"],
                [],
                "A")
        self.assertEqual(
                self.graph_generator.calc_lca_all(
                    [],
                    ["A"],
                    "A"),
                (set([]), {}))

    def test_generate_redundant_graph(self):
        subgraph_1 = nx.DiGraph()
        subgraph_1.add_nodes_from(["H", "B", "F", "A", "C"])
        subgraph_1.add_edges_from(
                [("H", "B"), ("B", "A"), ("C", "A"), ("F", "C")])
        graph_ex_1 = GraphEx()
        graph_ex_1.set_graph_ex(subgraph_1)
        graph_ex_1.set_connection({"A":set(["H", "B", "F"])})
        graph_ex_1.set_lcas(set(["A"]))
        graph_ex_1_result = self.graph_generator.generate_redundant_graph(
                    ["H", "B", "F"],
                    ["I", "D"],
                    "A")

        self.assertEqual(type(graph_ex_1), type(graph_ex_1_result))
        self.assertEqual(
                graph_ex_1.__dict__.keys(), graph_ex_1.__dict__.keys())
        for key in graph_ex_1.__dict__.keys():
            if type(graph_ex_1.__getattribute__(key)) is not nx.DiGraph:
                self.assertEqual(
                        graph_ex_1.__getattribute__(key),
                        graph_ex_1_result.__getattribute__(key))
            else:
                self.assertEqual(
                        graph_ex_1.__getattribute__(key).__dict__.keys(),
                        graph_ex_1_result.__getattribute__(key).__dict__.keys(),
                        )
                for g_key in graph_ex_1.__getattribute__(key).__dict__.keys():
                    self.assertEqual(
                            graph_ex_1.__getattribute__(key).__getattribute__(g_key),
                            graph_ex_1_result.__getattribute__(key).__getattribute__(g_key),
                            )

    def test_fbeta_lca_score(self):
        y_true_matrix = [[0,0,0,0,0,0,0,1,1,0,0,0]]
        y_pred_matrix = [[0,0,0,0,0,0,0,1,0,1,0,0]]
        self.assertEqual(
            fbeta_lca_score(y_true_matrix,
                y_pred_matrix,
                self.graph_generator.reference_graph,
                "A",
                self.label_list),
            0.6666666666666666
        )

        y_true_matrix = [[0,0,0,0,0,0,0,1,1,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0]]
        y_pred_matrix = [[0,0,0,0,0,0,0,1,0,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0]]
        self.assertEqual(
            fbeta_lca_score(y_true_matrix,
                y_pred_matrix,
                self.graph_generator.reference_graph,
                "A",
                self.label_list),
            0.8333333333333333
        )

        y_true_matrix = [[0,0,0,0,0,0,0,1,1,0,0,0],
                [0,1,0,0,0,0,0,0,0,0,0,1]]
        y_pred_matrix = [[0,0,0,0,0,0,0,1,0,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0]]
        self.assertEqual(
            fbeta_lca_score(y_true_matrix,
                y_pred_matrix,
                self.graph_generator.reference_graph,
                "A",
                self.label_list),
            0.53333333333333333
        )

        y_true_matrix = [[1,0,0,0,0,0,0,0,0,0,0,0]]
        y_pred_matrix = [[0,0,0,0,0,1,1,1,0,1,1,1]]
        self.assertEqual(
            fbeta_lca_score(y_true_matrix,
                y_pred_matrix,
                self.graph_generator.reference_graph,
                "A",
                self.label_list),
            0.16666666666666669
        )

        self.assertEqual(
            fbeta_lca_score(y_true_matrix,
                y_pred_matrix,
                self.graph_generator.reference_graph,
                "A",
                self.label_list,
                1,
                True),
            0.090909090909090939
        )

        y_true_matrix = [
                [1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0]]
        y_pred_matrix = [
                [0,0,0,0,0,1,1,1,0,1,1,1],
                [0,0,0,0,0,0,1,0,0,0,0,0],]
        self.assertEqual(
                fbeta_lca_score(y_true_matrix,
                    y_pred_matrix,
                    self.graph_generator.reference_graph,
                    "A",
                    self.label_list,
                    dummy_depth=1),
                0.283333333333333333
                )

        y_true_matrix = [[1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,1,1,1,0,1,1,1]]
        y_pred_matrix = [[0,0,0,0,0,1,1,1,0,1,1,1]]
        self.assertRaises(
            ValueError,
            fbeta_lca_score,
            y_true_matrix,
            y_pred_matrix,
            self.graph_generator.reference_graph,
            "A",
            self.label_list)

if __name__ =='__main__':
    unittest.main()


if __name__ =='__main__':
    unittest.main()
