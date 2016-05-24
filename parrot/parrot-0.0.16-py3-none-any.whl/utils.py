import os
import traceback
from urllib.parse import urlsplit, quote

try:
    from lxml.html import tostring as html_to_string
except ImportError:
    html_to_string = None


def get_domain(url):
    return urlsplit(url)[1]


class MethodsIfSilentIsDefinedMixin(object):
    def _raise_if_not_silent(self, exc, logger=None):
        if not self.silent:
            if logger is not None:
                logger.error(exc)
            raise exc


def traceback_in_one_line(sep=' -> '):
    tb = traceback.format_exc()
    return tb.replace('\n', sep)


def make_dirs(dir_or_file_path):
    dir_path = (
        dir_or_file_path if os.path.isdir(dir_or_file_path)
        else os.path.dirname(dir_or_file_path)
    )
    if os.path.exists(dir_path):
        return
    os.makedirs(dir_path, exist_ok=True)


def tree_to_str(data_or_tree):
    """
    Переводит дерево в строку

    :param data_or_tree:
    :return:
    """
    # TODO: Для bytes добавить кодировку как параметр для decode
    if isinstance(data_or_tree, (str, bytes)):
        return str(data_or_tree)
    return (
        html_to_string(data_or_tree) if html_to_string is not None
        else str(data_or_tree)
    )


def url_quote(url):
    """
    Кодирует недопустимые символы url

    :param url:
    :return:
    """
    # http://stackoverflow.com/questions/120951/how-can-i-normalize-a-url-in-python
    # http://bugs.python.org/issue918368
    return quote(url, safe="%/:=&?~#+!$,;'@()*[]")
