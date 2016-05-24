import logging
from parrot.paginator import Paginator
from parrot.exceptions import CrawlerEmptySectionsUrls, CrawlerEmptySection
from parrot.parser import Parser
from parrot.utils import MethodsIfSilentIsDefinedMixin


logger = logging.getLogger(__name__)


class Crawler(MethodsIfSilentIsDefinedMixin):
    """
    'Паук'. Ищет и парсит объекты из каталога
    """
    def __init__(
        self, sections_init_url, sections_urls_parser, section_parser,
        paginator_parser, section_items_urls_parser, item_parser, *,
        silent=True
    ):
        self.sections_init_url = sections_init_url
        self.sections_urls_parser = sections_urls_parser
        self.section_parser = section_parser
        self.paginator_parser = paginator_parser
        self.section_items_urls_parser = section_items_urls_parser
        self.item_parser = item_parser
        self.silent = silent

    @classmethod
    def _urls_set_is_empty(cls, urls_set):
        return not (
            Parser.result_contain_attr(urls_set, 'urls') and urls_set['urls']
        )

    @classmethod
    def _sections_urls_set_is_empty(cls, sections_urls):
        return cls._urls_set_is_empty(sections_urls)

    @classmethod
    def _section_is_empty(cls, section_items):
        return cls._urls_set_is_empty(section_items)

    def _fetch_section_urls_with_paginate(self, section_url):
        """
        Для указанной категории собирает все ссылки на страницы включая
        переданный url.

        Например:
        section_url = 'http://domain.org/demo_category/'
        Объекты категории размещены на десяти страницах, тогда результатом
        будет итератор, возвращающий:
        [
            'http://domain.org/demo_category/',
            'http://domain.org/demo_category/2',
            'http://domain.org/demo_category/3',
            ...
            'http://domain.org/demo_category/10'
        ]
        :return:
        """
        yield from Paginator(section_url, self.paginator_parser)

    def _fetch_sections_urls(self, *, with_paginate=True):
        """
        Собрать ссылки на все категории проекта, для дальнейшего сбора ссылок
        на все объекты проекта

        :param with_paginate: Отвечает за сбор ссылок с пагинацией для каждой
                              категории (True/False = собирать/не собирать)
        :return:
        """
        sections_urls = self.sections_urls_parser.from_source(
            self.sections_init_url
        )
        if self._sections_urls_set_is_empty(sections_urls):
            exc = CrawlerEmptySectionsUrls(
                self.sections_init_url, sections_urls,
                with_paginate
            )
            self._raise_if_not_silent(exc)
            logger.error(exc)
            return ()

        sections_urls = sections_urls['urls']

        while sections_urls:
            section_url = sections_urls.pop(0)
            if section_url is None:
                continue
            if with_paginate:
                yield from self._fetch_section_urls_with_paginate(section_url)
            else:
                yield section_url

    def _fetch_section_items_urls(self, section_url):
        """
        Собрать все объекты со страницы категории

        :param section_url:
        :return:
        """
        section_items_urls = self.section_items_urls_parser.from_source(
            section_url
        )
        if self._section_is_empty(section_items_urls):
            exc = CrawlerEmptySection(section_url, section_items_urls)
            logger.warning(exc)
            return ()

        section_items_urls = section_items_urls['urls']
        while section_items_urls:
            section_item_url = section_items_urls.pop(0)
            if section_item_url is None:
                continue
            yield section_item_url

    def _fetch_sections_items_urls(self, sections_urls):
        """
        Собрать ссылки на все объекты во всех категориях проекта со всех
        страниц для дальнейшего обхода каждого url и сбора данных
        :return:
        """
        for section_url in sections_urls:
            yield from self._fetch_section_items_urls(section_url)

    def _parse_section(self, section_url):
        return self.section_parser.from_source(section_url)

    def _parse_sections(self, sections_urls):
        for section_url in sections_urls:
            yield self._parse_section(section_url)

    def parse_item(self, item_url):
        """
        Спарсить объект по url

        :param item_url:
        """
        item = self.item_parser.from_source(item_url)
        return item

    def parse_items(self, items_urls):
        items = (self.parse_item(item_url) for item_url in items_urls)
        yield from items

    def _find_and_parse_items_without_sections_info(self):
        """
        Найти все товары и собрать информацию по ним

        :return: ссылка на объект, результат парсинга объекта
        :rtype: tuple
        """
        for item_url in self._fetch_sections_items_urls(
            self._fetch_sections_urls()
        ):
            yield item_url, self.parse_item(item_url)

    def _find_and_parse_items_with_sections_info(self):
        """
        Найти все товары и собрать информацию по ним

        Операция получается дороже, чем
        self._find_and_parse_items_without_sections_info, т. к. для каждой
        категории выполняется парсинг информации.

        :return: ссылка на объект, результат парсинга объекта,
                 ссылка на категорию, информация о категории
        :rtype: tuple
        """
        for section_url in self._fetch_sections_urls(with_paginate=False):
            section_info = self._parse_section(section_url)
            for section_page_url in self._fetch_section_urls_with_paginate(
                section_url
            ):
                for item_url in self._fetch_section_items_urls(
                    section_page_url
                ):
                    yield (
                        item_url, self.parse_item(item_url),
                        section_url, section_info
                    )

    def find_and_parse_items(self, *, with_section_info=False):
        """
        Найти и распарсить объекты

        :param with_section_info: передавать ли с объектом данные о категории
        :return:
        """
        items = (
            self._find_and_parse_items_with_sections_info()
            if with_section_info
            else self._find_and_parse_items_without_sections_info()
        )
        yield from items
