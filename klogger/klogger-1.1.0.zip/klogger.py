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
__SYNC_PRINT_LOCK = threading.Lock()
__THREADS = {}
__THREADS_STACK_DEPTH = {}

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

def __get_current_thread_id():
    if not hasattr(__get_current_thread_id, "index"):
        setattr(__get_current_thread_id, "index", 0)

    cur_index = getattr(__get_current_thread_id, "index", 0)
    cur_thread = threading.current_thread()
    if cur_thread not in __THREADS:
        __THREADS[cur_thread] = cur_index
        __THREADS_STACK_DEPTH[cur_thread] = 0
        setattr(__get_current_thread_id, "index", cur_index + 1)

    return __THREADS[cur_thread]

def __get_current_thread_type_string():
    cur_thread = threading.current_thread()
    is_main = isinstance(cur_thread, threading._MainThread)

    if is_main:
        return "main"
    else:
        thread_idx = __get_current_thread_id()
        return "t{:03d}".format(thread_idx)

def __get_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREADS_STACK_DEPTH:
        return 0

    return __THREADS_STACK_DEPTH[cur_thread]

def __get_current_thread_depth_string():
    depth = __get_current_thread_depth()
    return "d{:02d}".format(depth)

def __get_current_thread_indent_string():
    depth = __get_current_thread_depth()
    return " " * 2 * depth

def __increase_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREADS_STACK_DEPTH:
        __THREADS_STACK_DEPTH[cur_thread] = 0

    __THREADS_STACK_DEPTH[cur_thread] += 1

def __decrease_current_thread_depth():
    cur_thread = threading.current_thread

    if cur_thread not in __THREADS_STACK_DEPTH:
        __THREADS_STACK_DEPTH[cur_thread] = 0

    __THREADS_STACK_DEPTH[cur_thread] -= 1
    __THREADS_STACK_DEPTH[cur_thread] = max(0, __THREADS_STACK_DEPTH[cur_thread])

def __get_prefix(t):
    timestamp = datetime.now().isoformat()
    type_str = __get_log_type_string(t)
    t_str = __get_current_thread_type_string()
    depth_str = __get_current_thread_depth_string()
    indent_str = __get_current_thread_indent_string()

    return "{0} [{3}] ({1}|{2}) {4}".format(type_str, t_str, depth_str, timestamp, indent_str)

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

def log(jobName, func, t, *args, **kwargs):
    file = __get_path_info()
    prefix = __get_prefix(t)
    __increase_current_thread_depth()

    if t <= __VERBOSITY:
        slog = "{}Now working on '{}'...".format(prefix, jobName)
        __sync_print(slog)

    # if (to_file):
    #     with open("{}.log".format(file), "w+") as f:
    #         f.write("[{}] In {}: {}\n".format(datetime.now(), file, slog))

    t1 = time.time()
    r = func(*args, **kwargs)
    t2 = time.time()

    if t <= __VERBOSITY:
        elog = "{}'{}' finished in {:.3f}s.".format(prefix, jobName, t2 - t1)
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
    duration is logged in console. If task name is not given, it will attempt to
    infer it from the function name. Optionally, the decorator can log
    information into files.
    """
    if callable(name):
        f = name
        name = f.__name__

        return lambda *args, **kwargs: log(name, f, t, *args, **kwargs)

    if name == None:
        def wrapped(f):
            name = f.__name__
            return lambda *args, **kwargs: log(name, f, t, *args, **kwargs)

        return wrapped
    else:
        return lambda f: lambda *args, **kwargs: log(name, f, t, *args, **kwargs)

def info(name=None, *args, **kwargs):
    return task(name, INFO, *args, **kwargs)

def debug(name=None, *args, **kwargs):
    return task(name, DEBUG, *args, **kwargs)

def set_verbosity(level):
    global __VERBOSITY
    __VERBOSITY = level