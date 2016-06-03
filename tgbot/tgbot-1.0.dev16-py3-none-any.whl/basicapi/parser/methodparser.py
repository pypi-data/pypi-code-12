
import inspect
from tgbot.tglogging import logger


def parsemethods(message,command,args):
      if args:
        for obj in args:
            if inspect.getmembers(obj):
                for method in inspect.getmembers(obj):
                    if command.lower() == method[0]:
                        logger.info(command + " method recognized.")
                        getattr(obj,method[0])(message)