import re


class DbgCode:

    def __init__(self, inputstring):
        self.inputstring = inputstring
        self.inline_pattern = re.compile("\s*.*# *_dbg", re.MULTILINE)
        self.block_pattern = re.compile("\s*# *dbg.*?# */dbg", re.DOTALL)

    def clean(self):
        self.clean_inline()
        self.clean_blocks()
        return self.inputstring

    def clean_inline(self):
        self.inputstring = re.sub(self.inline_pattern, "", self.inputstring)

    def clean_blocks(self):
        self.inputstring = re.sub(self.block_pattern, "", self.inputstring)
