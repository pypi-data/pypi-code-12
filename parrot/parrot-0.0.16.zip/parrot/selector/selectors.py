import logging
import re
from parrot.exceptions import SelectorEmptyResult, SelectorSearchException
from parrot.utils import traceback_in_one_line
try:
    from lxml.html import document_fromstring
except ImportError:
    document_fromstring = None

from .base import Selector, SingleSelector, MultiSelector


logger = logging.getLogger(__name__)


class RegexpSelector(Selector):
    def __init__(self, regexp_or_pattern, *, silent=True):
        super().__init__(silent=silent)
        self.regexp = (
            re.compile(regexp_or_pattern) if isinstance(regexp_or_pattern, str)
            else regexp_or_pattern
        )

    def __str__(self):
        return '{}'.format(self.regexp.pattern)

    def __call__(self, data):
        try:
            candidates = self.regexp.findall(data)
        except Exception as exc:
            custom_exc = SelectorSearchException(
                self, data, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc)
            logger.error(custom_exc)
            return None

        if not candidates:
            exc = SelectorEmptyResult(self, data)
            self._raise_if_not_silent(exc)
            logger.warning(exc)
            return None
        return candidates


class SingleRegexpSelector(RegexpSelector, SingleSelector):
    def __call__(self, data):
        return SingleSelector.__call__(self, data)


class MultiRegexpSelector(RegexpSelector, MultiSelector):
    def __call__(self, data):
        return MultiSelector.__call__(self, data)


if document_fromstring is not None:
    class XpathSelector(Selector):
        """
        Объект, выполняющий поиск элементов на основе xpath в указанном HTML
        или объекте дерева (lxml.tree)
        """
        def __init__(self, xpath, *, silent=True):
            super().__init__(silent=silent)
            self.xpath = xpath

        def __str__(self):
            return '{}'.format(self.xpath)

        def __call__(self, html_or_tree):
            tree = (
                document_fromstring(html_or_tree)
                if isinstance(html_or_tree, (str, bytes))
                else html_or_tree
            )
            try:
                candidates = tree.xpath(self.xpath)
            except Exception as exc:
                custom_exc = SelectorSearchException(
                    self, html_or_tree, exc, traceback_in_one_line()
                )
                self._raise_if_not_silent(custom_exc)
                logger.error(custom_exc)
                return None

            if not candidates:
                exc = SelectorEmptyResult(self, html_or_tree)
                self._raise_if_not_silent(exc)
                logger.warning(exc)
                return None
            return candidates


    class SingleXpathSelector(XpathSelector, SingleSelector):
        def __call__(self, html_or_tree):
            return SingleSelector.__call__(self, html_or_tree)


    class MultiXpathSelector(XpathSelector, MultiSelector):
        def __call__(self, html_or_tree):
            return MultiSelector.__call__(self, html_or_tree)
