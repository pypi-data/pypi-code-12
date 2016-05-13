"""
.. module sgsclient

This module contains the client library code. In general, a client should
subclass ``StratumGSClientInstance`` and call the ``main`` function.
"""

import json
import socket
import sys


version = "0.1.0"


class StratumGSClient(object):

    def __init__(self, settings, client_instance_constructor):
        self._settings = settings
        self._socket = None
        self._socket_readfile = None
        self._socket_writefile = None
        self._client_instance_constructor = client_instance_constructor
        self._client_instances = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._socket_writefile: self._socket_writefile.close()
        if self._socket_readfile: self._socket_readfile.close()
        if self._socket: self._socket.close()

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        address = (self._settings["host"], self._settings["port"])
        try:
            self._socket.connect(address)
        except ConnectionError:
            print("Failed to connect to the specified host {}:{}".format(*address))
            sys.exit(1)
        self._socket_readfile = self._socket.makefile('rb', 0)
        self._socket_writefile = self._socket.makefile('wb', 0)

        self.send_obj_to_server({
            "type": "connect",
            "name": self._settings["name"],
            "supported_games": self._settings["supported_games"],
            "max_games": self._settings["max_games"]
        })

        response = self._receive_obj_from_server()
        if response["type"] != "name":
            print("Invalid response received from server")
            sys.exit(1)

        self._settings["name"] = response["name"]
        print("Connected to server as {}".format(response["name"]))


    def run(self):
        while True:
            obj = self._receive_obj_from_server()
            if obj["type"] == "close":
                game_id = obj["game_id"]
                if game_id in self._client_instances:
                    self._client_instances[game_id].server_closed_connection()
                    del self._client_instances[game_id]
            elif obj["type"] == "message":
                game_id = obj["game_id"]
                message = json.loads(obj["payload"])
                if game_id in self._client_instances:
                    self._client_instances[game_id].message_received_from_server(message)
            elif obj["type"] == "start":
                game_id = obj["game_id"]
                client_instance = self._client_instance_constructor(self, game_id)
                self._client_instances[game_id] = client_instance
            else:
                print("Invalid response received from server")
                sys.exit(1)

    def send_obj_to_server(self, obj):
        s = json.dumps(obj) + "\n"
        self._socket_writefile.write(s.encode())

    def _receive_obj_from_server(self):
        b = self._socket_readfile.readline()
        return json.loads(b.decode().strip())


class StratumGSClientInstance:
    """
        The client instance that is instantiated for each game. This class
        should be subclassed, and the methods ``server_closed_connection`` and
        ``message_received_from_server`` should be implemented.

        :param client: The client that spawned this instance.
        :type client: :class:`StratumGSClient`
        :param game_id: The game id of the new game.
        :type game_id: int
    """

    def __init__(self, client, game_id):
        self._client = client
        self._game_id = game_id

    def send_message_to_server(self, message):
        """
            Send a message to the engine. The message should be a JSON-encodable
            object. This method will encode the message, wrap it with the
            appropriate message for the server, and send it.

            :param message: A JSON-encodable message object for the engine.
        """

        self._client.send_obj_to_server({
            "type": "message",
            "game_id": self._game_id,
            "payload": json.dumps(message)
        })

    def server_closed_connection(self):
        """
            **Must be implemented by the subclass.**

            Called to notify the client that the server closed the connection.
        """

        print("Server closed the connection")

    def message_received_from_server(self, message):
        """
            **Must be implemented by the subclass.**

            Called when a message for this game is received from the server.
            Message will be the decoded value of the ``payload`` parameter of
            the original message from the server.

            :param message: The decoded message.
        """

        raise NotImplementedError


def main(client_instance_constructor, **kwargs):
    """
        The main run loop for the client. This function parses the command line
        arguments, then parses the ``kwargs``.

        The following configuration parameters are accepted as keyword
        arguments:

        - **host**: The host to connect to.
        - **port**: The port to connect to.
        - **name**: The name to request to connect with.
        - **supported_games**: The list of supported games.
        - **max_games**: The maximum number of games the client can support.

        :param client_instance_constructor: The class to instantiate for client
                                            instances.
    """

    settings = {
        "host": "localhost",
        "port": 8889,
        "name": None,
        "supported_games": [],
        "max_games": 5
    }

    # parse keyword arg parameters
    for key, value in kwargs.items():
        if key in settings:
            settings[key] = value

    # parse command line arg parameters
    args = sys.argv[1:]
    while args:
        try:
            arg = args.pop(0)
            if arg == "--host":
                settings["host"] = args.pop(0)
            elif arg == "--port":
                settings["port"] = int(args.pop(0))
            elif arg == "--max-games":
                settings["max_games"] = int(args.pop(0))
            else:
                print("Invalid argument.")
                sys.exit(1)
        except:
            print("Invalid argument format.")
            sys.exit(1)

    with StratumGSClient(settings, client_instance_constructor) as client:
        client.connect()
        client.run()
