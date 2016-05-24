#
# PyAxel 0.1
#
# Downloaded from http://code.google.com/p/pyaxel/
# and ported to Python 3
#
from collections import namedtuple
import logging
import math
import os
import pickle
import shutil
import socket
import sys
import threading
import time

from optparse import OptionParser
from urllib.error import URLError
from urllib.request import urlopen, Request, install_opener, build_opener, ProxyHandler, HTTPCookieProcessor

logger = logging.getLogger(__name__)

std_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; '
        'en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/xml,application/xml,application/xhtml+xml,'
        'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'Accept-Language': 'en-us,en;q=0.5',
}


class ConnectionState:
    def __init__(self, n_conn, filesize):
        self.n_conn = n_conn
        self.filesize = filesize
        self.progress = [0 for i in range(n_conn)]
        self.elapsed_time = 0
        self.chunks = [int(filesize / n_conn) for i in range(n_conn)]
        self.chunks[0] += filesize % n_conn

    def download_sofar(self):
        dwnld_sofar = 0
        for rec in self.progress:
            dwnld_sofar += rec
        return dwnld_sofar

    def update_time_taken(self, elapsed_time):
        self.elapsed_time += elapsed_time

    def update_data_downloaded(self, fetch_size, conn_id):
        self.progress[conn_id] += fetch_size

    def resume_state(self, in_fd):
        try:
            saved_obj = pickle.load(in_fd)
        except pickle.UnpicklingError:
            logger.error("State file is corrupted")
            #now start download from the beginning
            return 

        self.n_conn = saved_obj.n_conn
        self.filesize = saved_obj.filesize
        self.progress = saved_obj.progress
        self.chunks = saved_obj.chunks
        self.elapsed_time = saved_obj.elapsed_time

    def save_state(self, out_fd):
        #out_fd will be closed after save_state() is completed
        #to ensure that state is written onto the disk
        pickle.dump(self, out_fd)


class ProgressBar:
    def __init__(self, n_conn, conn_state):
        self.n_conn = n_conn
        self.dots = ["" for i in range(n_conn)]
        self.conn_state = conn_state

    def _get_term_width(self):
        term_size = shutil.get_terminal_size((80, 20))
        return term_size.columns

    def _get_download_rate(self, bytes):
        ret_str = report_bytes(bytes)
        ret_str += "/s."
        return len(ret_str), ret_str

    def _get_percentage_complete(self, dl_len):
        assert self.conn_state.filesize != 0
        ret_str = "{:.2f}%.".format(dl_len * 100 / self.conn_state.filesize)
        return len(ret_str), ret_str

    def _get_time_left(self, time_in_secs):
        ret_str = ""
        mult_list = [60, 60 * 60, 60 * 60 * 24]
        unit_list = ["second(s)", "minute(s)", "hour(s)", "day(s)"]
        for i in range(len(mult_list)):
            if time_in_secs < mult_list[i]:
                pval = int(time_in_secs / (mult_list[i - 1] if i > 0 else 1))
                ret_str = "%d %s" % (pval, unit_list[i])
                break
        if len(ret_str) == 0:
            ret_str = "%d %s." % (int(time_in_secs / mult_list[2]), unit_list[3])
        return len(ret_str), ret_str

    def _get_pbar(self, width):
        ret_str = "["
        for i in range(self.n_conn):
            dots_list = ['.' for j in range(int((self.conn_state.progress[i] *
                                             width) /
                                            self.conn_state.chunks[i]))]
            self.dots[i] = "".join(dots_list)
            if ret_str == "[":
                ret_str += self.dots[i]
            else:
                ret_str += "|" + self.dots[i]
            if len(self.dots[i]) < width:
                ret_str += '>'
                ret_str += "".join([' ' for i in range(width -
                                                       len(self.dots[i]) - 1)])

        ret_str += "]"
        return len(ret_str), ret_str

    def display_progress(self):
        dl_len = 0
        for rec in self.conn_state.progress:
            dl_len += rec

        avg_speed = dl_len / self.conn_state.elapsed_time if self.conn_state.elapsed_time > 0 else 0

        ldr, drate = self._get_download_rate(avg_speed)
        lpc, pcomp = self._get_percentage_complete(dl_len)
        ltl, tleft = self._get_time_left((self.conn_state.filesize - dl_len) /
                                         avg_speed if avg_speed > 0 else 0)
        # term_width - #(|) + #([) + #(]) + #(strings) +
        # 6 (for spaces and periods)
        term_width = self._get_term_width()
        available_width = term_width - (ldr + lpc + ltl) - self.n_conn - 1 - 6
        lpb, pbar = self._get_pbar(int(available_width / self.n_conn))
        sys.stdout.flush()
        line = "\r{} {} {} {}".format(pbar, drate, pcomp, tleft)
        blanks = " " * (term_width - len(line))
        print(line + blanks, file=sys.stderr, end="")


def report_bytes(bytes):
    if bytes == 0:
        return "0b"
    k = math.log(bytes, 1024)
    ret_str = "%.2f%s" % (bytes / (1024.0 ** int(k)), "bKMGTPEY"[int(k)])
    return ret_str


def get_file_size(url):
    request = Request(url, None, std_headers)
    data = urlopen(request)
    content_length = data.info()['Content-Length']
    # print content_length
    return int(content_length)


