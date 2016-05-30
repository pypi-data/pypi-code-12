
from tgbot.basicapi.model.base import Base

from tgbot.basicapi.model.message import Message

from tgbot.basicapi.model.user import User

from tgbot.tglogging import logger

class CallBackQuery(Base):

    def __createfromdata__(self, data):
        self.data = data
        self.callback_data = data["data"]

        self.callback_id = data["id"]

        self.from_User = User(data=data["from"])

        try:
            self.message = Message(data=data["message"])
        except KeyError:
            self.message = None
            logger.debug("No message available.")

        try:
            self.inline_message_id = data["inline_message_id"]
        except KeyError:
            self.inline_message_id=""
            logger.debug("No inline message id.")

    def __init__(self, callback_data=None,callback_id=None,from_User=None,message=None,inline_message_id=None,data=None):
        super().__init__()
        if data:
            self.__createfromdata__(data)
        else:
            self.callback_id = callback_id

            self.from_User = from_User

            self.message = message

            self.inline_message_id = inline_message_id

            self.callback_data = callback_data

