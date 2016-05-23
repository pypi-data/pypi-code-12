class InlineKeyboardButton:
    def __init__(self, text,url=None,callback_data=None, switch_inline_query=None):

        self.text= text

        self.url = url

        self.callback_data = callback_data

        self.switch_inline_query = switch_inline_query