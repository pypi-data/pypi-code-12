import sys
import time
import json
import logging
import traceback

from oct_turrets.base import BaseTurret
from oct_turrets.cannon import Cannon

log = logging.getLogger(__name__)


class Turret(BaseTurret):
    """This class represent the classic turret for oct
    """

    def init_commands(self):
        """Initialize the basics commandes for the turret
        """
        self.commands['start'] = self.run
        self.commands['status_request'] = self.send_status
        self.commands['kill'] = self.kill

    def send_status(self, msg=None):
        """Reply to the master by sending the current status
        """
        if not self.already_responded or self.status != self.READY:
            reply = self.build_status_message()
            self.result_collector.send_json(reply)

    def send_result(self, result):
        """Update the results and send it to the hq
        """
        result['turret_name'] = self.config['name']
        self.result_collector.send_json(result)

    def start(self):
        """Start the turret and wait for the master to run the test
        """
        log.info("starting turret")
        self.status = self.READY
        while self.start_loop:
            try:
                socks = dict(self.poller.poll(2000))
                self.send_status()
                if self.master_publisher in socks:
                    payload = self.master_publisher.recv_string()
                    payload = json.loads(payload)
                    command = self.find_command(payload)
                    if command:
                        command(payload['msg'])
            except (Exception, KeyboardInterrupt):
                self.close_sockets()
                raise

    def run(self, msg=None):
        """The main run method
        """
        if self.status == self.RUNNING:
            return None

        log.info("Starting test for turret %s", self.uuid)

        self.already_responded = True
        self.start_time = time.time()
        self.start_loop = False
        self.status = self.RUNNING
        self.send_status()

        if 'rampup' in self.config:
            rampup = float(self.config.get('rampup', 0)) / float(self.config['cannons'])
        else:
            rampup = 0

        last_insert = 0

        if rampup > 0 and rampup < 1:
            timeout = rampup * 1000
        else:
            timeout = 1000

        try:
            while self.run_loop:
                if len(self.cannons) < self.config['cannons'] and time.time() - last_insert >= rampup:
                    cannon = Cannon(self.start_time, self.script_module, self.uuid, self.context, self.config)
                    cannon.daemon = True
                    self.cannons.append(cannon)
                    cannon.start()
                    last_insert = time.time()

                socks = dict(self.poller.poll(timeout))
                if self.master_publisher in socks:
                    data = self.master_publisher.recv_string()
                    data = json.loads(data)
                    if 'command' in data and data['command'] == 'stop':  # not managed, must break the loop
                        log.info("Exiting loop, premature stop")
                        self.run_loop = False
                        break
                    elif 'command' in data:
                        command = self.find_command(data)
                        if command:
                            command(data['msg'])
                if self.local_result in socks:
                    results = self.local_result.recv_json()
                    self.send_result(results)

            self.reset_turret()

        except (Exception, RuntimeError, KeyboardInterrupt) as e:
            self.status = self.ABORTED
            log.error(e)
            self.send_status()
            traceback.print_exc()
            self.close_sockets()

    def reset_turret(self):
        """Reset the turret and set it ready for the next test
        """
        log.info("Sending stop signal to cannons...")
        for i in self.cannons:
            i.run_loop = False
        log.info("Waiting for all cannons to finish")
        for i in self.cannons:
            i.join()

        self.cannons = []
        self.already_responded = False
        self.start_loop = True
        self.run_loop = True

        # clear sockets
        self.close_sockets()
        self.setup_sockets()

        self.start()

    def kill(self, msg=None):
        """Kill the turret
        """
        for i in self.cannons:
            i.run_loop = False
        self.status = self.KILLED
        self.send_status()
        self.close_sockets()
        sys.exit(1)
