
import logging
import os
import select
import socket
import ssl
import threading
import time

import wayround_org.utils.threading

CAT_READWRITE_TYPES = ['sync', 'async']

SELECT_SLEEP = 0.02
UNSELECTABLE_SLEEP = SELECT_SLEEP


class CatTerminationFlagFound(Exception):
    pass


class Streamer:

    def __init__(
            self,
            stream_object,
            stream_object_read_meth,
            stream_object_write_meth,
            stream_object_mode='sync',
            stream_object_selectable=True,
            stream_object_unselectable_sleep=0.2,
            bs=2 * 1024 ** 2,
            descriptor_to_wait_for=None,
            flush_after_each_write=False,
            standard_write_method_result=None,
            thread_name='Thread',
            termination_event=None,
            verbose=False,
            debug=False,
            on_exit_callback=None,
            on_input_read_error=None,
            on_output_write_error=None
            ):

        if not stream_object_mode in CAT_READWRITE_TYPES:
            raise ValueError("invalid `descriptor_mode'")

        if bs < 1:
            raise ValueError("invalid `bs'")

        if not standard_write_method_result in [None, False, True]:
            raise ValueError("invalid `standard_write_method_result'")

        if not isinstance(stream_object_selectable, bool):
            raise TypeError("`stream_object_selectable' must be bool")

        self._verbose = verbose
        self._debug = debug

        self._bs = bs

        self._stream_object = stream_object
        self._stream_object_mode = stream_object_mode
        self._stream_object_selectable = stream_object_selectable
        self._stream_object_unselectable_sleep = \
            stream_object_unselectable_sleep

        self._stream_object_read_meth = stream_object_read_meth
        self._stream_object_write_meth = stream_object_write_meth

        self._descriptor_to_wait_for = descriptor_to_wait_for

        self._standard_write_method_result = standard_write_method_result

        self._thread_name = thread_name

        self._flush_after_each_write = flush_after_each_write

        self._on_exit_callback = on_exit_callback
        self._on_input_read_error = on_input_read_error
        self._on_output_write_error = on_output_write_error

        self._termination_event = termination_event

        return

    def _wait_input_avail(self):

        if self._debug:
            logging.debug(
                "{}: waiting for input descriptor {}".format(
                    self._thread_name,
                    self._descriptor_to_wait_for
                    )
                )

        while len(
                select.select(
                    [self._descriptor_to_wait_for],
                    [],
                    [],
                    SELECT_SLEEP
                    )[0]
                ) == 0:

            if (self._termination_event
                    and self._termination_event.is_set()):
                raise CatTerminationFlagFound()

            if self._debug:
                logging.debug(
                    "{}: rewaiting for input descriptor {}".format(
                        self._thread_name,
                        self._descriptor_to_wait_for
                        )
                    )

            # the ssl.SSLSocket.pending() method is undocumented.
            # as so, I can't use it her, as it can be removed from ssl
            # socket class object at any time.
            # Instead of it I'll use time.sleep().
            # say thanks to /* Antoine Pitrou (pitrou) */
            # http://bugs.python.org/issue21430
            # .. commenting out

            # if isinstance(self._stream_object, ssl.SSLSocket):
            #     if self._debug:
            #         logging.debug(
            #             "{}: {} pending {}".format(
            #                 self._thread_name,
            #                 self._stream_object,
            #                 self._stream_object.pending()
            #                 )
            #             )
            #
            #     if self._stream_object.pending() != 0:
            #         if self._debug:
            #             logging.debug(
            #                 "{}: receiving pending data".format(
            #                     self._thread_name
            #                     )
            #                 )
            #         break

        if self._debug:
            logging.debug(
                "{}: input descriptor - ready - {}".format(
                    self._thread_name,
                    self._descriptor_to_wait_for
                    )
                )

        return

    def _wait_output_avail(self):

        if self._debug:
            logging.debug(
                "{}: waiting for output descriptor {}".format(
                    self._thread_name,
                    self._descriptor_to_wait_for
                    )
                )

        while len(
                select.select(
                    [],
                    [self._descriptor_to_wait_for],
                    [],
                    SELECT_SLEEP
                    )[1]
                ) == 0:

            if (self._termination_event
                    and self._termination_event.is_set()):
                raise CatTerminationFlagFound()

            if self._debug:
                logging.debug(
                    "{}: rewaiting for output descriptor {}".format(
                        self._thread_name,
                        self._descriptor_to_wait_for
                        )
                    )

        if self._debug:
            logging.debug(
                "{}: output descriptor - ready - {}".format(
                    self._thread_name,
                    self._descriptor_to_wait_for
                    )
                )

        return

    def read(self, data_size=None):
        """
        ret[0] == True - stream closed
        """

        ret_closed = False
        ret_buff = None

        try:

            if self._stream_object_mode == 'sync':

                if (self._termination_event
                        and self._termination_event.is_set()):
                    raise CatTerminationFlagFound()

                if self._debug:
                    logging.debug(
                        "Reading `{}' bytes using `{}'".format(
                            self._bs,
                            self._stream_object_read_meth
                            )
                        )

                res = self._stream_object_read_meth(self._bs)

                if self._debug:
                    logging.debug(
                        "Readed `{}' bytes using `{}'".format(
                            len(res),
                            self._stream_object_read_meth
                            )
                        )

                if len(res) == 0:
                    ret_closed = True
                    ret_buff = None
                    res = None

                else:

                    ret_closed = False
                    ret_buff = res
                    res = None

            elif self._stream_object_mode == 'async':

                if self._stream_object_selectable:
                    if self._descriptor_to_wait_for is not None:
                        self._wait_input_avail()
                else:
                    time.sleep(self._stream_object_unselectable_sleep)

                while True:

                    if (self._termination_event
                            and self._termination_event.is_set()):
                        raise CatTerminationFlagFound()

                    try:
                        if data_size is None:
                            ret_buff = self._stream_object_read_meth(self._bs)
                        else:
                            if data_size > self._bs:
                                ret_buff = self._stream_object_read_meth(
                                    self._bs
                                    )
                            else:
                                ret_buff = self._stream_object_read_meth(
                                    data_size
                                    )

                    except BlockingIOError:
                        pass

                    except ssl.SSLWantReadError:
                        # this is commented out, because withous use of
                        # .pending() too many garbage debugging messages
                        # are printed
                        # logging.debug("ssl.SSLWantReadError")
                        if self._stream_object_selectable:
                            select.select(
                                [self._descriptor_to_wait_for],
                                [],
                                [],
                                SELECT_SLEEP
                                )
                        else:
                            time.sleep(self._stream_object_unselectable_sleep)

                    except ssl.SSLWantWriteError:
                        # this is commented out, because withous use of
                        # .pending() too many garbage debugging messages
                        # are printed
                        # logging.debug("ssl.SSLWantWriteError")
                        if self._stream_object_selectable:
                            select.select(
                                [],
                                [self._descriptor_to_wait_for],
                                [],
                                SELECT_SLEEP
                                )
                        else:
                            time.sleep(self._stream_object_unselectable_sleep)
                    else:
                        break

            else:
                raise Exception(
                    "Programming error: self._stream_object_mode == {}".format(
                        self._stream_object_mode
                        )
                    )

        except CatTerminationFlagFound:
            logging.debug(
                "Caught termination flag in read method of {}:{}".format(
                    self,
                    self._thread_name
                    )
                )

            ret_closed = True
            ret_buff = None

            raise

        except:
            if self._on_input_read_error:
                threading.Thread(
                    target=self._on_input_read_error,
                    name="{} Input Read Error Thread".format(
                        self._thread_name
                        )
                    ).start()

            ret_closed = True
            ret_buff = None

            raise

        if not ret_closed and not isinstance(ret_buff, bytes):
            ret_closed = True
            raise TypeError(
                (
                    "Can read only bytes buffer "
                    "(Not str or anything other), but "
                    "buffer is ({}):{}..."
                    ).format(
                    type(ret_buff),
                    repr(ret_buff)[:100]
                    )
                )

        ret = ret_closed, ret_buff

        return ret

    def write(self, buff):

        if buff:

            if (self._termination_event
                    and self._termination_event.is_set()):
                raise CatTerminationFlagFound()

            try:

                while len(buff) != 0:

                    if self._stream_object_selectable:
                        if self._descriptor_to_wait_for is not None:
                            self._wait_output_avail()
                    else:
                        time.sleep(self._stream_object_unselectable_sleep)

                    sb = buff[:self._bs]
                    buff = buff[self._bs:]
                    self._stream_object_write_meth(sb)

                    if self._flush_after_each_write:
                        self._stream_object.flush()

            except TypeError as err_val:
                if err_val.args[0] == 'must be str, not bytes':
                    logging.warning(
                        "{}: hint: check that output is in bytes mode or do"
                        " conversion with convert_to_str option".format(
                            self._thread_name
                            )
                        )
                raise

            except CatTerminationFlagFound:
                logging.debug(
                    "Caught termination flag in write method of {}:{}".format(
                        self,
                        self._thread_name
                        )
                    )

                raise

            except BrokenPipeError:
                logging.exception(
                    "Broken pipe error arised. but I'll not give a damn\n"
                    " (take surraunding exit codes as a consideration of success)"
                    )
                # FIXME: cyrus-sasl-2.1.26.tar.gz
                #        (md5: a7f4e5e559a0e37b3ffc438c9456e425)
                #        gives an unknown broken pipe error.
                #        need to figure out this

                raise

            except:

                logging.error(
                    "{}: Can't use object's `{}' `{}' method.\n"
                    "    (possibly it isn't and error)".format(
                        self._thread_name,
                        self._stream_object,
                        self._stream_object_write_meth
                        )
                    )

                if self._on_output_write_error:
                    threading.Thread(
                        target=self._on_output_write_error,
                        name="`{}' Output Error Thread".format(
                            self._thread_name
                            )
                        ).start()

                raise

        return


