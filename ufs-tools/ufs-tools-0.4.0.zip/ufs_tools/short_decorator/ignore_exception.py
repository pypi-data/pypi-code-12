import traceback


def ignore_exc(func):
    return ignore_exc_with_result(func)


def ignore_exc_with_result(exception_result=None, exception=Exception):
    # Ref: http://wklken.me/posts/2012/10/27/python-base-decorator.html
    def exc_wrapper(func):
        def wrap_with_exc():
            # noinspection PyBroadException
            try:
                return func()
            except exception, e:
                print "ignored the following exception:________________________________________________"
                traceback.print_exc()
                return exception_result

        return wrap_with_exc

    return exc_wrapper
