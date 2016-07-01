#!usr/bin/env python

from . import BASE_URL
from spider_threads.entry import ThreadCreator
from spider_threads.utils import message
from .spiders.spider_list import NpmSearchSpider
from .spiders.spider_page import NpmPageSpider
from .data import database_creator


def get_keywords(keywords):
    urls_generation(keywords.split('-'))


def urls_generation(keywords):
    try:
        assert type(keywords) is list
        urls = [BASE_URL.format(query='+'.join(keywords), page=i) for i in range(1, 2)]
        thread_generation(urls)
    except AssertionError:
        message.error_message('except to receive a list')


def thread_generation(urls):
    threads = ThreadCreator(main_spider=NpmSearchSpider, branch_spider=NpmPageSpider)
    threads.get_entry_urls(urls)
    threads.finish_all_threads()


def get_data():
    database = database_creator()
    return database.data

