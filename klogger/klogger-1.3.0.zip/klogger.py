from datetime import datetime
import time
import inspect
import threading
import sys

# _CAMEL_CASE_REGEX = re.compile(r"([a-z])([A-Z])")
# _UNDERSCORE_REGEX = re.compile(r"([a-z])_([a-z])")

INFO = 3
DEBUG = 2
WARNING = 1
ERROR = 0
__VERBOSITY = 3
__FUNC_NAME_LENGTH = 5
__SYNC_PRINT_LOCK = threading.Lock()
__REGISTER_LOCK = threading.Lock()
__THREAD_INDEX = 0
__THREADS = {}
__THREAD_STACK_DEPTH = {}
__THREAD_PARAMS = {}
__THREAD_PARAMS_FNAME_KEY = "func_name"

def __get_path_info():
    for item in inspect.stack():
        if item and __file__ not in item:
            return item[1]

    return __file__

# def add_ing(word):
#     assert type(word) == str and len(word) > 0
#
#     if len(word) >= 3 and word[-3:] == "ing":
#         return word
#
#     if word[-1] == 'e':
#         word = word[:-1]
#
#     return word + 'ing'

def __merge_dicts(a, b):
    a = a.copy()
    a.update(b)
    return a

def __get_log_type_string(t):
    if t == INFO:
        return "I"
    elif t == DEBUG:
        return "D"
    elif t == WARNING:
        return "W"
    elif t == ERROR:
        return "E"

    return None

def __sync_print(a, *args, **kwargs):
    with __SYNC_PRINT_LOCK:
        a = str(a) + "\n"
        sys.stdout.write(a, *args, **kwargs)

def __init_thread_info(thread):
    global __THREAD_INDEX

    __THREADS[thread] = __THREAD_INDEX
    __THREAD_STACK_DEPTH[thread] = 0
    __THREAD_PARAMS[thread] = {}
    __THREAD_INDEX += 1
    __THREAD_PARAMS[thread][__THREAD_PARAMS_FNAME_KEY] = ""

def __get_current_thread():
    t = threading.current_thread()

    if t not in __THREADS:
        __register_thread()

    return t

def __get_current_thread_id():
    return __THREADS[__get_current_thread()]

def __get_current_thread_type_string():
    cur_thread = __get_current_thread()
    is_main = isinstance(cur_thread, threading._MainThread)

    if is_main:
        return "main"
    else:
        thread_idx = __get_current_thread_id()
        return "t{:03d}".format(thread_idx)

def __get_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREAD_STACK_DEPTH:
        return 0

    return __THREAD_STACK_DEPTH[cur_thread]

def __get_current_thread_depth_string():
    depth = __get_current_thread_depth()
    return "d{:02d}".format(depth)

def __get_current_thread_indent_string():
    #depth = __get_current_thread_depth()
    #return " " * 2 * depth
    return ""

def __increase_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREAD_STACK_DEPTH:
        __THREAD_STACK_DEPTH[cur_thread] = 0

    __THREAD_STACK_DEPTH[cur_thread] += 1

def __decrease_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREAD_STACK_DEPTH:
        __THREAD_STACK_DEPTH[cur_thread] = 0

    __THREAD_STACK_DEPTH[cur_thread] -= 1
    __THREAD_STACK_DEPTH[cur_thread] = max(0, __THREAD_STACK_DEPTH[cur_thread])

def __get_current_thread_fname():
    thread = __get_current_thread()
    name = __THREAD_PARAMS[thread][__THREAD_PARAMS_FNAME_KEY]

    if len(name) > __FUNC_NAME_LENGTH + 2:
        name = name[:__FUNC_NAME_LENGTH] + ".."

    #name = "{{:{}s}}".format(__FUNC_NAME_LENGTH + 2).format(name)

    return name

def __get_prefix(t):
    timestamp = datetime.now().isoformat()
    type_str = __get_log_type_string(t)
    t_str = __get_current_thread_type_string()
    depth_str = __get_current_thread_depth_string()
    indent_str = __get_current_thread_indent_string()
    fname_str = __get_current_thread_fname()

    return "{0} [{3}] ({1}|{2}) <{5}> {4}".format(type_str, t_str, depth_str, timestamp, indent_str, fname_str)

def __register_thread():
    with __REGISTER_LOCK:
        cur_thread = threading.current_thread()
        if cur_thread not in __THREADS:
            __init_thread_info(cur_thread)

