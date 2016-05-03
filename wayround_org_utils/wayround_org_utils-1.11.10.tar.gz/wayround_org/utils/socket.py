
import select
import ssl
import threading
import queue
import time

import wayround_org.mail.miscs

DEBUG_NB_FUNCS = False


def nb_handshake(sock, stop_event=None, select_timeout=0.5):

    while True:

        if stop_event is not None and stop_event.is_set():
            break

        try:
            data = sock.do_handshake()
        except BlockingIOError:
            select.select([sock], [], [], select_timeout)
        except ssl.SSLWantReadError:
            select.select([sock], [], [], select_timeout)
        except ssl.SSLWantWriteError:
            select.select([], [sock], [], select_timeout)
        except OSError as err:
            if err.errno == 9:
                break
            else:
                raise
        else:
            break

    return


def nb_recv(sock, bs=4096, stop_event=None, select_timeout=0.5):
    """

    if len() of returned value is 0, then foreign socket is closed

    not returns until something recived from socket or socket is
    closed. use stop_event to terminate this function

    stop_event must be of threading.Event() type
    """

    if stop_event is not None:
        if not isinstance(stop_event, threading.Event):
            raise TypeError("`stop_event' must be of threading.Event type")

    data = b''

    while True:

        if stop_event is not None and stop_event.is_set():
            break

        try:
            data = sock.recv(bs)
        except BlockingIOError:
            select.select([sock], [], [], select_timeout)
        except ssl.SSLWantReadError:
            select.select([sock], [], [], select_timeout)
        except ssl.SSLWantWriteError:
            select.select([], [sock], [], select_timeout)
        except OSError as err:
            if err.errno == 9:
                ret = b''
                break
            else:
                raise
        else:
            break

    if DEBUG_NB_FUNCS:
        print("recvd: {}".format(data))

    return data


def nb_sendall(sock, data, bs=4096, stop_event=None, select_timeout=0.5):

    if DEBUG_NB_FUNCS:
        print("sending: {}".format(data))

    if stop_event is not None:
        if not isinstance(stop_event, threading.Event):
            raise TypeError("`stop_event' must be of threading.Event type")

    if type(data) != bytes:
        raise TypeError("`data' must be bytes")

    while True:

        try:
            sock.sendall(data)
        except BlockingIOError:
            select.select([], [sock], [], select_timeout)
        except ssl.SSLWantReadError:
            select.select([sock], [], [], select_timeout)
        except ssl.SSLWantWriteError:
            select.select([], [sock], [], select_timeout)
        except OSError as err:
            if err.errno == 9:
                ret = b''
                break
            else:
                raise
        else:
            break

        if stop_event is not None and stop_event.is_set():
            break

    return


