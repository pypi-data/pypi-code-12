from prosodypy.base import ProsodyBasePlugin

class ProsodyPlugin(ProsodyBasePlugin):
    """
    Simple examplary prosody plugin that just logs hello
    """

    def load(self):
        self.module.log(u"debug", "Hello prosody from python!")