# def decorate_jobname(jobname):
#     """
#     Decorate job name suitable for humans
#     :type jobname: str
#     :return: decorated string
#     :rtype: str
#     """
#     assert type(jobname) == str and len(jobname) > 0
#
#     jobname = jobname.strip()
#     words = jobname.split()
#
#     assert len(words) > 0
#
#     words[0] = add_ing(words[0])
#     words = [word.capitalize() for word in words]
#
#     return " ".join(words)

def log(x, func=None, t=INFO, fargs=(), fkwargs={}, *args, **kwargs):

    init_progress = kwargs.pop("init_progress", False)
    max_value = kwargs.pop("max_value", 100)

    thread = __get_current_thread()
    prefix = __get_prefix(t)

    if init_progress:
        __THREAD_PARAMS[thread]["max_value"] = max_value
        __THREAD_PARAMS[thread]["progress"] = 0

    if not func:
        slog = prefix + x
        __sync_print(slog)
    else:
        __increase_current_thread_depth()
        if t <= __VERBOSITY:
            slog = "{}Now working on '{}'...".format(prefix, x)
            __sync_print(slog)

        # if (to_file):
        #     with open("{}.log".format(file), "w+") as f:
        #         f.write("[{}] In {}: {}\n".format(datetime.now(), file, slog))

        t1 = time.time()
        r = func(*fargs, **fkwargs)
        t2 = time.time()

        if t <= __VERBOSITY:
            elog = "{}'{}' finished in {:.3f}s.".format(prefix, x, t2 - t1)
            __sync_print(elog)

        # if (to_file):
        #     with open("{}.log".format(file), "a") as f:
        #         f.write("[{}] In {}: {}\n".format(datetime.now(), file, elog))


        __decrease_current_thread_depth()
        return r

# def parseFunctionName(name):
#     if _UNDERSCORE_REGEX.findall(name):
#         regex = _UNDERSCORE_REGEX
#     elif _CAMEL_CASE_REGEX.findall(name):
#         regex = _CAMEL_CASE_REGEX
#     else:
#         return None
#
#     return regex.sub("\g<1> \g<2>", name).lower()

def task(name=None, t=INFO, *args, **kwargs):
    """
    This decorator modifies current function such that its start, end, and
    duration is logged in console. If the task name is not given, it will attempt to
    infer it from the function name. Optionally, the decorator can log
    information into files.
    """

    def c_run(name, f, t, args, kwargs):
        def run(*largs, **lkwargs):
            thread = __get_current_thread()
            old_name = __THREAD_PARAMS[thread][__THREAD_PARAMS_FNAME_KEY]
            __THREAD_PARAMS[thread][__THREAD_PARAMS_FNAME_KEY] = name

            r = log(name, f, t, *(args + largs), **__merge_dicts(lkwargs, kwargs))

            __THREAD_PARAMS[thread][__THREAD_PARAMS_FNAME_KEY] = old_name
            return r

        return run

    if callable(name):
        f = name
        name = f.__name__

        return c_run(name, f, t, args, kwargs)

    if name == None:
        def wrapped(f):
            name = f.__name__

            return c_run(name, f, t, args, kwargs)

        return wrapped
    else:
        return c_run(name, None, t, args, kwargs)

def progress_task(name=None, t=INFO, max_value=100, *args, **kwargs):
    """
    This decorator extends the basic @task decorator by allowing users to
    display some form of progress on the console. The module can receive
    an increment in the progress through "tick_progress".
    """
    return task(name=name, t=t, init_progress=True, max_value=max_value, *args, **kwargs)

def tick_progress(amount=1, msg=None):
    cur_thread = __get_current_thread()
    __THREAD_PARAMS[cur_thread]["progress"] += amount
    prefix = __get_prefix(INFO)
    progress = __THREAD_PARAMS[cur_thread]["progress"]
    max_value = __THREAD_PARAMS[cur_thread]["max_value"]

    slog = prefix + ("" if msg == None else msg + " ") + "{}/{} ({}%)".format(progress, max_value, float(progress) / max_value * 100)
    __sync_print(slog)

def info(name=None, *args, **kwargs):
    return task(name, INFO, *args, **kwargs)

def debug(name=None, *args, **kwargs):
    return task(name, DEBUG, *args, **kwargs)

def set_verbosity(level):
    global __VERBOSITY
    __VERBOSITY = level