def square_(p_obj, nodes):
    """square neighborhood filtering"""

    neighbors = filter(lambda n: n.x >= p_obj['min_x'] - 1 and n.x <= p_obj['max_x'] + 1, nodes)
    neighbors = filter(lambda n: n.y >= p_obj['min_y'] - 1 and n.y <= p_obj['max_y'] + 1, neighbors)
    #neighbors = filter(lambda n: n.i != p_obj['p_i'], neighbors)
    return neighbors
