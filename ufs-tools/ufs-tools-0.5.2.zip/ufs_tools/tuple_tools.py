
def remove_duplicated_keep_order(value_in_tuple):
    new_tuple = []
    for i in value_in_tuple:
        if not (i in new_tuple):
            new_tuple.append(i)
    return new_tuple
    # return tuple(set(value_in_tuple))
