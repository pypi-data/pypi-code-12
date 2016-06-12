class InlineKeyboardButton:
    def __init__(self, text,url="",callback_data="", switch_inline_query=""):

        self.text= text

        self.url = url

        self.callback_data = str(callback_data)

        self.switch_inline_query = switch_inline_query