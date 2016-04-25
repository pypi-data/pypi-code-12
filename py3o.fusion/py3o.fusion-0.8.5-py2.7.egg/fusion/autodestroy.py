from twisted.web.static import File
import os


class FileAutoDestroy(File):
    """special twisted.web.static.File resource subclass
    to make it auto destroy the file once served
    """
    def open(self):
        return AutodestroyFile(self.path, 'r')


class AutodestroyFile(file):
    """a simple file like object that will autodestroy when you close() it...
    """

    def close(self):
        """we just make sure that the file will be destroyed when closed...
        """
        super(AutodestroyFile, self).close()
        os.unlink(self.name)
