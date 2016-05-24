import logging
import re
from urllib.parse import urljoin
from parrot.exceptions import BadFormatterValue
try:
    from lxml.html import HtmlElement
except ImportError:
    HtmlElement = None


logger = logging.getLogger(__name__)


_spaces_regexp = re.compile(r'\s+')


def set_base_url_fabric(base_url):
    def formatter(val):
        return urljoin(base_url, val)
    return formatter


def delete_duplicate_spaces(val):
    if val is not None:
        return _spaces_regexp.sub(' ', val)


def clean_text(val):
    if val is not None:
        return delete_duplicate_spaces(val.strip())


if HtmlElement is not None:
    def _html_node_or_none(val):
        if not isinstance(val, HtmlElement):
            exc = BadFormatterValue('invalid value (isn\'t HtmlElement) ', val)
            logger.warning(exc)
            return None
        return val


    def get_html_node_attr(node, attr):
        node = _html_node_or_none(node)
        if node is not None:
            return node.get(attr)


    def html_node_text_content_raw(val):
        node = _html_node_or_none(val)
        if node is not None:
            return val.text_content()


    def html_node_text_content(val):
        """
        В полученном тексте удалены пробелы, переносы строк, символы
        табуляции, а точнее, все символы, которые подходят под маску "\s".

        :param val:
        :return:
        """
        return clean_text(html_node_text_content_raw(val))

    def html_href(val):
        return get_html_node_attr(val, 'href')


    def html_href_with_base_url_fabric(base_url):
        with_base = set_base_url_fabric(base_url)

        def formatter(val):
            href = html_href(val)
            if href is not None:
                return with_base(href)
        return formatter


    def html_src(val):
        return get_html_node_attr(val, 'src')


    def html_src_with_base_url_fabric(base_url):
        with_base = set_base_url_fabric(base_url)

        def formatter(val):
            src = html_src(val)
            if src is not None:
                return with_base(src)
        return formatter
