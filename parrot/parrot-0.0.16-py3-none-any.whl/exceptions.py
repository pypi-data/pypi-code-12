from parrot.utils import tree_to_str


class CrawlerException(Exception):
    pass


class ParserException(Exception):
    pass


class SelectorException(Exception):
    pass


class FormatterException(Exception):
    pass


class SerializerException(Exception):
    pass


class StorageException(Exception):
    pass


class LoaderException(Exception):
    pass


class ExporterException(Exception):
    pass


class ParserFetchingDataException(ParserException):
    def __init__(self, source, exc, tb):
        super().__init__()
        self.source = source
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Fetching data from source {} raise exception: {}. '
            'Traceback: {}.'
        ).format(self.source, self.exc, self.tb)


class InvalidData(ParserException):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def __str__(self):
        return 'Invalid data: {}'.format(repr(self.data))


class InvalidDataFromSource(InvalidData):
    def __init__(self, data, source):
        super().__init__(data)
        self.source = source

    def __str__(self):
        return 'Invalid data from source: {}. Data: {}'.format(
            self.source, repr(self.data)
        )


class EmptyValue(ParserException):
    def __init__(self, val):
        super().__init__()
        self.val = val

    def __str__(self):
        return 'Value "{}" is empty'.format(repr(self.val))


class InvalidValue(ParserException):
    def __init__(self, val):
        super().__init__()
        self.val = val

    def __str__(self):
        return 'Invalid value: "{}"'.format(repr(self.val))


class InvalidValueFromSource(InvalidValue):
    def __init__(self, val, source):
        super().__init__(val)
        self.source = source

    def __str__(self):
        return super().__str__() + ' from source: {}'.format(self.source)


class SelectorNotFound(SelectorException):
    def __init__(self, selectors_set, selector_name):
        super().__init__()
        self.selectors_set = selectors_set
        self.selector_name = selector_name

    def __str__(self):
        return 'Selector "{}" is not found. Available selectors: {}'.format(
            self.selector_name, self.selectors_set
        )


class SelectorSearchException(SelectorException):
    def __init__(self, selector, data_or_tree, exc, tb):
        super().__init__()
        self.selector = selector
        self.data = tree_to_str(data_or_tree)
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Selector "{}" search raise exception: {}. '
            'Data: {}. Traceback: {}.'
        ).format(self.selector, self.exc, repr(self.data), self.tb)


class SelectorEmptyResult(SelectorException):
    def __init__(self, selector, data_or_tree):
        super().__init__()
        self.selector = selector
        self.data = tree_to_str(data_or_tree)

    def __str__(self):
        return 'Empty selector "{}" results. Data: {}'.format(
            self.selector, repr(self.data)
        )


class BadFormatterValue(FormatterException):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

    def __str__(self):
        return 'Bad "{}" value: "{}"'.format(self.name, repr(self.value))


class FormatterFormatException(FormatterException):
    def __init__(self, val, exc, tb):
        super().__init__()
        self.val = val
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Format value "{}" raise exception: {}. Traceback: {}.'
        ).format(self.val, self.exc, self.tb)


class CrawlerEmptySectionsUrls(CrawlerException):
    def __init__(
        self, sections_init_url, sections_urls, with_paginate
    ):
        super().__init__()
        self.sections_init_url = sections_init_url
        self.sections_urls = sections_urls
        self.with_paginate = with_paginate

    def __str__(self):
        return (
            'Empty sections urls list "{}". '
            'Sections init url: {}. With paginate: {}.'
        ).format(
            self.sections_urls, self.sections_init_url,
            self.with_paginate
        )


class CrawlerEmptySection(CrawlerException):
    def __init__(self, section_url, section_items):
        super().__init__()
        self.section_url = section_url
        self.section_items = section_items

    def __str__(self):
        return (
            'Empty section "{}". Section items: {}'
        ).format(self.section_url, self.section_items)


class SerializerBadValue(SerializerException):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return 'Bad {} value: {}'.format(self.VALUE_TYPE_NAME, self.value)


class SerializerBadValueFromSource(SerializerBadValue):
    def __init__(self, value, source):
        super().__init__(value)
        self.source = source

    def __str__(self):
        return super().__str__() + ' from source: {}'.format(self.source)


class SerializerItemBadValue(SerializerBadValue):
    VALUE_TYPE_NAME = 'item'


