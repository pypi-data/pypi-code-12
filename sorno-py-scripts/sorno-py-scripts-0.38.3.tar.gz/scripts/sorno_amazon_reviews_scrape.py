#!/usr/bin/env python
"""A script to scrape Amazon product reviews from the web page.


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import logging
import os
import random
import sys
import time
import urllib
import urlparse

import requests
from lxml import html

from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()


class App(object):
    HEADERS = {
        'user-agent': 'Mozilla/5.0 ;Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko',
    }

    def __init__(self, url, stop_at=-1):
        self.url = url
        self.stop_at = stop_at

    def run(self):
        _log.info("Given url: %s", self.url)
        url, cur_page_num = self.get_main_url_and_page_number(self.url)
        _log.info("Main url: %s", url)

        if self.stop_at > 0 and self.stop_at < cur_page_num:
            _log.info("Not fetching page number %s", cur_page_num)
            return

        _log.info("Fetch page %d", cur_page_num)
        initial_page_tree = self.get_tree_from_url(url)

        prev_page_items = None
        cur_page_items = self.get_items_from_page_tree(initial_page_tree)
        all_items = list(cur_page_items)

        while prev_page_items != cur_page_items:
            # sleep a little bit to avoid being characterized as a bot
            time.sleep(random.uniform(0.5, 2))

            prev_page_items = cur_page_items
            cur_page_num += 1
            if self.stop_at > 0 and self.stop_at < cur_page_num:
                _log.info("Not fetching page number %s", cur_page_num)
                break

            new_url = url + "?pageNumber=" + str(cur_page_num)

            _log.info("Fetch page %s", cur_page_num)
            cur_page_items = self.get_items_from_page_tree(
                self.get_tree_from_url(new_url)
            )
            _log.debug("%s items fetched", len(cur_page_items))

            all_items.extend(cur_page_items)

        for item in all_items:
            review_content = item['review']
            print(review_content.encode('utf8'))
            print("-" * 70)

    def get_main_url_and_page_number(self, url):
        """Get the product reviews page url and the starting page number.

        Args:
            url (str): The url for the product either the product page or the
                product reviews page.

        Returns:
            Returns the product reviews page url and the starting page number.
            This method will try to get the product reviews page, without all
            the junk queries.
        """
        url = self._ensure_product_reviews_url(url)

        n = 1
        parsed = urlparse.urlparse(url)

        query = parsed.query
        query_list = urlparse.parse_qsl(query)
        # capture the pageNumber in query, and leave other as is
        for k, v in query_list:
            if k == "pageNumber":
                n = int(v)

        modified_parsed = urlparse.ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=parsed.path,
            params=parsed.params,
            # not setting the query since it's really not needed"
            query=None,
            fragment=parsed.fragment,
        )
        return modified_parsed.geturl(), n

    def _ensure_product_reviews_url(self, url):
        """Ensures the url is a product reviews page.

        The url maybe referring to the product page not the reviews, so we
        need to get the product reviews page if necessary.
        """
        if "/product-reviews/" in url:
            return url
        else:
            _log.info(
                "It's not a \"All customer reviews\" url, will try to fetch" +
                    " the correct one"
            )
            tree = self.get_tree_from_url(url)
            reviews_anchors = tree.xpath(
                "//*[@id='revF']/div/a[contains(@href, '/product-reviews/')]"
            )
            product_reviews_url = None
            for anchor in reviews_anchors:
                _log.info(
                    "Potential product reviews url: %s",
                    anchor.attrib['href'],
                )
                if not product_reviews_url:
                    product_reviews_url = anchor.attrib['href']

            url_query = urlparse.urlparse(product_reviews_url).query
            if not url_query:
                product_reviews_url += "?pageNumber=1"

            return product_reviews_url

    def get_tree_from_url(self, url):
        _log.debug("Fetch from url [%s]", url)
        website_text = requests.get(url, headers=self.HEADERS).text
        return html.fromstring(website_text)

    def get_items_from_page_tree(self, tree):
        """Get all review items for the page

        Args:
            tree: The page's dom tree.

        Returns:
            A list of items. Each item is a dictionary with the following
            fields (each key is a str):
                review (str): the review content
        """
        review_elements = self.get_reviews_from_node(tree)

        reviews = []
        for review_element in review_elements:
            review = {}
            review['review'] = self.get_text_from_element(review_element)
            reviews.append(review)
        return reviews

    def get_reviews_from_node(self, node):
        reviews = node.xpath("//span[@class='a-size-base review-text']")
        return reviews

    def get_text_from_element(self, node):
        """
        Return a plain text representation of an html node.
        """
        text_segments = []
        self._collect_text_from_element(node, text_segments)
        return "".join(text_segments)

    def _collect_text_from_element(self, node, text_segments):
        """
        Collect text from node and all its children recursively and put into
        text_segments as a list of strings.
        """
        if node.tag.lower() == "br":
            text_segments.append(os.linesep)

        if node.text:
            text_segments.append(node.text)

        for child in node:
            self._collect_text_from_element(child, text_segments)

        if node.tail:
            text_segments.append(node.tail)


def parse_args(cmd_args):
    description = """
A script to scrape Amazon product reviews
    """
    parser = argparse.ArgumentParser(
        description=description,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--stop-at",
        type=int,
        default=-1,
        help="Stop fetching more reviews at this page",
    )
    parser.add_argument(
        "url",
        help="The url that point to all reviews of an Amazon product. You"
            + " probably want to single-quote the url when running this"
            + " script in the command line because the url probably contains"
            + " shell characters. An example of a url is:"
            + " http://www.amazon.com/Ito-En-Beverage-Unsweetened-Bottles/product-reviews/B0017T2MWW/ref=cm_cr_dp_see_all_summary?ie=UTF8&showViewpoints=1&sortBy=byRankDescending",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger("PLAIN")

    app = App(args.url, stop_at=args.stop_at)
    app.run()


if __name__ == '__main__':
    main()