def _is_cat_cycles_counter_enabled(verbose, count):
    return verbose or count is not None


def _is_cat_transferred_data_size_counter_enabled(
        verbose,
        maximum_total_data_transfer_size
        ):
    return verbose or maximum_total_data_transfer_size is not None


def cat(
        stdin,
        stdout,

        bs=2 * 1024 ** 2,
        count=None,
        maximum_total_data_transfer_size=None,

        threaded=False,
        thread_name='Thread',

        convert_to_str=None,

        read_method_name='read',
        write_method_name='write',

        read_type='sync',
        read_selectable=True,
        read_unselectable_sleep=UNSELECTABLE_SLEEP,

        write_type='sync',
        write_selectable=False,
        write_unselectable_sleep=UNSELECTABLE_SLEEP,

        exit_on_input_eof=True,
        flush_after_each_write=False,
        flush_on_input_eof=False,
        close_output_on_eof=False,

        descriptor_to_wait_for_input=None,
        descriptor_to_wait_for_output=None,

        apply_input_seek=True,
        apply_output_seek=True,

        standard_write_method_result=True,

        termination_event=None,

        verbose=False,
        debug=False,

        on_exit_callback=None,
        on_input_read_error=None,
        on_output_write_error=None
        ):

    if not read_method_name.isidentifier():
        raise ValueError("Wrong `read_method_name' parameter")

    if not write_method_name.isidentifier():
        raise ValueError("Wrong `write_method_name' parameter")

    if not read_type in CAT_READWRITE_TYPES:
        raise ValueError(
            "`read_type' must be in {}, not {}".format(
                CAT_READWRITE_TYPES,
                read_type
                )
            )

    if not write_type in CAT_READWRITE_TYPES:
        raise ValueError(
            "`write_type' must be in {}, not {}".format(
                CAT_READWRITE_TYPES,
                write_type
                )
            )

    if not hasattr(stdin, read_method_name):
        raise ValueError(
            "Object `{}' have no '{}' method".format(stdin, read_method_name)
            )

    if not hasattr(stdout, write_method_name):
        raise ValueError(
            "Object `{}' have no '{}' method".format(stdout, write_method_name)
            )

    if convert_to_str == True:
        convert_to_str = 'utf-8'
    elif convert_to_str == False:
        convert_to_str = None

    if (convert_to_str is not None
        and not isinstance(convert_to_str, str)
        ):
        raise ValueError(
            "convert_to_str can only be str(encoding name), bool or None"
            )

    if thread_name is None:
        thread_name = 'Thread'

    if threaded:

        return threading.Thread(
            target=cat,
            args=(stdin, stdout),
            kwargs=dict(
                bs=bs,
                count=count,
                threaded=False,
                thread_name=thread_name,
                verbose=verbose,
                convert_to_str=convert_to_str,
                read_method_name=read_method_name,
                write_method_name=write_method_name,
                read_type=read_type,
                read_selectable=read_selectable,
                read_unselectable_sleep=read_unselectable_sleep,
                write_type=write_type,
                write_selectable=write_selectable,
                write_unselectable_sleep=write_unselectable_sleep,
                exit_on_input_eof=exit_on_input_eof,
                flush_after_each_write=flush_after_each_write,
                flush_on_input_eof=flush_on_input_eof,
                close_output_on_eof=close_output_on_eof,
                descriptor_to_wait_for_input=descriptor_to_wait_for_input,
                descriptor_to_wait_for_output=descriptor_to_wait_for_output,
                apply_input_seek=apply_input_seek,
                apply_output_seek=apply_output_seek,
                standard_write_method_result=standard_write_method_result,
                termination_event=termination_event,
                on_exit_callback=on_exit_callback,
                on_input_read_error=on_input_read_error,
                on_output_write_error=on_output_write_error,
                debug=debug
                ),
            name=thread_name
            )

    #    if termination_event and termination_event.is_set():
    #        return None

    if verbose:
        logging.info("Starting `{}' thread".format(thread_name))

    buff = None

    if _is_cat_cycles_counter_enabled(verbose, count):
        c = 0

    if _is_cat_transferred_data_size_counter_enabled(
            verbose,
            maximum_total_data_transfer_size
            ):
        bytes_counter = 0

    if apply_input_seek and hasattr(stdin, 'seek'):
        try:
            stdin.seek(0)
        except:
            logging.exception("Can't seek")

    read_method = getattr(stdin, read_method_name)
    write_method = getattr(stdout, write_method_name)

    s1 = Streamer(
        stdin,
        read_method,
        None,
        stream_object_mode=read_type,
        stream_object_selectable=read_selectable,
        stream_object_unselectable_sleep=read_unselectable_sleep,
        bs=bs,
        descriptor_to_wait_for=descriptor_to_wait_for_input,
        thread_name='Input Streamer {}'.format(thread_name),
        termination_event=termination_event,
        verbose=verbose,
        debug=debug
        )

    s2 = Streamer(
        stdout,
        None,
        write_method,
        stream_object_mode=write_type,
        stream_object_selectable=write_selectable,
        stream_object_unselectable_sleep=write_unselectable_sleep,
        bs=bs,
        descriptor_to_wait_for=descriptor_to_wait_for_output,
        thread_name='Output Streamer {}'.format(thread_name),
        flush_after_each_write=flush_after_each_write,
        termination_event=termination_event,
        verbose=verbose,
        debug=debug
        )

    try:
        while True:

            if termination_event and termination_event.is_set():
                raise CatTerminationFlagFound()

            if maximum_total_data_transfer_size is None:
                closed, buff = s1.read()
            else:
                if bytes_counter + bs > maximum_total_data_transfer_size:
                    closed, buff = s1.read(
                        maximum_total_data_transfer_size - bytes_counter
                        )
                else:
                    closed, buff = s1.read()

            if not closed and buff is not None and len(buff) != 0:

                if debug:

                    buff_len = len(buff)
                    logging.debug(
                        "{}: Readed  {} bytes using method `{}'".format(
                            thread_name,
                            buff_len,
                            read_method
                            )
                        )
                    logging.debug(
                        "{}: buff data: {}".format(
                            thread_name,
                            repr(buff)
                            )
                        )
                    logging.debug(
                        "{}: Writing {} bytes using method `{}'".format(
                            thread_name,
                            buff_len,
                            write_method
                            )
                        )
                if convert_to_str is not None:
                    buff = str(buff, encoding=convert_to_str)

                if termination_event and termination_event.is_set():
                    raise CatTerminationFlagFound()

                s2.write(buff)

            else:
                if exit_on_input_eof:
                    break

            if _is_cat_cycles_counter_enabled(verbose, count):
                c += 1

            if isinstance(buff, (bytes, str)):
                if _is_cat_transferred_data_size_counter_enabled(
                        verbose,
                        maximum_total_data_transfer_size
                        ):

                    if isinstance(buff, bytes):
                        bytes_counter += len(buff)
                    if isinstance(buff, str):
                        bytes_counter += len(bytes(buff, 'utf-8'))

            if count is not None and count == c:
                break

            if (maximum_total_data_transfer_size is not None
                    and bytes_counter >= maximum_total_data_transfer_size):
                break

    except CatTerminationFlagFound:
        if debug:
            logging.debug(
                "{}: Termination flag caught".format(thread_name)
                )

    except:
        logging.exception(
            "{}: Exception in cat thread".format(thread_name)
            )

    if flush_on_input_eof:
        stdout.flush()

    if apply_output_seek and hasattr(stdout, 'seek'):
        try:
            stdout.seek(0, os.SEEK_END)
        except:
            pass

    if close_output_on_eof:
        if verbose:
            logging.info(" {}: Closing thread stdout".format(thread_name))

        stdout.close()

    if verbose:
        logging.info("""\
Ending `{name}' thread
    {{
       {num} cycles worked,
       {size} bytes ({sizem:4.2f} MiB) transferred,
       with buffer size {bufs} bytes ({bufm:4.2f} MiB)
    }}
""".format_map(
            {
                'name': thread_name,
                'num': c,
                'size': bytes_counter,
                'sizem': (float(bytes_counter) / 1024 / 1024),
                'bufs': bs,
                'bufm': (float(bs) / 1024 / 1024)
                }
            )
            )

    if on_exit_callback:
        threading.Thread(
            target=on_exit_callback,
            name="{} Exited Callback Thread".format(thread_name)
            ).start()

    return


