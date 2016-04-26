from messaging_client.messaging_client import MessagingClient


class App(object):

    def __init__(self):
        self.client = MessagingClient()
        self.values = self.client.parse_command_line()
        self.client.set_debug_mode(self.values['debug'])

    def run(self):
        listen_first = False  # TODO: move this to command line parameter
        host = self.values['host']
        port = self.values['port']
        print("Connecting to '" + host + ":" + str(port) + "'...\n")
        self.client.connect(host, port)
        if listen_first:
            response = self.client.receive_response()
            print(response)

        print("Sending message...")
        if self.values['file']:
            self.client.send_file_message(self.values['file'])
        else:
            self.client.send_message(self.values['message'])

        response = self.client.receive_response()
        print("Received response:")
        print(response)
        self.client.close()
