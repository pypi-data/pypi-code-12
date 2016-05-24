class Paginator(object):
    """
    Пагинатор по страницам

    Принимает начальную страницу и парсер, который возвращает
    ссылку на следуюущую страницу.

    Пагинатор всегда возвращает начальный url (который используется для
    инициализации)
    """
    def __init__(self, url, parser):
        self.url = url
        self.parser = parser

    def __iter__(self):
        url = self.url
        yield url
        while url:
            candidate = self.parser.from_source(url)
            if candidate is None:
                raise StopIteration
            url = candidate.get('url', None)
            if url is None:
                raise StopIteration
            yield url
