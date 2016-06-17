import logging
import os
import time
import consolecolor

_MIDNIGHT = 24 * 60 * 60  # number of seconds in a day

try:
    unicode
    _unicode = True
except NameError:
    _unicode = False

LOGGING_COLORS = {
    logging.WARN : "cyan",
    logging.ERROR : "red"
}
class ConsoleColorHandler(logging.StreamHandler):

    def __init__(self, stream = None, ):

        global LOGGING_COLORS
        logging.StreamHandler.__init__(self,stream)
        self.colors = LOGGING_COLORS

    def emit(self, record):
        
        if 0 == len(self.colors):
            logging.StreamHandler.emit(self,record)
        else:
            level = record.levelno
            if level in self.colors:
                color = self.colors[level]
                printer = consolecolor.ColorPrinter(self.stream)
                try:
                    msg = self.format(record)
                    stream = self.stream
                    if not _unicode: #if no unicode support...
                        printer.print_color_text(color,msg)
                    else:
                        try:
                            if (isinstance(msg, unicode) and
                                getattr(stream, 'encoding', None)):
                                ufs = u'%s'
                                try:
                                    printer.print_color_text(color, ufs % msg)
                                except UnicodeEncodeError:
                                    #Printing to terminals sometimes fails. For example,
                                    #with an encoding of 'cp1251', the above write will
                                    #work if written to a stream opened or wrapped by
                                    #the codecs module, but fail when writing to a
                                    #terminal even when the codepage is set to cp1251.
                                    #An extra encoding step seems to be needed.
                                    printer.print_color_text(color,(ufs % msg).encode(stream.encoding))
                            else:
                                printer.print_color_text(color, msg)
                        except UnicodeError:
                            printer.print_color_text(color, msg.encode("UTF-8"))
                    self.flush()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    self.handleError(record)
            else:
                logging.StreamHandler.emit(self,record)

        
