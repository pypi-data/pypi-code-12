from cum.scrapers.foolslide import FoOlSlideChapter, FoOlSlideSeries
import re

BASE_URL = "http://www.yuri-ism.net/slide/"


class YuriismChapter(FoOlSlideChapter):
    BASE_URL = BASE_URL
    url_re = re.compile(r'http://www\.yuri-ism\.net/slide/read/')


class YuriismSeries(FoOlSlideSeries):
    BASE_URL = BASE_URL
    CHAPTER_OBJECT = YuriismChapter
    url_re = re.compile(r'http://www\.yuri-ism\.net/slide/series/')
