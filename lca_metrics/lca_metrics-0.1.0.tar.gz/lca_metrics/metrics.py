#!/usr/bin/env python
# vim:fileencoding=utf-8
#Author: Shinya Suzuki
#Created: 2016-02-13
#Fixed: 2016-03-10

import networkx as nx
import numpy as np
from itertools import product

class GraphGenerator(object):

    """
    Class for calculation of subgraph
    """
    def __init__(self, reference_graph):
        self.reference_graph = reference_graph

    def calc_lca_all(self, ss, ts, r):
        """
            Return LCAall of ss against ts and connection_dict

            connection_dict is correspondence of ss and lca .
        """
        lca_all = set([])
        connection_dict={}

        for s in ss:
            lcas_set = self.calc_extended_lca(s, ts, r)
            for lca in lcas_set:
                if lca in connection_dict.keys():
                    connection_dict[lca].add(s)
                else:
                    connection_dict[lca] = set([s])
            lca_all = lca_all.union(lcas_set)
        return lca_all, connection_dict

    def calc_extended_lca(self, s, ts, r):
        """
            Return lowest cost LCA set .
        """
        if len(ts) == 0:
            raise ValueError("LCA is not definable for empty set")
        lcas_for_s = set([self.calc_lca(s, t, r) for t in ts])
        path_length_min = min(lcas_for_s, key=lambda x:x[1])[1]

        lcas_set = set([])
        for lca in lcas_for_s:
            if lca[1] == path_length_min:
                lcas_set.add(lca[0])
        return lcas_set

    def calc_lca(self, s, t, r):
        """
            Return lca for s and t, and sum length of s to lca and r to lca.

            To archive this, search co-ancestor of s and t .
            Next calculate depth of co-ancestor from root .
            LCA is the deepest node of co-ancestor.
            To minimize cost of this lca is also calculated .
        """
        s_ancestors = nx.descendants(self.reference_graph, s)
        s_ancestors.add(s)
        t_ancestors = nx.descendants(self.reference_graph, t)
        t_ancestors.add(t)
        if ( r not in t_ancestors ) or ( r not in s_ancestors ):
            raise ValueError("Input root is invalid. "+
                    "This is not ancestor of s and t")
        else:
            ca = s_ancestors.intersection(t_ancestors)
            length_from_root = {
                    each:nx.dijkstra_path_length(
                        self.reference_graph,
                        source=each,
                        target=r
                        ) for each in ca}
            lca = max(length_from_root.items(), key=lambda x:x[1])[0]

            path_length_from_s_to_t = ( nx.dijkstra_path_length(
                self.reference_graph,
                source=s,
                target=lca) +
                nx.dijkstra_path_length(
                    self.reference_graph,
                    source=t,
                    target=lca) )
            return (lca, path_length_from_s_to_t)

    def generate_redundant_graph(self, y1, y2, root):
        """
        Method for calculation of redundant graph; GraphEx
        """
        graph_ex = GraphEx()
        lca_all, connection_dict = self.calc_lca_all(y1, y2, root)
        graph_ex.set_lcas(lca_all)
        graph_ex.set_connection(connection_dict)

        intermedium_node = set([])
        for each in product(y1, lca_all):
            intermedium_node = intermedium_node.union(nx.dijkstra_path(
                self.reference_graph.to_undirected(), each[0], each[1]))
        nodes = lca_all.union(y1).union(intermedium_node)
        subgraph = self.reference_graph.subgraph(nodes)
        graph_ex.set_graph_ex(subgraph)
        return graph_ex

    def get_best_lcas(self, graph_ex_t, graph_ex_p, true_node, predict_node, lca_all):
        lcas = sorted(lca_all,\
                key=lambda x:graph_ex_t.get_n_connected(x)+\
                graph_ex_p.get_n_connected(x), reverse=True)
        best_lcas=[]
        i=0
        while True:
            best_lcas.append(lcas[i])
            i+=1
            if self.is_satisfy(best_lcas, graph_ex_t, graph_ex_p, true_node, predict_node):
                break
        for lca in best_lcas:
            if self.is_satisfy(list(set(best_lcas)-set([lca])), graph_ex_t, graph_ex_p, true_node, predict_node):
                    best_lcas.remove(lca)
        for lca in best_lcas[::-1]:
            if self.is_satisfy(list(set(best_lcas)-set([lca])), graph_ex_t, graph_ex_p, true_node, predict_node):
                    best_lcas.remove(lca)
        return best_lcas

    def get_best_path(self, best_lcas, graph_ex):
        intermedium_node = set([])
        for lca in best_lcas:
            for source in graph_ex.get_connected(lca):
                if source is not None:
                    path = set(nx.dijkstra_path(self.reference_graph, source, lca))
                    path.discard(lca)
                    path.discard(source)
                    intermedium_node = intermedium_node.union(path)
        return intermedium_node

    def is_satisfy(self, best_lcas, graph_ex_t, graph_ex_p, true_node, predict_node):
        """
        Checking whether all true_node or predict_node is connected to
            LCA node at least one to satisfy constraint 3 in minimal LCA
            graph extension .
        """

        satisfied_true_node = set([])
        satisfied_predict_node = set([])
        for lca in best_lcas:
            satisfied_true_node = satisfied_true_node.union(set(graph_ex_t.get_connected(lca)))
            satisfied_predict_node = satisfied_predict_node.union(set(graph_ex_p.get_connected(lca)))
        satisfied_true_node.discard(None)
        satisfied_predict_node.discard(None)

        if satisfied_true_node == true_node and satisfied_predict_node == predict_node:
            return True
        return False

    def remove_redundancy(self, graph_ex_t, graph_ex_p, true_node, predict_node):
        """
        Removing redundancy from GraphEx to estimate Rlca, Plca, Flca.
        """
        lca_all = graph_ex_t.lcas.union(graph_ex_p.lcas)
        best_lcas = self.get_best_lcas(graph_ex_t, graph_ex_p, true_node, predict_node, lca_all)

        best_path_true = self.get_best_path(best_lcas, graph_ex_t)
        best_path_predict = self.get_best_path(best_lcas, graph_ex_p)
        graph_t = graph_ex_t.graph_ex.subgraph(set(best_lcas).union(true_node).union(best_path_true))
        graph_p = graph_ex_p.graph_ex.subgraph(set(best_lcas).union(predict_node).union(best_path_predict))
        return (graph_t, graph_p)

    def generate_lca_graph(self, true_node, predict_node, root):
        """
        Generate non-redundant graph by tuple
        """
        true_node = set(true_node)
        predict_node = set(predict_node)
        graph_ex_t = self.generate_redundant_graph(true_node, predict_node, root)
        graph_ex_p = self.generate_redundant_graph(predict_node, true_node, root)
        return self.remove_redundancy(graph_ex_t, graph_ex_p, true_node, predict_node)

