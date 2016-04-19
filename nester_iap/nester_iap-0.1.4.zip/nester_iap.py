"""
This is the “nester_iap.py" module, and it provides one function called
repeat_print() which prints lists that may or may not include nested lists.
"""


def repeat_print(list_data, ident=False level=0):
    """
    This function takes a positional argument called “the_list", which is any
    Python list (of, possibly, nested lists). Each data item in the provided list
    is (recursively) printed to the screen on its own line. A second argument called
    “level" is used to insert tab-stops when a nested list is encountered.
    """
    for item in list_data:
        if isinstance(item, list):
            repeat_print(item, ident, level+1)
        else:
            if ident:
                for tab_stop in range(level):
                    print("\t"),
            print item


