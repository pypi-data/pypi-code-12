#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""A script to scrape items from an Amazon wishlist. The script only works for
wishlists which are "Public". You can change the settings by following the
instruction in:
http://www.amazon.com/gp/help/customer/display.html?nodeId=501094

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
from collections import namedtuple
import logging
import os
import sys
import urlparse

import requests
from lxml import html

from sorno import loggingutil
from sorno import consoleutil


_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()
_PLAIN_ERROR_LOGGER = None  # will be created in main()

Item = namedtuple('Item', 'id title url')


class App(object):
    WISHLIST_PAGE_TEMPLATE = (
        "https://www.amazon.com/gp/registry/wishlist"
        + "/{wishlist_id}/?page={page_number}"
    )
    HEADERS = {
        'user-agent': 'Mozilla/5.0 ;Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko',
    }

    def __init__(self, wishlist_id):
        self.wishlist_id = wishlist_id

    def run(self):
        # stores the id's of items
        seen_items = set()

        page_number = 1
        item_number = 1
        num_of_empty_page_reached = 0

        while True:
            items = self.get_items_from_page_num(page_number)

            rows = []
            for item in items:
                if item.id in seen_items:
                    _LOG.debug("Seen title %s, skip it", item.title)
                else:
                    seen_items.add(item.id)
                    rows.append(
                        {
                            'no.': str(item_number),
                            'title': item.title,
                            'url': item.url if item.url else "",
                        }
                    )
                    item_number += 1
                    num_of_empty_page_reached = 0

            if not rows:
                num_of_empty_page_reached += 1
                if num_of_empty_page_reached >= 3:
                    # All items are seen in the fetch, so we are done
                    # Sometimes amazon returns 0 items even we havn't reached
                    # to the end, so give it a few trials
                    break
                else:
                    continue

            data_printer = consoleutil.DataPrinter(
                rows,
                headers=('no.', 'title', 'url'),
                delimiter='\t',
                print_func=_PLAIN_LOGGER.info,
            )

            data_printer.print_result(
                style=consoleutil.DataPrinter.PRINT_STYLE_PLAIN
            )

            page_number += 1

    def get_items_from_page_num(self, num):
        url = self.WISHLIST_PAGE_TEMPLATE.format(
            wishlist_id=self.wishlist_id,
            page_number=num,
        )
        _LOG.debug("Fetch from: %s", url)

        wishlist_page = requests.get(url)
        wishlist_page_html = wishlist_page.text
        _PLAIN_ERROR_LOGGER.debug(wishlist_page_html)

        tree = html.fromstring(wishlist_page_html)
        all_h5_nodes = tree.xpath("//div[@class='a-row a-size-small']/h5")

        items = []
        for h5_node in all_h5_nodes:
            try:
                item = self._get_item_from_idea_h5_node(h5_node)
                if not item:
                    item = self._get_item_from_amazon_item_h5_node(h5_node)

                if item:
                    items.append(item)
                else:
                    _LOG.warn("Fail to retrieve an item for snippet")
                    _PLAIN_ERROR_LOGGER.warn("===== Start of snippet =====")
                    _PLAIN_ERROR_LOGGER.warn(html.tostring(h5_node))
                    _PLAIN_ERROR_LOGGER.warn("===== End of snippet =====")
            except ValueError as ex:
                _LOG.exception("Fail to retrieve an item: %s", ex)
                _PLAIN_ERROR_LOGGER.warn("===== Start of snippet =====")
                _PLAIN_ERROR_LOGGER.warn(html.tostring(h5_node))
                _PLAIN_ERROR_LOGGER.warn("===== End of snippet =====")

        return items

    def _get_item_from_idea_h5_node(self, h5_node):
        """
        Gets the item in a H5 html node that contains an Idea. Returns
        None if an Idea cannot be found.

        The H5 html node supposes to be like the following, "{param}" denotes
        the parameters of the item:

        <h5>
        ...
        <span id="itemName_{item id}">{item title}</span>
        ...
        </h5>
        """
        span_nodes = h5_node.xpath(
            ".//span[contains(@id, 'itemName_')]"
        )

        if not span_nodes:
            return None

        span_node = span_nodes[0]
        item_title = self.get_text_from_element(span_node)
        item_id = span_node.attrib['id'].split('itemName_')[1]
        return Item(id=item_id, title=item_title, url=None)

    def _get_item_from_amazon_item_h5_node(self, h5_node):
        """
        Gets the item in a H5 html node that contains an Amazon item. Returns
        None if an Amazon item cannot be found. An Amazon item is an item in
        wishlish that is sold in Amazon.

        The H5 html node supposes to be like the following, "{param}" denotes
        the parameters of the item:

        <h5>
        ...
        <a id="itemName_{item id}" href="{item url}">{item title}</a>
        ...
        </h5>
        """
        anchor_nodes = h5_node.xpath(".//a[contains(@id, 'itemName_')]")
        if anchor_nodes:
            # This is an Amazon item node
            anchor_node = anchor_nodes[0]

            item_url = "http://www.amazon.com" + anchor_node.attrib['href']
            item_title = self.get_text_from_element(anchor_node).strip()
            item_id = anchor_node.attrib['id'].split('itemName_')[1]
            return Item(id=item_id, title=item_title, url=item_url)

        return None

    def same_item_lists(self, prev_items, items):
        if prev_items is None or len(prev_items) != len(items):
            return False

        for prev, cur in zip(prev_items, items):
            prev_query = urlparse.urlparse(prev.attrib['href']).query
            cur_query = urlparse.urlparse(cur.attrib['href']).query
            if prev_query != cur_query:
                return False

        return True

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
        A script to scrape items from an Amazon wishlist. The script only
        works for wishlists which are "Public". You can change the settings by
        following the instruction in:
        http://www.amazon.com/gp/help/customer/display.html?nodeId=501094
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "wishlist_id",
        help="When you look at the URL of your wishlist, it's something like"
        + " https://www.amazon.com/gp/registry/wishlist/<wishlist id>/ref=cm_wl_list_o_0?"
        + ", so just copy the wishlist id for this argument",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER, _PLAIN_ERROR_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")
    _PLAIN_ERROR_LOGGER = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        stdout=False,
    )

    app = App(args.wishlist_id)
    app.run()


if __name__ == '__main__':
    main()