class FetchData(threading.Thread):

    def __init__(self, name, url, out_file, state_file,
                 start_offset, conn_state):
        threading.Thread.__init__(self)
        self.name = name
        self.url = url
        self.out_file = out_file
        self.state_file = state_file
        self.start_offset = start_offset
        self.conn_state = conn_state
        self.length = conn_state.chunks[name] - conn_state.progress[name]
        self.sleep_timer = 0
        self.need_to_quit = False
        self.need_to_sleep = False

    def run(self):
        # Ready the url object
        # print "Running thread with %d-%d" % (self.start_offset, self.length)
        request = Request(self.url, None, std_headers)
        if self.length == 0:
            return
        request.add_header('Range', 'bytes=%d-%d' % (self.start_offset,
                                                     self.start_offset + \
                                                     self.length))
        while 1:
            try:
                data = urlopen(request)
            except URLError as u:
                logger.error("Connection", self.name, " did not start with", u)
            else:
                break

        # Open the output file
        out_fd = os.open(self.out_file+".part", os.O_WRONLY)
        os.lseek(out_fd, self.start_offset, os.SEEK_SET)

        block_size = 1024
        # indicates if connection timed out on a try
        while self.length > 0:
            if self.need_to_quit:
                return

            if self.need_to_sleep:
                time.sleep(self.sleep_timer)
                self.need_to_sleep = False

            if self.length >= block_size:
                fetch_size = block_size
            else:
                fetch_size = self.length
            try:
                data_block = data.read(fetch_size)
                if len(data_block) == 0:
                    logger.info("Connection %s: [TESTING]: 0 sized block fetched." % self.name)
                if len(data_block) != fetch_size:
                    logger.info("Connection %s: len(data_block) != fetch_size, but continuing anyway." % self.name)
                    self.run()
                    return

            except socket.timeout as s:
                logger.error("Connection {} timed out with {}".format(self.name, s))
                self.run()
                return

            else:
                retry = 0

            # assert(len(data_block) == fetch_size)
            self.length -= fetch_size
            self.conn_state.update_data_downloaded(fetch_size, int(self.name))
            os.write(out_fd, data_block)
            self.start_offset += len(data_block)
            # saving state after each blk of dwnld
            state_fd = open(self.state_file, "wb")
            self.conn_state.save_state(state_fd)
            state_fd.close()


def general_configuration():
    # General configuration
    install_opener(build_opener(ProxyHandler()))
    install_opener(build_opener(HTTPCookieProcessor()))
    socket.setdefaulttimeout(120) # 2 minutes


def download(url, options):
    fetch_threads = []
    try:
        output_file = url.rsplit("/", 1)[1]   # basename of the url

        if options.output_file is not None:
            output_file = options.output_file

        if output_file == "":
            logger.error("Invalid URL")
            sys.exit(1)

        filesize = get_file_size(url)

        num_connections = min(int(filesize / 1000000) + 1, options.num_connections)

        conn_state = ConnectionState(num_connections, filesize)
        pbar = ProgressBar(num_connections, conn_state)

        # Checking if we have a partial download available and resume
        state_file = output_file + ".st"
        try:
            os.stat(state_file)
        except OSError as o:
            # statefile is missing for all practical purposes
            pass
        else:
            state_fd = open(state_file, "rb")
            conn_state.resume_state(state_fd)
            state_fd.close()

        logger.info("Need to fetch {}".format(report_bytes(conn_state.filesize - sum(conn_state.progress))))

        # create output file with a .part extension to indicate partial download
        out_fd = os.open(output_file+".part", os.O_CREAT | os.O_WRONLY)

        start_offset = 0
        start_time = time.time()
        for i in range(num_connections):
            # each iteration should spawn a thread.
            # print start_offset, len_list[i]
            current_thread = FetchData(i, url, output_file, state_file,
                                       start_offset + conn_state.progress[i],
                                       conn_state)
            fetch_threads.append(current_thread)
            current_thread.start()
            start_offset += conn_state.chunks[i]

        while len([t for t in fetch_threads if t.isAlive()]) > 0:
            # print "\n",progress
            end_time = time.time()
            conn_state.update_time_taken(end_time - start_time)
            start_time = end_time
            dwnld_sofar = conn_state.download_sofar()
            if options.max_speed != None and \
                    (dwnld_sofar / conn_state.elapsed_time) > \
                    (options.max_speed * 1024):
                for th in fetch_threads:
                    th.need_to_sleep = True
                    th.sleep_timer = dwnld_sofar / (options.max_speed * \
                        1024 - conn_state.elapsed_time)

            try:
                pbar.display_progress()
            except:
                pass

            time.sleep(1)

        pbar.display_progress()
        print("")

        # at this point we are sure dwnld completed and can delete the
        # state file and move the dwnld to output file from .part file
        os.remove(state_file)
        os.rename(output_file+".part", output_file)

    finally:
        for thread in fetch_threads:
            thread.need_to_quit = True


def main(options, args):
    general_configuration()
    url = args[0]
    download(url, options)

OptionsTuple = namedtuple('Options', ['output_file', 'num_connections', 'max_speed', 'verbose'])


def cmdline():
    parser = OptionParser(usage="Usage: %prog [options] url")
    parser.add_option("-s", "--max-speed", dest="max_speed",
                      type="int",
                      help="Specifies maximum speed (Kbytes per second)."
                      " Useful if you don't want the program to suck up"
                      " all of your bandwidth",
                      metavar="SPEED")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-n", "--num-connections", dest="num_connections",
                      type="int", default=4,
                      help="You can specify an alternative number of"
                      " connections here.",
                      metavar="NUM")
    parser.add_option("-o", "--output", dest="output_file",
                      help="By default, data does to a local file of "
                      "the same name. If this option is used, downloaded"
                      " data will go to this file.")

    (options, args) = parser.parse_args()

    print("Options: ", options)
    print("args: ", args)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
    try:
        main(options, args)
    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as e:
        # TODO: handle other types of errors too.
        logger.error(e)
        pass


if __name__ == "__main__":
    cmdline()




