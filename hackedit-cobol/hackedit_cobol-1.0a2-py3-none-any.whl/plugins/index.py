import locale
from hackedit import api
from pyqode.core.cache import Cache
from pyqode.core.share import Definition
from pyqode.cobol.backend.workers import get_outline


class CobolSymbolParser(api.plugins.SymbolParserPlugin):
    mimetypes = ['text/x-cobol']

    @staticmethod
    def parse(path):
        def include_path_in_definition(path, d):
            d.file_path = path
            for ch in d.children:
                include_path_in_definition(path, ch)

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

        # todo: change get_outline to include path information
        results = get_outline(request_data)
        definitions = [Definition.from_dict(ddict) for ddict in results]
        for d in definitions:
            include_path_in_definition(path, d)
        return definitions
