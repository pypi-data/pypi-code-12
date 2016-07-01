#!usr/bin/env python
"""

Usage:
    pnpm [-s | -d] <keywords>

Options:
    -h --help  显示帮助菜单
    -keywords  关键字
    -s         按star数排序
    -d         按下载量排序

Examples:
    pnpm lazyloading
    pnpm jquery-lazyloading
"""
from docopt import docopt
from npm_helper import BASE_URL, TABLE_HEADER, TABLE_ROW
from prettytable import PrettyTable
from spider_threads.entry import ThreadCreator
from spider_threads.utils import message
from .spiders.spider_list import NpmSearchSpider
from .spiders.spider_page import NpmPageSpider
from .data import database_creator


def get_keywords():
    arguments = docopt(__doc__, version="beta 0.1")
    keywords = arguments['<keywords>'].split('-')
    urls_generation(keywords)


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
    print_table()


def print_table():
    database = database_creator()
    npm_table = PrettyTable(TABLE_HEADER)
    for index, package in enumerate(database.data):
        package["index"] = index
        package_row = [package[item] for item in TABLE_ROW]
        npm_table.add_row(package_row)
    print(npm_table)
