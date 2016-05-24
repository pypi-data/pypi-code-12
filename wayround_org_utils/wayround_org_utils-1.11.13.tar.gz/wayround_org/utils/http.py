

def convert_cb_params_to_boolean(params, names):

    for i in names:

        if i in params and (
            params[i].lower() in ['on', 'yes', 'true', 'ok']
            ):
            params[i] = True
        else:
            params[i] = False
