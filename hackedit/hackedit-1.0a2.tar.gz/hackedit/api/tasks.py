"""
This module contains a simple API for running cancellable tasks in a
background process and make sure to automatically display a visual feedback
to the user.

A task is a function that runs in a background process. Communication
between the main process and the child is done through tcp sockets using our
own ipc library.

Once the task finished, a callback function will automatically get called
with the function's return value.

To start a background task, use :func:`start`.

Example::

    from hackedit import api


    def task_function(initial_value):
        # function that run in a background process
        import time
        total = initial_value
        for i in range(100):
            total += i
            time.sleep(.1)
        return {'status': True, 'total': total}


    def callback(ret_val):
        # callback function that get called on the main thread of the IDE
        # with the function's return value
        if ret_val:
            print('status = %r' % ret_val['status'])
            print('total = %r' % ret_val['total'])
        else:
            print('Task cancelled')


    # example of usage
    api.tasks.start(
        'Example task', task_function, callback, args=(0,))
    api.tasks.start(
        'Example task 2', task_function, callback, args=(10,))
    api.tasks.start(
        'Example task 3', task_function, callback, args=(100,),
        use_thread=True)

"""
from ._shared import _window


class TaskHandle:
    """
    Describes the public interface of a task handle (for documentation purpose
    """
    def report_progress(self, message, progress):
        """
        Reports progress updates to the main gui thread.
        :param message: Message associated with the progress update
        :param progress: New progress value.
        """
        print(message)


def start(name, func, callback, args=(), cancellable=True, use_thread=False):
    """
    Starts a task in background process/thread.

    A task is a regular function with positional and keyworded arguments.
    When the task completes, a callback function is executed with the task's
    return value as the first (and only) argument.

    Here is an example implementation of a background task function::

        def my_background_task(task_handle, *args, **kwargs):
            # do some work
            ...
            # report progress
            task_handle.report_progress('Half done', 50)
            # do some more work
            ...
            # return task result
            return ret_val


    .. note:: `task_handle` is a :class:`TaskHandle` instance that is always
              passed as the first argument to ``func``.

    :param name: Name of the task, the name will show up next to the
        spinner movie or in the background tasks popup dialog.
    :param func: Function/method to run in a background thread
    :param callback: Callback to execute when the worker has finished. This
        function must take one positional argument: the task's return value.
    :param args: arguments passed to ``func``
    :param cancellable: whether the task can be cancelled or not. Set it to
        False if the background operation cannot be terminated by the user.
    :param use_thread: True to use a background thread instead of a subprocess.
        Default is False. Use this if your arguments are unpickables.
    :return: the task instance created.
    """
    return _window().task_manager.start(
        name, func, callback, args, cancellable, use_thread)
