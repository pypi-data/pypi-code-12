import mimetypes
from PyQt5 import QtGui


class CobolIconProvider:
    """
    Provides an icon for the files whose mimetype is recognized as COBOL.
    """
    # SUPPORTED_EXTENSIONS = mimetypes.guess_all_extensions('text/x-cobol')

    @staticmethod
    def icon(file_info):
        mtype = mimetypes.guess_type(file_info.absoluteFilePath())[0]
        if mtype == 'text/x-cobol':
            return QtGui.QIcon(':/icons/cobol-mimetype.png')
        return None
