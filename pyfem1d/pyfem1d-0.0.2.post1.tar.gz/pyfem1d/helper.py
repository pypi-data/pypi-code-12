from collections import OrderedDict
import inspect


def deploy_objects(path, class_):
    local_ret = globals()
    # local_ret = {}
    global_ret = globals()
    with open(path) as f:
        code = compile(f.read(), path, 'exec')
        exec(code, global_ret, local_ret)

    # globals().update(global_ret)

    # globals().update(local_ret)

    result = {}
    try:
        for key, i in local_ret.items():
            # print(key, i.__class__)
            if inspect.isclass(i):
                if issubclass(i, class_) and key != class_.__name__:
                    # print(key, i)
                    result[key] = i()
    except Exception as e:
        raise Exception("There was an error in the config %s:\n%s" %
                        (path, str(e)))

    # Sort the result dict according to the keys alphabetically
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    return result
