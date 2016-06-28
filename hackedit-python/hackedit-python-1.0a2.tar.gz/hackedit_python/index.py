import locale
from hackedit import api
from pyqode.core.cache import Cache
from pyqode.core.share import Definition
from pyqode.python.backend import defined_names


class PySymbolParser(api.plugins.SymbolParserPlugin):
    """
    Parses symbols of python files, the parsed symbols are added to the project
    index by the indexing backend.
    """
    mimetypes = ['text/x-python']

    @staticmethod
    def parse(path):
        if path.endswith('_rc.py'):
            return []
        try:
            encoding = Cache().get_file_encoding(path)
        except KeyError:
            encoding = locale.getpreferredencoding()
        try:
            with open(path, encoding=encoding) as f:
                code = f.read()
        except (UnicodeDecodeError, OSError):
            try:
                with open(path, encoding='utf-8') as f:
                    code = f.read()
            except (UnicodeDecodeError, OSError):
                # could not deduce encoding
                return []
        request_data = {
            'path': path,
            'code': code
        }
        results = defined_names(request_data)
        return [Definition.from_dict(ddict) for ddict in results]
