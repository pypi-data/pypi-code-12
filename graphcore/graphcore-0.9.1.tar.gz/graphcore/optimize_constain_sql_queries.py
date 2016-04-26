from .sql_query import SQLQuery

def constrain_sql_queries(call_graph):
    for node in call_graph.nodes:
        if isinstance(node.function, SQLQuery):
            for relation in node.relations:
                print nodefunction, relation
