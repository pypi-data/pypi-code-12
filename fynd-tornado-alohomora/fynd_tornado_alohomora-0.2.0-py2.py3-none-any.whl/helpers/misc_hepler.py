

def get_bool_value(key):
    bool_val = True
    if not key or key == 'False':
        bool_val = False

    return bool_val