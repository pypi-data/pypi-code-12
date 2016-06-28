"""
Private implementation of :mod:`hackedit.api.tasks`
"""
import logging
import traceback

from PyQt5 import QtCore, QtWidgets

from hackedit.api import events
from hackedit.api.widgets import ClickableLabel, SpinnerLabel
from hackedit.app.forms import task_widget_ui
from hackedit.app.ipc import Process


class TaskExceptionEvent(events.ExceptionEvent):
    def __init__(self, task, tb, exception):
        desc = ('The task "%s" failed due to an unhandled exception:\n"%s"\n' %
                (task.name, exception))
        self.traceback = tb
        self.name = task.name
        super().__init__(
            _('Task <%s> failed') % task.name, desc, exception,
            tb=self.traceback)


class SubprocessTaskHandle:
    """
    Descritbes the interface for a task handler.
    """
    @staticmethod
    def report_progress(message, progress):
        """
        Reports progress updates to the main gui thread.
        :param message: Message associated with the progress update
        :param progress: New progress value.
        """
        print(message)
        # send progress though stream (much more efficient than using sockets).
        print('Progress update: %s|%d' % (message, progress))


class ThreadTaskHandle:
    """
    Descritbes the interface for a task handler.
    """
    def __init__(self, thread):
        self.thread = thread

    def report_progress(self, message, progress):
        """
        Reports progress updates to the main gui thread.
        :param message: Message associated with the progress update
        :param progress: New progress value.
        """
        self.thread.message_available.emit(
            {'message': message, 'progress': int(progress)})


class TaskThread(QtCore.QThread):
    #: Signal emitted with the function's return value if the function executed
    #: without error (otherwise, errored is emitted).
    result_available = QtCore.pyqtSignal(object)

    #: Signal emitted when a progress update is available.
    message_available = QtCore.pyqtSignal(object)

    #: Signal emitted if the function failed with an exception. Parameters
    #: are the exception instance and the traceback.
    errored = QtCore.pyqtSignal(Exception, str)

    #: Signal emitted when the process has finished. Parameter is the exit
    #: code of the process.
    finished = QtCore.pyqtSignal(int)

    def __init__(self, func, args=()):
        self.func = func
        self.args = args
        super().__init__()

    def run(self):
        try:
            ret = self.func(ThreadTaskHandle(self), *self.args)
        except Exception as e:
            self.errored.emit(e, traceback.format_exc())
            ret = None
            exit_code = 1
        else:
            exit_code = 0
        finally:
            self.result_available.emit(ret)
            self.finished.emit(exit_code)


def run_task(func, *args):
    print('running task: %r with args=%r' % (func, args[0]))
    ret = func(SubprocessTaskHandle(), *args[0])
    print('task finished: %r' % func)
    return ret


