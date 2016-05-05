import pprint
from multiprocessing import Process
import logging

from zmq.eventloop import ioloop, zmqstream

logger = logging.getLogger(__name__)


def run_hub(task):
    logging.basicConfig(level=logging.DEBUG)

    task.reset()

    # Register on receive callback.
    task.command_stream = zmqstream.ZMQStream(task.command_socket)
    task.command_stream.on_recv(task.on_command_recv)

    # Register on receive callback.
    task.query_stream = zmqstream.ZMQStream(task.query_socket)
    task.query_stream.on_recv(task.on_query_recv)

    try:
        ioloop.install()
        logger.info('Starting hub ioloop')
        ioloop.IOLoop.instance().start()
    except RuntimeError:
        logger.warning('IOLoop already running.')


if __name__ == '__main__':
    from ..hub import Hub

    logging.basicConfig(level=logging.DEBUG)

    hub_process = Process(target=run_hub,
                          args=(Hub('tcp://*:12345', 'hub') ,))
    hub_process.daemon = False
    hub_process.start()