class GraphEx(object):
    def __init__(self):
        self.lcas = None
        self.connection = None
        self.graph_ex = None

    def set_lcas(self, lcas):
        self.lcas = lcas

    def set_connection(self, connection):
        self.connection = connection

    def get_n_connected(self, key):
        """
            Return number of connected node of key .
        """
        if key in self.connection.keys():
            return len(self.connection[key])
        else:
            return 0

    def get_connected(self, key):
        """
            Return connected node of key if graph has.
        """
        if key in self.connection.keys():
            return self.connection[key]
        else:
            return [None]

    def set_graph_ex(self, graph_ex):
        self.graph_ex = graph_ex

def p_lca(graph_t, graph_p):
    y_aug = set(graph_t.node.keys())
    y_cap_aug = set(graph_p.node.keys())
    return len(y_aug.intersection(y_cap_aug)) / len(y_cap_aug)

def r_lca(graph_t, graph_p):
    y_aug = set(graph_t.node.keys())
    y_cap_aug = set(graph_p.node.keys())
    return len(y_aug.intersection(y_cap_aug)) / len(y_aug)

def f_lca(graph_t, graph_p, beta=1):
    plca = p_lca(graph_t, graph_p)
    rlca = r_lca(graph_t, graph_p)
    return (1+beta**2) * plca * rlca / (beta**2 * plca + rlca) 

def matrix2multi_label(matrix, label_list):
    matrix_np = np.array(matrix)
    label_list_np = np.array(label_list)
    if matrix_np.dtype != np.int:
        matrix_np = matrix_np.astype(np.int)
    if (len(np.argwhere(matrix_np==1)) + len(np.argwhere(matrix_np==0))) != matrix_np.size:
        raise ValueError("Input matrix must has only 0 or 1")

    y_sparsed = [list(label_list_np[np.where(each==1)]) for each in matrix_np]
    y_sparsed_np = np.array(y_sparsed)
    return y_sparsed_np

def add_dummy_node(graph, root, depth=0):
    if depth < 0:
        raise ValueError("depth value must be natural number")
    if type(depth) is not int:
        raise ValueError("depth value must be integer")

    copy_graph = graph.copy()
    i = 0
    while i < depth:
        if "dummy_{0}".format(i) in copy_graph.nodes():
            raise ValueError("Node name 'dummy_{0}' is reserved".format(i))
        elif i == 0:
            copy_graph.add_edge("dummy_{0}".format(i+1), root)
        else:
            copy_graph.add_edge("dummy_{0}".format(i+1), "dummy_{0}".format(i))
        i += 1
    return copy_graph

def get_dummy_node(root, depth):
    if depth == 0:
        return root
    else:
        return "dummy_{0}".format(depth)

def fbeta_lca_score(y_true_matrix, y_pred_matrix, graph, root, label_list, beta=1, regularize=False, dummy_depth=0):
    y_true_matrix = np.array(y_true_matrix)
    y_pred_matrix = np.array(y_pred_matrix)
    label_list = np.array(label_list)
    if y_true_matrix.shape != y_pred_matrix.shape:
        raise ValueError("Shape of input two matrix must be same.")
    d_graph = add_dummy_node(graph, root, dummy_depth)

    y_true_mlabel = matrix2multi_label(y_true_matrix, label_list)
    y_pred_mlabel = matrix2multi_label(y_pred_matrix, label_list)
    graph_generator = GraphGenerator(d_graph)

    result  = []
    for y_true, y_pred in zip(y_true_mlabel, y_pred_mlabel):
        if len(y_true) == 0:
            y_true.append(get_dummy_node(root, dummy_depth))
        if len(y_pred) == 0:
            y_pred.append(get_dummy_node(root, dummy_depth))
        graph_t, graph_p = graph_generator.generate_lca_graph(y_true, y_pred, root)
        result.append(f_lca(graph_t, graph_p, beta))
    result = np.array(result)
    if regularize == True:
        result_min = 1/len(label_list)
        result_max = 1
        result_average = ( ( np.average(result) - result_min ) / ( result_max - result_min ) )
    else:
        result_average = np.average(result)
    return result_average

def f1_lca_score(y_true_matrix, y_pred_matrix, graph, root, label_list):
    return fbeta_lca_score(y_true_matrix, y_pred_matrix, graph, root, label_list, 1)