class Task(QtCore.QObject):
    """
    Task wrapper. Creates a new subprocess.
    """
    #: Signal emitted when the worker has started
    started = QtCore.pyqtSignal(object)

    #: Signal emitted when results are available
    results_avaialble = QtCore.pyqtSignal(object, object)

    #: Signal emitted when the worker has finished.
    #: Parameter is the task instance and the task's return value.
    finished = QtCore.pyqtSignal(object)

    #: Signal emitted when the progress has changed
    #: Parameters:
    #:    - message (str)
    #:    - progress [0-100] (int)
    #: ..note:: It is up to the implementation to provide progress updates by
    #:          emitting this signal.
    progress_updated = QtCore.pyqtSignal(str, int)

    #: Signal emitted if an exception occured during the execution of the task
    #: function.
    errored = QtCore.pyqtSignal(object, str, Exception)

    def __init__(self, parent, function, args, use_thread=True):
        super().__init__(parent)
        self.function = function
        self.args = args
        self.aborted = False
        self.progress = -1
        self._finished = False
        self.use_thread = use_thread

    def cleanup(self):
        self.args = None
        self.function = None
        self.callback = None
        self.worker.setParent(None)
        self.worker.deleteLater()
        self.worker = None

    @QtCore.pyqtSlot()
    def cancel(self):
        """
        Cancels the worker by setting :attr:`_flg_abort` to True.

        .. note:: It is up to the worker implementation to check this flag to
                  and exit from its process method.
        """
        try:
            self.worker.terminate()
        except AttributeError:
            _logger().debug('failed to terminate process, already terminated')
        try:
            self.finished.emit(self)
        except RuntimeError as e:
            # wrapped C/C++ object of type Task has been
            return

    def start(self):
        """
        Worker's main entrypoint that will execute the worker function in
        a background process.
        """
        if self.use_thread:
            self.worker = TaskThread(self.function, args=self.args)
        else:
            self.worker = Process(run_task, args=(self.function, self.args))
        self.worker.finished.connect(self._on_finished)
        self.worker.result_available.connect(self._on_result_available)
        self.worker.errored.connect(self._on_error)
        self.worker.message_available.connect(self._on_message_available)
        self.worker.start()
        self.started.emit(self)

    def _on_result_available(self, ret_val):
        try:
            self.name
        except AttributeError:
            return
        else:
            _logger().debug('<{}> results available'.format(self.name))
            self.results_avaialble.emit(self, ret_val)

    def _on_finished(self, _):
        try:
            if not self._finished:
                self.finished.emit(self)
                self._finished = True
        except AttributeError:
            pass  # already deleted

    def _on_error(self, exc, tb):
        self.errored.emit(self, tb, exc)

    def _on_message_available(self, obj):
        try:
            message = obj['message']
            progress = obj['progress']
        except KeyError:
            _logger().warn('invalid message: %r, "message" and "progress" '
                           'keys not found...', obj)
        else:
            try:
                self.progress_updated.emit(message, progress)
            except AttributeError:
                pass  # already deleted


class TaskManager(QtCore.QObject):
    """
    Manages a collection of background tasks.
    """
    task_started = QtCore.pyqtSignal(Task)
    task_finished = QtCore.pyqtSignal(Task)
    task_count_changed = QtCore.pyqtSignal(int)

    @property
    def running_tasks(self):
        return self._running_tasks

    @property
    def count(self):
        return len(self._running_tasks)

    def __init__(self, window):
        super().__init__()
        self._running_tasks = []
        self.main_window = window

    def terminate(self):
        for task in self._running_tasks:
            task.cancel()

    def start(self, name, func, callback, args, cancellable, use_thread):
        _logger().debug('starting task <%s>' % name)
        task = Task(self, func, args, use_thread)
        task.name = name
        task.cancellable = cancellable
        task.callback = callback
        task.started.connect(self.task_started.emit)
        task.finished.connect(self._on_task_finished)
        task.results_avaialble.connect(self._on_task_results_available)
        task.errored.connect(self._post_errored_event)
        task.start()
        self._running_tasks.append(task)
        self.task_count_changed.emit(len(self._running_tasks))
        return task

    @staticmethod
    def _post_errored_event(task, traceback, exception):
        events.post(TaskExceptionEvent(task, traceback, exception))

    def _on_task_finished(self, task):
        _logger().debug('task finished <%s>' % task.name)
        try:
            self._running_tasks.remove(task)
        except ValueError:
            _logger().debug('failed to remove task %r from _running_tasks',
                            task)
        self.task_finished.emit(task)
        self.task_count_changed.emit(len(self._running_tasks))
        task.cleanup()
        task.setParent(None)
        task.deleteLater()

    @staticmethod
    def _on_task_results_available(task, ret_val):
        if task.callback:
            task.callback(ret_val)