class SerializerItemBadValueFromSource(
    SerializerBadValueFromSource, SerializerItemBadValue
):
    pass


class SerializerSectionBadValue(SerializerBadValue):
    VALUE_TYPE_NAME = 'section'


class SerializerSectionBadValueFromSource(
    SerializerBadValueFromSource, SerializerSectionBadValue
):
    pass


class SerializerSerializingException(SerializerException):
    def __init__(self, item, exc, tb):
        super().__init__()
        self.item = item
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Serializing object "{}" raised exception: "{}". '
            'Traceback: {}.'
        ).format(self.item, self.exc, self.tb)


class SerializerLoaderFromUrlException(SerializerException):
    def __init__(self, url, exc, tb):
        super().__init__()
        self.url = url
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Loading data from url "{}" raised exception: {}. '
            'Traceback: {}.'
        ).format(self.url, self.exc, self.tb)


class PeeweeStorageException(StorageException):
    def __init__(self, model):
        super().__init__()
        self.model = model


class PeeweeStorageObjectException(PeeweeStorageException):
    def __init__(self, model, obj):
        super().__init__(model)
        self.obj = obj


class PeeweeStorageSavedObjectIsNotDict(PeeweeStorageObjectException):
    def __str__(self):
        return (
            'Saved object is not dict: "{}". '
            'Model {}.'
        ).format(repr(self.obj), self.model)


class PeeweeStorageCreatingException(PeeweeStorageObjectException):
    def __init__(self, model, obj, exc, tb):
        super().__init__(model, obj)
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Creating object "{}" raised exception: "{}". '
            'Model {}. Traceback: {}.'
        ).format(repr(self.obj), self.exc, self.model, self.tb)


class PeeweeStorageUpdatingException(PeeweeStorageObjectException):
    def __init__(self, model, obj, peewee_obj, exc, tb):
        super().__init__(model, obj)
        self.peewee_obj = peewee_obj
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Updating object "{}" raised exception: "{}". '
            'Model {}. Peewee object: {}. Traceback: {}.'
        ).format(
            repr(self.obj), self.exc, self.model, repr(self.peewee_obj),
            self.tb
        )


class PeeweeStorageQueryByLabelException(PeeweeStorageException):
    def __init__(self, model, label, exc, tb):
        super().__init__(model)
        self.label = label
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            '{} by label "{}" raised exception: "{}". '
            'Model {}. Traceback: {}.'
        ).format(
            self.QUERY_TYPE, self.label, self.exc, self.model, self.tb
        )


class PeeweeStorageSelectByLabelException(
    PeeweeStorageQueryByLabelException
):
    QUERY_TYPE = 'Select'


class PeeweeStorageDeleteByLabelException(
    PeeweeStorageQueryByLabelException
):
    QUERY_TYPE = 'Delete'


class LoaderLoadException(LoaderException):
    def __init__(self, url, exc, tb):
        super().__init__()
        self.url = url
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Loading data from url {} raise exception: {}. '
            'Traceback: {}.'
        ).format(self.url, self.exc, self.tb)


class UrllibLoaderException(LoaderException):
    pass


class UrllibLoaderLoadException(UrllibLoaderException, LoaderLoadException):
    pass


class SeleniumLoaderException(LoaderException):
    pass


class SeleniumLoaderLoadException(
    SeleniumLoaderException, LoaderLoadException
):
    pass


class SeleniumLoaderInvalidCookiesException(SeleniumLoaderException):
    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies


class SeleniumLoaderCookiesDifferentDomainsException(
    SeleniumLoaderInvalidCookiesException
):
    def __str__(self):
        return (
            'Cookies must have the same domains. Current cookies: {}.'
        ).format(self.cookies)


class ExporterInitFunctionCallException(ExporterException):
    def __init__(self, func, exc, tb):
        super().__init__()
        self.func = func
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Exporter init function call "{}" raise exception: {}. '
            'Traceback: {}.'
        ).format(repr(self.func), repr(self.exc), self.tb)


class CSVExporterItemExportException(ExporterException):
    def __init__(self, item, output_fn, exc, tb):
        super().__init__()
        self.item = item
        self.output_fn = output_fn
        self.exc = exc
        self.tb = tb

    def __str__(self):
        return (
            'Export item "{}" to file "{}" raise exception "{}". '
            'Traceback: {}.'
        ).format(self.item, self.output_fn, repr(self.exc), self.tb)