def cat_socket_to_socket(
        one, another, bs=2 * 1024**2
        ):
    ret = cat(
        one,
        another,

        bs=bs,

        threaded=True,

        read_method_name='recv',
        write_method_name='send',

        read_type='async',
        read_selectable=False,
        read_unselectable_sleep=UNSELECTABLE_SLEEP,

        write_type='async',
        write_selectable=False,
        write_unselectable_sleep=UNSELECTABLE_SLEEP,

        exit_on_input_eof=False,
        flush_after_each_write=False,
        flush_on_input_eof=False,
        close_output_on_eof=False,

        descriptor_to_wait_for_input=one.fileno(),
        descriptor_to_wait_for_output=another.fileno(),

        apply_input_seek=False,
        apply_output_seek=False,

        standard_write_method_result=True,

        termination_event=None,

        verbose=False,
        debug=False,

        on_exit_callback=None,
        on_input_read_error=None,
        on_output_write_error=None
        )
    return ret


def lbl_write(
        stdin,
        stdout,
        threaded=False,
        typ='info'
        ):

    if not typ in ['info', 'error', 'warning']:
        raise ValueError("Wrong `typ' value")

    if threaded:
        return threading.Thread(
            target=lbl_write,
            args=(stdin, stdout),
            kwargs=dict(threaded=False)
            )
    else:

        while True:
            l = stdin.readline()
            if isinstance(l, bytes):
                l = l.decode('utf-8')
            if l == '':
                break
            else:
                l = l.rstrip(' \0\n')

                if typ == 'info':
                    stdout.info(l)
                elif typ == 'error':
                    stdout.error(l)
                elif typ == 'warning':
                    stdout.warning(l)

        return

    return


