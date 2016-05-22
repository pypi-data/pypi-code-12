
from tgbot.basicapi.model.base import Base

class CallBackQuery(Base):

    def __createfromdata__(self,callback_data):
        pass

    def __init__(self, callback_data=None,callback_id=None,from_User=None,message=None,inline_message_id=None,data=None):
        if callback_data:
            self.__createfromdata__(callback_data)
        else:
            self.callback_id = callback_id

            self.from_User = from_User

            self.message = message

            self.inline_message_id = inline_message_id

            self.data = data

