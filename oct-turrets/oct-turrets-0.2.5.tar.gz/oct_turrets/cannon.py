import time

from oct_turrets.base import BaseCannon


class Cannon(BaseCannon):

    def run(self):
        """The main run method of the canon
        """
        elapsed = 0
        trans = self.script_module.Transaction(self.config)
        trans.custom_timers = {}

        while self.run_loop:
            error = ''

            trans.setup()
            start = time.time()
            try:
                trans.run()
            except Exception as e:
                error = str(e)
            scriptrun_time = time.time() - start
            trans.tear_down()

            elapsed = time.time() - self.start_time

            epoch = time.mktime(time.localtime())

            data = {
                'elapsed': elapsed,
                'epoch': epoch,
                'scriptrun_time': scriptrun_time,
                'error': error,
                'custom_timers': trans.custom_timers
            }
            self.result_socket.send_json(data)
