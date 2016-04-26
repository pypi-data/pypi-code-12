from optparse import OptionParser
from messaging_client.metadata import VERSION

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8700


class DefaultOptionParser(object):

    def __init__(self):
        self.parser = OptionParser(usage="usage: %prog [options] filename",
                                   version="%prog " + VERSION)
        self.parser.add_option("-m", "--message",
                               dest="message",
                               help="Message to be sent.")
        self.parser.add_option("-a", "--address",
                               dest="host",
                               help="Address of remote host (default is " + DEFAULT_HOST + ").")
        self.parser.add_option("-p", "--port",
                               type="int",
                               dest="port",
                               help="Port of the application to send a message (default: " + str(DEFAULT_PORT) +")")
        self.parser.add_option("-d", "--debug",
                               dest="debug",
                               help="Enable debug mode.")

    def _set_attributes(self, args, options):
        self.args = args
        self.options = options

        if len(args) == 1:
            self.file = args[0]
            self.message = None
        elif options.message is not None:
            self.message = options.message
            self.file = None
        elif options.message is None and len(args) < 1:
            self.parser.error("No filename or message given!")

        if options.host is not None:
            self.host = options.host
        else:
            self.host = DEFAULT_HOST
        if options.port is not None:
            self.port = options.port
        else:
            self.port = DEFAULT_PORT
        if options.debug is not None:
            self.debug = True
        else:
            self.debug = False

    def _create_dictionary(self):
        values = {'args': self.args, 'options': self.options, 'file': self.file, 'message': self.message,
                  'host': self.host, 'port': self.port, 'debug': self.debug}
        return values

    def parse(self):
        """Parse command line arguments and options.

        Returns:
            Dictionary containing all given command line arguments and options.
        """
        (options, args) = self.parser.parse_args()
        self._set_attributes(args, options)
        return self._create_dictionary()
