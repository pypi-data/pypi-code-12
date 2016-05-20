import re
import asyncio

sender = None


class Dealer(asyncio.SubprocessProtocol):

    def __init__(self):
        super()
        self.complete = asyncio.Future()
        self.sender = sender

    def pipe_data_received(self, data, line):
        if line.startswith(b'tail: '):
            return
        result = self.do_line(line.rstrip())
        if self.sender:
            self.sender.send(result)

    def do_line(self, line):
        tsuru_app = line.split(b" ")[-3].replace(b'"', b'').split(b'.')[0]
        value = line.split(b" ")[-2]
        r = b'.* "(?P<method>\w+) (?P<path>.*) HTTP.*" (?P<status_code>\d{3}).*'
        info = re.search(r, line)
        return {
            "metric": "response_time",
            "client": "tsuru",
            "app": tsuru_app.decode('utf-8'),
            "value": float(value),
            "path": info.groupdict()['path'].decode('utf-8'),
            "method": info.groupdict()['method'].decode('utf-8'),
            "status_code": info.groupdict()['status_code'].decode('utf-8')
        }