class SocketStreamer:

    """
    Featured class for flexibly handling socket connection

    Signals:
    'start' (self, self.socket)
    'stop' (self, self.socket)
    'error' (self, self.socket)
    'restart' (self, self.socket)
    'ssl wrap error' (self, self.socket)
    'ssl wrapped' (self, self.socket)
    'ssl ununwrapable' (self, self.socket)
    'ssl unwrap error' (self, self.socket)
    'ssl unwrapped' (self, self.socket)
    """

    def __init__(self, sock, socket_transfer_size=4096, debug=False):

        self.signal = wayround_org.utils.threading.Signal(
            self,
            ['start',
             'stop',
             'error',
             'restart',
             'ssl wrap error',
             'ssl wrapped',
             'ssl ununwrapable',
             'ssl unwrap error',
             'ssl unwrapped'
             ]
            )

        if sock.gettimeout() != 0:
            raise ValueError("`sock' timeout must be 0")

        if not isinstance(sock, (socket.socket, ssl.SSLSocket)):
            raise TypeError(
                "sock must be of type socket.socket or ssl.SSLSocket"
                )

        self.socket = sock
        self._socket_transfer_size = socket_transfer_size
        self._debug = debug

        self._pipe_inside = os.pipe2(os.O_NONBLOCK)
        self._pipe_outside = os.pipe2(os.O_NONBLOCK)

        # From remote process to current process.
        # For instance internals.
        self._strout = open(self._pipe_outside[1], 'wb', buffering=0)
        # For instance user.
        self.strout = open(self._pipe_outside[0], 'rb', buffering=0)

        # From current process to remote process.
        # For instance internals.
        self._strin = open(self._pipe_inside[0], 'rb', buffering=0)
        # For instance user.
        self.strin = open(self._pipe_inside[1], 'wb', buffering=0)

        # from strin to socket
        self._in_thread = None

        # from socket to strout
        self._out_thread = None

        self._connection_error_signalled = False
        self._connection_stop_signalled = False

        self._wrapping = False

        # flag indicating stop for instance threads
        self._stop_flag = False

        self._output_availability_watcher_thread = None
        self.connection = False

        self._in_thread_stop_event = threading.Event()
        self._out_thread_stop_event = threading.Event()

        return

    def __del__(self):
        try:
            self.destroy()
        except:
            logging.exception("Error destroying {}".format(self))
        return

    def destroy(self):
        self.stop()
        self._close_pipe_descriptors()
        return

    def get_socket(self):
        return self.socket

    def _close_pipe_descriptors(self):
        for i in [self._strout, self.strout, self._strin, self.strin]:
            if i:
                i.close()

        return

    def _start_threads(self):

        if self._stat_threads() == 'stopped':

            sock_selectable = True
            if self.is_ssl_working():
                sock_selectable = False

            self._in_thread = cat(
                stdin=self._strin,
                stdout=self.socket,
                threaded=True,
                write_method_name='send',
                close_output_on_eof=False,
                thread_name='strin -> socket',
                bs=self._socket_transfer_size,
                convert_to_str=None,
                read_method_name='read',
                read_type='async',
                read_selectable=True,
                write_type='async',
                write_selectable=sock_selectable,
                write_unselectable_sleep=UNSELECTABLE_SLEEP,
                exit_on_input_eof=True,
                descriptor_to_wait_for_input=self._strin,
                descriptor_to_wait_for_output=self.socket,
                apply_input_seek=False,
                apply_output_seek=False,
                flush_on_input_eof=False,
                on_exit_callback=self._on_in_thread_exit,
                on_output_write_error=self._on_socket_write_error,
                termination_event=self._in_thread_stop_event,
                flush_after_each_write=False,
                debug=self._debug
                )

            self._out_thread = cat(
                stdin=self.socket,
                stdout=self._strout,
                threaded=True,
                write_method_name='write',
                close_output_on_eof=False,
                thread_name='socket -> strout',
                bs=self._socket_transfer_size,
                convert_to_str=None,
                read_method_name='recv',
                read_type='async',
                read_selectable=sock_selectable,
                read_unselectable_sleep=UNSELECTABLE_SLEEP,
                write_type='async',
                write_selectable=True,
                exit_on_input_eof=True,
                descriptor_to_wait_for_input=self.socket,
                descriptor_to_wait_for_output=self._strout,
                apply_input_seek=False,
                apply_output_seek=False,
                flush_on_input_eof=True,
                on_exit_callback=self._on_out_thread_exit,
                on_input_read_error=self._on_socket_read_error,
                termination_event=self._out_thread_stop_event,
                flush_after_each_write=True,
                debug=self._debug
                )

            self._in_thread.start()
            self._out_thread.start()

            self._wait_threads('working')

        return

    def _stop_threads(self):

        if self._stat_threads() != 'stopped':

            t_in = self._in_thread
            t_out = self._out_thread

            self._in_thread_stop_event.set()
            self._out_thread_stop_event.set()

            if t_in is not None:
                t_in.join()

            if t_out is not None:
                t_out.join()

            self._wait_threads('stopped')

            self._in_thread_stop_event.clear()
            self._out_thread_stop_event.clear()

        return

    def _restart_threads(self):
        self._stop_threads()
        self._start_threads()

        self.signal.emit('restart', self, self.socket)

        return

    def _stat_threads(self):

        ret = 'unknown'

        v1 = self._in_thread
        v2 = self._out_thread

        if v1 is not None and v2 is not None:
            ret = 'working'

        elif v1 is None and v2 is None:
            ret = 'stopped'

        return ret

    def _send_connection_stopped_event(self):
        if not self._wrapping:
            if not self._connection_stop_signalled:
                self._connection_stop_signalled = True

                self.signal.emit('stop', self, self.socket)

        return

    def _send_connection_error_event(self):
        if not self._wrapping:
            if not self._connection_error_signalled:
                self._connection_error_signalled = True

                self.signal.emit('error', self, self.socket)

        return

    def start(self):

        if self.stat() == 'stopped':

            self._stop_flag = False

            self._connection_error_signalled = False
            self._connection_stop_signalled = False

            self._start_threads()

            self._output_availability_watcher_thread = threading.Thread(
                target=self._output_availability_watcher,
                name="Socket Output Availability Watcher Thread"
                )

            self._output_availability_watcher_thread.start()

            self.wait('working')

            self.signal.emit('start', self, self.socket)

        return

    def stop(self):

        if self.stat() != 'stopped':

            if self.is_ssl_working():
                self.stop_ssl()

            self._stop_flag = True

            self._stop_threads()

            self.wait('stopped')

            self.signal.emit('stop', self, self.socket)

        return

    def start_ssl(self, *args, **kwargs):
        """
        All parameters, same as for ssl.wrap_socket(). Exception is parameter
        socket, which
        taken from self.socket
        """

        if not self.is_ssl_working():

            self._wrapping = True

            if len(args) > 0:
                if issubclass(args[0], socket.socket):
                    del args[0]

            if 'sock' in kwargs:
                del kwargs['sock']

            kwargs['do_handshake_on_connect'] = False
            #            kwargs['suppress_ragged_eofs'] = False

            socket_wrap_result = None

            logging.debug("stopping threads before wrapping")

            self._stop_threads()

            logging.debug('before wrap sock is {}'.format(self.socket))

            try:
                socket_wrap_result = ssl.wrap_socket(
                    self.socket,
                    *args,
                    **kwargs
                    )

                while True:

                    try:
                        socket_wrap_result.do_handshake()

                    except ssl.SSLWantReadError:
                        select.select(
                            [socket_wrap_result.fileno()], [], [], SELECT_SLEEP
                            )

                    except ssl.SSLWantWriteError:
                        select.select(
                            [], [socket_wrap_result.fileno()], [], SELECT_SLEEP
                            )

                    except:
                        raise

                    else:
                        break

            except:
                logging.exception("ssl wrap error")
                self.signal.emit('ssl wrap error', self, self.socket)
            else:
                logging.debug(
                    """
peer cert:
{}
cipher:
{}
compression:
{}
""".format(
                        socket_wrap_result.getpeercert(binary_form=False),
                        socket_wrap_result.cipher(),
                        socket_wrap_result.compression()
                        )
                    )

                self.socket = socket_wrap_result

                #                self.socket.settimeout(0)

                logging.debug('after wrap sock is {}'.format(self.socket))

                logging.debug("starting threads after wrapping")

                self._start_threads()

                self.signal.emit('ssl wrapped', self, self.socket)

            self._wrapping = False

        return

    def stop_ssl(self):

        if self.is_ssl_working():

            if not self.connection:

                logging.debug(
                    "Connection already gone. "
                    "Unwrapping is pointless (and erroneous)"
                    )
                self.signal.emit('ssl ununwrapable', self, self.socket)

            else:

                self._wrapping = True

                logging.debug('before unwrap sock is {}'.format(self.socket))

                self._stop_threads()

                s = None
                try:
                    s = self.socket.unwrap()
                except:
                    logging.exception("ssl unwrap error")
                    self.signal.emit('ssl unwrap error', self, self.socket)

                else:
                    self.socket = s

                    self._start_threads()

                    logging.debug(
                        'after unwrap sock is {}'.format(self.socket)
                        )

                    self.signal.emit('ssl unwrapped', self, self.socket)

                self._wrapping = False

        return

    def _unwrap_procedure(self):
        if self.is_ssl_working():
            self.stop_ssl()
        else:
            logging.debug("Socket not wrapped - unwrapping not needed")
        return

    def is_ssl_working(self):
        return isinstance(self.socket, ssl.SSLSocket)

    def stat(self):

        ret = 'unknown'

        threads = self._stat_threads()
        v3 = self._output_availability_watcher_thread

        logging.debug(
            "{} :: status :: threads == {}, {}".format(self, threads, v3)
            )

        if threads == 'working':
            #  and v3 != None
            ret = 'working'

        elif threads == 'stopped' and v3 is None:
            ret = 'stopped'

        return ret

    def wait(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:
            logging.debug(
                "{} :: waiting for `{}`".format(
                    self.wait,
                    what
                    )
                )
            if self.stat() == what:
                break
            time.sleep(SELECT_SLEEP)

        return

    def _wait_threads(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:
            logging.debug(
                "{} :: waiting for `{}`".format(
                    self._wait_threads,
                    what
                    )
                )
            if self._stat_threads() == what:
                break
            time.sleep(SELECT_SLEEP)

        return

    def _on_in_thread_exit(self):
        self._in_thread = None
        self._any_thread_exited()
        return

    def _on_out_thread_exit(self):
        self._out_thread = None
        self._any_thread_exited()
        return

    def _any_thread_exited(self):

        if not self._wrapping:
            self.connection = False
            self._unwrap_procedure()
            self.socket.close()

        self._stop_threads()
        return

    def _on_socket_write_error(self):
        self._on_socket_read_write_error()
        return

    def _on_socket_read_error(self):
        self._on_socket_read_write_error()
        return

    def _on_socket_read_write_error(self):
        self.connection = False

        self.stop()

        self._send_connection_error_event()
        return

    def _output_availability_watcher(self):

        stopped_by_flag = False

        while len(
                select.select([], [self.socket.fileno()], [], SELECT_SLEEP)[1]
                ) == 0:

            if self._stop_flag:
                stopped_by_flag = True
                break

        if not stopped_by_flag:

            if not self._wrapping:

                self.connection = True
                self.signal.emit('start', self, self.socket)

        self._output_availability_watcher_thread = None

        return
