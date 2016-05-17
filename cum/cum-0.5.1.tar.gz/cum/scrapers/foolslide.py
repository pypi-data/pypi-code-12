from abc import ABCMeta, abstractmethod
from cum import config, exceptions
from cum.scrapers.base import BaseChapter, BaseSeries
from mimetypes import guess_extension
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin, urlparse
import re
import requests


class FoOlSlideSeries(BaseSeries, metaclass=ABCMeta):
    def __init__(self, url, directory=None):
        self.url = url
        self.directory = directory
        self.get_comic_details()
        self.chapters = self.get_chapters()

    @property
    def api_hook_comic_details(self):
        path = 'api/reader/comic/id/{}'.format(self.foolslide_id)
        return urljoin(self.BASE_URL, path)

    @staticmethod
    def api_hook_comic_list(page):
        path = 'api/reader/comics/page/{}'.format(page)
        return urljoin(self.BASE_URL, path)

    @property
    @abstractmethod
    def BASE_URL(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def CHAPTER_OBJECT(self):
        raise NotImplementedError()

    def from_chapter_id(self):
        pass

    def get_comic_details(self):
        page = 1
        path = urlparse(self.url).path
        while True:
            response = requests.get(self.api_hook_comic_list(page)).json()
            if response.get('error', None) == 'Comics could not be found':
                break
            for comic in response['comics']:
                if urlparse(comic['href']).path == path:
                    self.foolslide_id = comic['id']
                    self.name = comic['name']
                    return
            page += 1

    def get_chapters(self):
        response = requests.get(self.api_hook_comic_details).json()
        chapters = []
        for chapter in response['chapters']:
            kwargs = {
                'name': self.name,
                'alias': self.alias,
                'chapter': chapter['chapter']['chapter'],
                'api_key': chapter['chapter']['id'],
                'url': chapter['chapter']['href'],
                'title': chapter['chapter']['name'],
                'groups': [team['name'] for team in chapter['teams']]
            }
            chapter = self.CHAPTER_OBJECT(**kwargs)
            chapters.append(chapter)
        return chapters

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class FoOlSlideChapter(BaseChapter, metaclass=ABCMeta):
    uses_pages = True
    chapter_id_re = re.compile(r'"chapter_id":"([0-9]*)"')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = kwargs.get('api_key')

    @staticmethod
    def api_hook_chapter_details(api_key):
        path = 'api/reader/chapter/id/{}'.format(api_key)
        return urljoin(self.BASE_URL, path)

    def download(self):
        response = (requests.get(self.api_hook_chapter_details(self.api_key))
                            .json())
        pages = response['pages']
        files = []
        with self.progress_bar(pages) as bar:
            for page in pages:
                r = requests.get(page['url'], stream=True)
                ext = guess_extension(r.headers.get('content-type'))
                f = NamedTemporaryFile(suffix=ext)
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                f.flush()
                files.append(f)
                bar.update(1)
        self.create_zip(files)

    def from_url(url):
        r = requests.get(url)
        chapter_id = re.search(chapter_id_re, r.text).group(1)
        endpoint = FoOlSlideChapter.api_hook_chapter_details(chapter_id)
        response = requests.get(endpoint).json()
        # response[]