class TaskWidget(QtWidgets.QWidget):
    """
    Widget that shows the status of a background task (progress, message).

    If the task is cancellable, a cancel button will appear next to the
    progress bar.
    """
    def __init__(self, task):
        super().__init__()
        self.ui = task_widget_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.group.setTitle(task.name)
        self.ui.lbl_description.setText('')
        self.ui.lbl_description.hide()
        self.task = task
        self.ui.bt_cancel.clicked.connect(self.task.cancel)
        self.ui.bt_cancel.setVisible(task.cancellable)
        self._update_progress('', -1)
        self.task.progress_updated.connect(self._update_progress)

    def _update_progress(self, message, value):
        self.ui.lbl_description.setText(message)
        self.ui.lbl_description.setVisible(message != '')
        if value == -1:
            self.ui.pbar_progress.setMinimum(0)
            self.ui.pbar_progress.setMaximum(0)
        else:
            self.ui.pbar_progress.setMinimum(0)
            self.ui.pbar_progress.setMaximum(100)
        self.ui.pbar_progress.setValue(value)


class TaskListWidget(QtWidgets.QWidget):
    """
    Shows a list of TaskWidget in a widget window
    """
    def __init__(self, task_manager):
        """
        :type task_manager: TaskManager
        """
        super().__init__()
        self.vertical_layout = QtWidgets.QVBoxLayout()
        spacer = QtWidgets.QSpacerItem(
            20, 20, vPolicy=QtWidgets.QSizePolicy.Expanding)
        self.vertical_layout.addSpacerItem(spacer)
        self.setLayout(self.vertical_layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.Fixed)
        self.tm = task_manager
        self.tm.task_started.connect(self._add_task)
        self.tm.task_finished.connect(self._rm_task)
        self._insert_index = 0

    def close(self):
        self.tm = None
        self.vertical_layout = None

    def _add_task(self, task):
        widget = TaskWidget(task)
        task.widget = widget
        self.vertical_layout.insertWidget(self._insert_index, widget)
        self._insert_index += 1

    def _rm_task(self, task):
        widget = task.widget
        self.vertical_layout.removeWidget(widget)
        widget.setParent(None)
        self._insert_index -= 1


class TaskListPopup(QtWidgets.QDialog):
    """
    Popup dialog that shows the running tasks
    """
    def __init__(self, parent, task_manager):
        super().__init__(parent)
        self.setWindowTitle(_('Background tasks'))
        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout()
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(TaskListWidget(task_manager))
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setWindowFlags(QtCore.Qt.Popup)

    @staticmethod
    def sizeHint():
        return QtCore.QSize(500, 250)


class TaskManagerWidget(QtWidgets.QWidget):
    """
    This widget shows a progress bar when some background tasks are running.

    When the user click on the widget, a popup shows up with the list of
    running tasks and their status.

    If there is only one task, the progress bar display the progress of the
    current task. If there are multiple tasks running, the progress bar is set
    to indeterminate.
    """

    def __init__(self, window):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.spinner = SpinnerLabel()
        self.label = ClickableLabel()
        self.label.clicked.connect(self._clicked)
        layout.addWidget(self.spinner)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.task_manager = TaskManager(window)
        self.main_window = window
        self.task_manager.task_count_changed.connect(
            self._on_task_count_changed)
        self.popup = TaskListPopup(window, self.task_manager)
        self.popup.hide()
        self.setMouseTracking(True)

    def close(self):
        self.popup.setParent(None)
        self.main_window = None
        self.task_manager.window = None
        self.task_manager = None

    def _on_task_count_changed(self, count):
        self.show()
        if not count:
            self.popup.hide()
            self.hide()
            self.label.clear()
        elif count > 1:
            self.label.setText(_('%d process running') % count)
        else:
            if self.task_manager:
                self.label.setText(self.task_manager.running_tasks[0].name)

    def setVisible(self, value):
        if hasattr(self, 'toolbar_action'):
            self.toolbar_action.setVisible(value)
        super().setVisible(value)

    def _clicked(self):
        if not self.popup.isVisible():
            self.popup.show()
        else:
            self.popup.hide()
        QtWidgets.qApp.processEvents()


def _logger():
    return logging.getLogger(__name__)
