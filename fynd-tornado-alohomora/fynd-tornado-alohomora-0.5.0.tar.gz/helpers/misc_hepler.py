def get_bool_value(key):
    """
    This method is used to get boolean value from json set value.
    :param key:
    :return:
    """
    bool_val = True
    if not key or key == 'False':
        bool_val = False

    return bool_val