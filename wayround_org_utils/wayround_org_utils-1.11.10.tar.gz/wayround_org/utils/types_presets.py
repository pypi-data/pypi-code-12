
import wayround_org.utils.types

LIST_OF_STR = {'t': list, '.': {'t': str}}
SET_OF_STR = {'t': set, '.': {'t': str}}

LIST_OF_BYTES = {'t': list, '.': {'t': bytes}}

LIST_OF_INT = {'t': list, '.': {'t': int}}


def is_list_of_str(value):
    ret = wayround_org.utils.types.struct_check(value, LIST_OF_STR)
    return ret


def is_set_of_str(value):
    ret = wayround_org.utils.types.struct_check(value, SET_OF_STR)
    return ret


def is_list_of_bytes(value):
    ret = wayround_org.utils.types.struct_check(value, LIST_OF_BYTES)
    return ret


def is_list_of_int(value):
    ret = wayround_org.utils.types.struct_check(value, LIST_OF_INT)
    return ret