class LblRecvReaderBuffer:

    def __init__(
            self,
            sock,
            recv_size=4096,
            line_terminator=wayround_org.mail.miscs.STANDARD_LINE_TERMINATOR,
            maximum_line_length=wayround_org.mail.miscs.MAX_LINE_LENGTH
            ):
        """

        line_terminator=b'\r\n' (0x10, 0x13) is mail system message terminator
        style

        if maximum_line_length is None, then control of maximum line length is
        disabled.

        if maximum_line_length is not None, it must be positive int

        if maximum_line_length is set, then if working thread
        (_02_worker_thread) detects limitation reach - then this class
        instance property .max_line_error is set to True and .stop() method is
        called.
        """

        if maximum_line_length is not None:
            if not isinstance(maximum_line_length, int):
                raise TypeError("`maximum_line_length' must be None or int")

            if not maximum_line_length >= 1:
                raise ValueError("`maximum_line_length' must be >= 1")

        self.sock = sock
        self.line_terminator = line_terminator
        self.recv_size = recv_size
        self.maximum_line_length = maximum_line_length

        self._socket_is_closed = False
        self._line_terminator_len = len(self.line_terminator)

        self._01_worker_thread = None
        self._02_worker_thread = None

        self._stop_flag = threading.Event()

        self._recv_buffer_queue = queue.Queue()

        # this buffer is here and not in thread look function for make
        # available it's size information
        self._input_bytes_buff = b''
        self._input_bytes_buff_lock = threading.Lock()

        # this list not supposed to be accessible for outsiders
        # and the only way to get items from it is special method
        self._lines = []
        self._lines_lock = threading.Lock()

        self.max_line_error = False

        return

    def start(self):
        if self._01_worker_thread is None:

            self._01_worker_thread = threading.Thread(
                target=self._worker_thread_target_01
                )
            self._01_worker_thread.start()

        if self._02_worker_thread is None:

            self._02_worker_thread = threading.Thread(
                target=self._worker_thread_target_02
                )
            self._02_worker_thread.start()

        return

    def stop(self):
        self._stop_flag.set()
        self.wait()
        self._01_worker_thread = None
        self._02_worker_thread = None
        return

    def wait(self):
        if self._01_worker_thread is not None:
            self._01_worker_thread.join()

        if self._02_worker_thread is not None:
            self._02_worker_thread.join()

        return

    def _worker_thread_target_01(self):
        """
        Recive data from socket and put it in queue.

        with this thread I just want server to read input data fast as I
        think it is important.
        """

        while True:
            if self._stop_flag.is_set():
                break

            res = nb_recv(self.sock, stop_event=self._stop_flag)

            if len(res) == 0:
                self._socket_is_closed = True
                break

            self._recv_buffer_queue.put(res)

        threading.Thread(target=self.stop).start()

        return

    def _worker_thread_target_02(self):
        """
        Takes data from queue and glues it with bytes string, after
        what - searches and slices it by line separators, adding result to
        dedicated list. warning: line separator is not stripped from lines!
        """

        while True:

            if self._stop_flag.is_set():
                break

            res_empty = False
            try:
                res = self._recv_buffer_queue.get(block=True, timeout=0.5)
            except queue.Empty:
                res_empty = True

            if res_empty:
                continue

            with self._input_bytes_buff_lock:

                self._input_bytes_buff += res

                while True:
                    if self._stop_flag.is_set():
                        break

                    sep_pos = self._input_bytes_buff.find(
                        self.line_terminator
                        )

                    if sep_pos == -1:
                        break

                    cut_pos = sep_pos + self._line_terminator_len

                    res_line_bytes = self._input_bytes_buff[:cut_pos]

                    self._input_bytes_buff = self._input_bytes_buff[cut_pos:]

                    with self._lines_lock:

                        self._check_line_length_rtn(len(res_line_bytes))
                        if self.max_line_error:
                            break

                        self._lines.append(res_line_bytes)

                self._check_line_length_rtn(len(self._input_bytes_buff))

                if self.max_line_error:
                    break

        threading.Thread(target=self.stop).start()

        return

    def _check_line_length_rtn(self, length):
        if self.maximum_line_length is not None:
            if length >= self.maximum_line_length:
                self.max_line_error = True
        return

    def get_lines_bytes_size(self, stop_event=None):
        sum_ = 0
        with self._lines_lock:
            for i in self._lines:

                if stop_event is not None and stop_event.is_set():
                    break

                if (self._stop_flag is not None
                        and self._stop_flag.is_set()):
                    break

                sum_ += len(i)

        return sum_

    def get_next_bytes(
            self,
            size,
            delete_readen_data=True,
            stop_event=None
            ):
        """
        if delete_readen_data is True, then in case on successful read,
            readen lines and readen part of last readen line will be removed.
        """

        if size < 0:
            raise ValueError("`size' must be not < 0")

        ret = None
        if self.get_lines_bytes_size(stop_event) >= size:
            with self._lines_lock:
                buff = b''
                line_i = 0
                remained_size = size
                error_exit = False
                len_lines = len(self._lines)
                while True:

                    if stop_event is not None and stop_event.is_set():
                        error_exit = True
                        break

                    if (self._stop_flag is not None
                            and self._stop_flag.is_set()):
                        error_exit = True
                        break

                    if remained_size < 0:
                        error_exit = True
                        raise Exception("programming error")

                    if remained_size == 0:
                        break

                    if len_lines == line_i:
                        break

                    if len(self._lines[line_i]) > remained_size:
                        buff += self._lines[line_i][:remained_size]
                        remained_size = 0
                        break
                    else:
                        buff += self._lines[line_i]
                        remained_size -= len(self._lines[line_i])

                    line_i += 1

                if not error_exit:
                    ret = buff

                    if delete_readen_data:

                        del buff
                        del line_i
                        del remained_size
                        del error_exit
                        del len_lines

                        left_delete_bytes = size

                        while True:

                            if left_delete_bytes == 0:
                                break

                            len_lines0 = len(self._lines[0])

                            if len_lines0 > left_delete_bytes:
                                self._lines[0] = \
                                    self._lines[0][left_delete_bytes:]
                                left_delete_bytes = 0
                            else:
                                del self._lines[0]
                                left_delete_bytes -= len_lines0

        return ret

    def nb_get_next_bytes(
            self,
            size,
            delete_readen_data=True,
            stop_event=None,
            retry_interval=0.2
            ):
        """

        Uses get_next_bytes(): wait's until it returns something.
        Can be interupted using passed event object.
        """

        if not isinstance(stop_event, threading.Event):
            raise TypeError("`stop_event' must be of threading.Event type")

        ret = None

        while True:

            if stop_event is not None and stop_event.is_set():
                break

            if (self._stop_flag is not None
                    and self._stop_flag.is_set()):
                break

            ret = self.get_next_bytes(
                size,
                delete_readen_data=delete_readen_data,
                stop_event=stop_event
                )

            if ret is not None:
                break

            time.sleep(retry_interval)

        return ret

    def get_next_line(self):
        """
        Returns next line, or None if there is not yet any. If socket is
        closed - and empty line with terminator is returned.

        this method is async. if self._lines has any items, this method
        returns first of them, and removes it from self._lines.

        this method supposed to be the only way to get data from self._lines,
        as there shuld be thread safety to work with self._lines.
        """

        ret = None

        if self._socket_is_closed:
            ret = self.line_terminator
        else:
            with self._lines_lock:
                if len(self._lines) != 0:
                    ret = self._lines[0]
                    del self._lines[0]

        return ret

    def nb_get_next_line(self, stop_event, retry_interval=0.2):
        """

        Uses get_next_line(): wait's until it returns something.
        Can be interupted using passed event object.
        """

        if not isinstance(stop_event, threading.Event):
            raise TypeError("`stop_event' must be of threading.Event type")

        ret = None

        while True:

            if stop_event is not None and stop_event.is_set():
                break

            if (self._stop_flag is not None
                    and self._stop_flag.is_set()):
                break

            ret = self.get_next_line()

            if ret is not None:
                break

            time.sleep(retry_interval)

        return ret

    def get_bytes_buffer_byte_size(self):
        with self._input_bytes_buff_lock:
            ret = len(self._input_bytes_buff)
        return ret

    def get_lines_buffer_byte_size(self):
        ret = 0
        with self._lines_lock:
            for i in self._lines:

                if (self._stop_flag is not None
                        and self._stop_flag.is_set()):
                    break

                ret += len(i)
        return ret

    def get_lines_count(self):
        with self._lines_lock:
            ret = len(self._lines)
        return ret
