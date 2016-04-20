from ..const import *

def list():
    arr = IT_DATA
    return arr


def get_ins_type_map():
    arr = IT_DATA
    m = {}
    for item in arr:
        m[item['name']] = item
    return m


