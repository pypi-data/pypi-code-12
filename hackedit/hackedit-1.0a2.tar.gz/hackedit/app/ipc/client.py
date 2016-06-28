import locale
import atexit
import logging
import sys

from PyQt5 import QtCore, QtNetwork, QtWidgets

from hackedit.app.ipc import server, utils


class Process(QtCore.QObject):
    #: Signal emitted when a message is available (to report progress updates).
    message_available = QtCore.pyqtSignal(object)

    #: Signal emitted with the function's return value if the function executed
    #: without error (otherwise, errored is emitted).
    result_available = QtCore.pyqtSignal(object)

    #: Signal emitted if the function failed with an exception. Parameters
    #: are the exception instance and the traceback.
    errored = QtCore.pyqtSignal(Exception, str)

    #: Signal emitted when the process has finished. Parameter is the exit
    #: code of the process.
    finished = QtCore.pyqtSignal(int)

    def __init__(self, func, args=(), interpreter=sys.executable):
        """
        Starts a background process and communicate with it though sockets.

        :param func: callable object that will get executed in the background
            process
        :param args: function arguments.
        :param interpreter: the interpreter to use. Default is sys.executable.
        """
        super().__init__()
        atexit.register(self.terminate)
        self._process = None
        self._interpreter = interpreter
        self._func = func
        self._args = args
        self._socket = None

    def terminate(self):
        _logger().debug('terminating process')
        if self._process:
            self._process.terminate()
            self._process.kill()
        try:
            atexit.unregister(self.terminate)
        except ValueError:
            _logger().warn('failed to unregister atexit callback')

    def is_alive(self):
        return self._process.state() != self._process.NotRunning

    def start(self):
        self.port = utils.pick_free_port()
        _logger().debug('starting server process: %s',
                        ' '.join([self._interpreter, server.__file__,
                                  str(self.port)]))
        self._process = QtCore.QProcess()
        self._process.readyRead.connect(self._on_ready_read)
        self._process.setProcessChannelMode(self._process.MergedChannels)
        self._process.finished.connect(self._on_finished)
        self._process.stateChanged.connect(self._on_state_changed)
        self._process.start(
            self._interpreter, (server.__file__, str(self.port)))

    def _on_ready_read(self):
        try:
            output = self._process.readAllStandardOutput().data().decode(
                locale.getpreferredencoding())
        except (TypeError, AttributeError):
            return
        for line in output.splitlines():
            if not line:
                continue
            if line.startswith('Progress update:'):
                line = line.replace('Progress update: ', '')
                message, progress = [t.strip() for t in line.split('|')]
                progress = int(progress)
                msg = {'message': message, 'progress': progress}
                try:
                    self.message_available.emit(msg)
                except TypeError:
                    pass
            else:
                levels = [
                    ('DEBUG:', _logger().debug),
                    ('INFO:', _logger().info),
                    ('WARNING:', _logger().warn),
                    ('ERROR:', _logger().error),
                    ('CRITICAL:', _logger().critical),
                ]
                for lvl, log_fct in levels:
                    if line.startswith(lvl):
                        line = line.replace(lvl, '')
                        log_fct('server::<localhost:%s> %s', self.port, line)
                        break
                else:
                    _logger().debug('server::localhost:%s> %s',
                                    self.port, line)

    def _on_state_changed(self, state):
        try:
            if state == self._process.Running:
                # connect to server
                QtCore.QTimer.singleShot(100, self.connect)
        except (TypeError, AttributeError):
            return

    def connect(self):
        try:
            _logger().debug('connecting to server: localhost:%s', self.port)
        except AttributeError:
            return
        if self._socket:
            self._socket.setParent(None)
            self._socket.deleteLater()
            self._socket = None
        self._socket = QtNetwork.QTcpSocket()
        self._socket.connected.connect(self._on_connected)
        self._socket.error.connect(self._on_socket_error)
        self._socket.readyRead.connect(self._on_socket_ready_read)
        self._socket.connectToHost(QtNetwork.QHostAddress.LocalHost,
                                   self.port)

    def _on_socket_ready_read(self):
        data = utils.read_message(self._socket)
        if not data:
            return
        if 'ret_val' in data.keys():
            ret_val = data['ret_val']
            try:
                self.result_available.emit(ret_val)
            except (TypeError, AttributeError):
                # c++ instance deleted
                return
        elif 'exception' in data.keys():
            try:
                self.errored.emit(data['exception'], data['traceback'])
            except (TypeError, AttributeError):
                pass
        else:
            try:
                self.message_available.emit(data)
            except (TypeError, AttributeError):
                pass

    def _on_socket_error(self, error):
        if error == self._socket.ConnectionRefusedError:
            self.connect()

    def _on_connected(self):
        _logger().debug('connected to server: localhost:%s', self.port)
        data = {
            'function': self._func,
            'arguments': self._args,
        }
        try:
            utils.send_message(self._socket, data)
        except (TypeError, AttributeError) as e:
            self.terminate()
            raise e

    def _on_finished(self, exit_code, exit_status):
        try:
            if exit_status == self._process.CrashExit:
                exit_code = 139
        except (AttributeError, TypeError):
            pass
        _logger().debug('process finished with exit code %d' % exit_code)
        try:
            self.finished.emit(exit_code)
        except (TypeError, AttributeError):
            pass
        else:
            QtCore.QTimer.singleShot(1, self.cleanup)

    def cleanup(self):
        if self._socket:
            self._socket.buffer = None
            self._socket.payload = None
            self._socket.close()
            self._socket.setParent(None)
            self._socket.deleteLater()
            self._socket = None
        self.terminate()
        if self._process:
            self._process.setParent(None)
            self._process.deleteLater()
            self._process = None
        self._func = None
        self._args = None


def _logger():
    return logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.show()
    p = Process(utils.echo, args=('some', 'args'))
    p.port = 8086
    p.connect()
    app.exec_()
