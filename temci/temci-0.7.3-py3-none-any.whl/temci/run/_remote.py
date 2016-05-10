import base64
import os
import random
import socket
import typing as t

import subprocess
from queue import Queue

import sys

import time

import fcntl

from temci.run.run_driver import RunProgramBlock, BenchmarkingResultBlock
from temci.run.run_worker_pool import AbstractRunWorkerPool, RunWorkerPool, ParallelRunWorkerPool
from temci.utils.typecheck import *
import json, logging
from temci.utils.settings import Settings
import bsonrpc


@bsonrpc.service_class
class RemoteRunWorkerPool(AbstractRunWorkerPool):
    """
    This worker pool runs the passed program blocks remotely on an other machine using SSH.
    """

    def __init__(self, host_and_user: str = "127.0.0.1", ssh_port: int = None, server_port: int = random.randint(4000, 9000), run_driver_name: str = None):
        """
        Initializes a worker pool.
        :param run_driver_name: name of the used run driver or None if the one set in the Settings should be used
        """
        super().__init__(disable_ht_check=True)
        self.queue = Queue()
        self.result_queue = Queue()
        if run_driver_name:
            Settings()["run/driver"] = run_driver_name
        self.ssh_cmd = []
        if host_and_user != "localhost":
            self.ssh_cmd.extend(["ssh", host_and_user])
            if ssh_port and ssh_port != 21:
                self.ssh_cmd.extend(["-p", str(ssh_port)])
        else:
            self.ssh_cmd.extend(["/bin/sh", "-c"])
        self.ssh_cmd.append("temci run_server " + str(server_port))
        self.proc = subprocess.Popen(self.ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                     universal_newlines=True)
        time.sleep(5)
        print(server_port)
        print((host_and_user.split("@")[-1], server_port))
        self.connect_tuple = (host_and_user.split("@")[-1], server_port)
        self.connect()
        self.server.setup(Settings().prefs)

    def connect(self):
        if hasattr(self, "rpc"):
            self.rpc.close()
            time.sleep(1)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.connect_tuple)
        self.rpc = bsonrpc.JSONRpc(self.s, self)
        self.server = self.rpc.get_peer_proxy()

    @bsonrpc.rpc_notification
    def log(self, rpc, level: int, msg: str, file: str, line: int):
        logging.log(level, "remote {}[{}]: {}".format(file, line, msg))

    @bsonrpc.rpc_notification
    def info(self, rpc, msg: str):
        logging.info("remote: " + str(msg))

    def submit(self, block: RunProgramBlock, id: int, runs: int):
        """
        Submits the passed block for "runs" times benchmarking.
        It also sets the blocks is_enqueued property to True.

        :param block: passed run program block
        :param id: id of the passed block
        :param runs: number of individual benchmarking runs
        """
        typecheck(block, RunProgramBlock)
        typecheck(runs, NaturalNumber())
        typecheck(id, NaturalNumber())
        self.connect()
        a = block.to_dict()
        logging.info("blabb")
        self.server.bla2( 1, 2)
        whole = json.dumps(a)
        #self.rpc.invoke_request("bla2", whole[0:500])
        #self.rpc.invoke_request("bla3", whole[5])
        #self.rpc.invoke_request("bla3", (id, runs))
        self.rpc.invoke_request("submit", a, id, runs)
        #self.server.submit(a, id, runs)
        logging.info("blabb3")

    def results(self, expected_num: int):
        """
        An iterator over all available benchmarking results.
        The items of this iterator are tuples consisting of
        the benchmarked block, the benchmarking result and the
        blocks id.
        The benchmarking results are simple
        ..run_driver.BenchmarkingResultBlock objects.
        :param expected_num: expected number of results
        """
        num = 0
        for (block, result, id) in self.server.results(expected_num):
            prog_block = RunProgramBlock.from_dict(id, block)
            result_block = BenchmarkingResultBlock.from_dict(result)
            num += 1
            yield (prog_block, result_block, id)

        print("####################", num, expected_num)

    def teardown(self):
        """
        Tears down the inherited run driver.
        This should be called if all benchmarking with this pool is finished.
        """
        print("########### close this hell")
        self.server.teardown()
        self.rpc.close()
        print("sdf")
        self.proc.kill()
        self.proc.poll()


class LogingHandler(logging.StreamHandler):

    def __init__(self):
        super().__init__()
        self.rpc = None

    def emit(self, record: logging.LogRecord):
        try:
            if self.rpc:
                self.rpc.invoke_notification("log", record.levelno, self.format(record), record.filename, record.lineno)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


@bsonrpc.service_class
class RunServerServices(object):

    def __init__(self):
        self.logger = LogingHandler()
        logging.getLogger().addHandler(self.logger)

    @bsonrpc.rpc_request
    def setup(self, rpc: bsonrpc.JSONRpc, settings: dict):
        self.logger.rpc = rpc
        Settings().load_from_dict(settings)
        if Settings()["run/cpuset/parallel"] == 0:
            self.pool = RunWorkerPool()
        else:
            self.pool = ParallelRunWorkerPool()
        self.logger.rpc = None

    @bsonrpc.rpc_request
    def submit(self, rpc: bsonrpc.JSONRpc, data: dict, id: int, runs: int):
        os.system("notify-send dfds")
        rpc.invoke_notification("info", "hello")
        self.logger.rpc = rpc
        #logging.error("{}{}".format(id, data))
        block = RunProgramBlock.from_dict(id, data, run_driver=self.pool.run_driver)
        os.system("notify-send runs " +str(runs))
        self.pool.submit(block, id, runs)
        os.system("notify-send " +str(id + 100))
        self.logger.rpc = None

    @bsonrpc.rpc_request
    def results(self, rpc: bsonrpc.JSONRpc, expected_num: int) -> t.Tuple[dict, dict, int]:
        rpc.invoke_notification("info", "hello")
        self.logger.rpc = rpc
        l = []
        os.system("notify-send  expected num {}".format(expected_num))
        logging.info("I'm here")
        for (block, result, id) in self.pool.results(expected_num):
            os.system("notify-send {}".format(type(3)))
            l.append((block.to_dict(), result.to_dict() , id))
        self.logger.rpc = None
        return l

    @bsonrpc.rpc_request
    def teardown(self, rpc: bsonrpc.JSONRpc):
        self.logger.rpc = rpc
        logging.info("dsaf")
        os.system("notify-send dfds")
        self.pool.teardown()
        os.system("notify-send dfds")
        self.logger.rpc = None

    @bsonrpc.rpc_request
    def bla(self, rpc: bsonrpc.JSONRpc):
        os.system("notify-send bla")

    @bsonrpc.request
    def bla2(self, *args):
        os.system("notify-send blaffffffffffff")
        return 1

    @bsonrpc.request
    def bla3(self, *args):
        os.system("notify-send bluffffffffffff")
        return 1

def run_server(port: int = 4123):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    os.system("notify-send " + str(port))
    ss.bind(('localhost', port))
    ss.listen(10)
    server = RunServerServices()
    while True:
        s, _ = ss.accept()
        os.system("notify-send accepted")
        bsonrpc.JSONRpc(s, server)