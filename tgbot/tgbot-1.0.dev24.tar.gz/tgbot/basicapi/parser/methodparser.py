
import inspect
from tgbot.tglogging import logger

from tgbot.i18n import TranslatedObject
def parsemethods(message,command,args):
      if args:
        for obj in args:
            if inspect.getmembers(obj):
                for method in inspect.getmembers(obj):
                    if command.lower() == method[0]:
                        logger.info(command + " method recognized.")
                        if(isinstance(obj,TranslatedObject)):
                            obj.translate(message)
                        getattr(obj,method[0])(message)