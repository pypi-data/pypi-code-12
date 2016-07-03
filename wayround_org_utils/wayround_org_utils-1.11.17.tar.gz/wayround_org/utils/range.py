

def get_range_indexes(value, ranges_list):
    ret = []
    for r in ranges_list:
        if value in r:
            ret.append(ranges_list.index(r))
    return ret


def get_range_first_index(value, ranges_list):
    ret = -1
    for r in ranges_list:
        if value in r:
            ret = ranges_list.index(r)
            break
    return ret


def is_in_ranges(value, ranges_list):
    return get_range_first_index(value, ranges_list) != -1
