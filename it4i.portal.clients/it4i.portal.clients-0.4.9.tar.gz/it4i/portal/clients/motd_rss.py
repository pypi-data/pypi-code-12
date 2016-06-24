#!/usr/bin/env python
"""
RSS parser for MOTD messages
"""

import cStringIO
import feedparser
import getopt
import os
import random
import re
import sys
import time

from bs4 import BeautifulSoup
from calendar import timegm
from chameleon.zpt.loader import TemplateLoader
from datetime import datetime
from logger import logging
from logger import CONSOLE_HANDLER
from logger import LOGGER
from textwrap import TextWrapper


class Feed(object):
    """
    feed class
    """

    def __init__(self):
        self.filtered_feed = []
        self.limit = 0
        self.page_template = None
        self.reverse = False
        self.sortkey = 'updated'
        self.sources = []
        self.width = 78

    def _parse(self):
        """
        parse available feeds
        """
        parsed_feed = []
        for source in self.sources:
            feed = feedparser.parse(source)
            if not feed.entries:
                LOGGER.warning("skipping feed: %s", source)
            for entry in feed.entries:
                try:
                    content = entry['content'][0].value
                except KeyError:
                    content = entry['summary']
                parsed_feed.append(
                    {'title': entry['title'],
                     'published': datetime.fromtimestamp(
                        timegm(entry['published_parsed'])),
                     'updated': datetime.fromtimestamp(
                        timegm(entry['updated_parsed'])),
                     'content': content})

        limit = self.limit if self.limit != 0 else len(parsed_feed)
        self.filtered_feed = sorted(parsed_feed,
                                    key=lambda item: item[self.sortkey],
                                    reverse=True)[:limit]

        # in fact, the list is already reversed
        if not self.reverse:
            self.filtered_feed.reverse()

    def render_text(self):
        """
        print text-only MOTD
        """
        output = cStringIO.StringIO()

        self._parse()
        wrapper = TextWrapper(width=self.width,
                              replace_whitespace=False,
                              break_long_words=False,
                              break_on_hyphens=False)
        for item in self.filtered_feed:
            print >> output
            for title_line in wrapper.wrap(item['title']):
                print >> output, title_line.center(self.width).encode('utf-8')
            print >> output, ('(%s)' % item['updated']).center(self.width)
            print >> output
            item['content'] = re.sub(r'(<br ?/?>){1,}',
                                     '\n',
                                     item['content'])
            soup = BeautifulSoup(item['content'], 'html.parser')
            for paragraph in soup.get_text().strip().split('\n'):
                print >> output, wrapper.fill(paragraph.strip()).encode('utf-8')
            print >> output

        return output

    def render_html(self):
        """
        print HTML-templated MOTD
        """
        output = cStringIO.StringIO()

        self._parse()
        pt_loader = TemplateLoader([os.path.dirname(self.page_template)],
                                   auto_reload=True)
        template = pt_loader.load(self.page_template)
        print >> output, template(items=self.filtered_feed).encode('utf-8')

        return output


def errmsg(msg, retval=1):
    """
    print help and exit
    """

    if not msg:
        my_name = __name__.split('.')[-1]
        print 'usage:', my_name, '-h|--help'
        print '      ', my_name, '[OPTION] ... -t|--text FEED_SOURCE ...'
        print '      ', my_name, '[OPTION] ... -t|--text -i [FEED_SOURCE ...]'
        print '      ', my_name, '[OPTION] ... \
-m <page_template>|--html=<page_template> FEED_SOURCE ...'
        print '      ', my_name, '[OPTION] ... \
-m <page_template>|--html=<page_template> -i [FEED_SOURCE ...]'
        print '''
FEED SOURCE
      o some URL
          e.g. http://example.com/atom.xml

      o some file
          e.g. /path/to/a/file.xml

      o raw XML data

OPTIONS
      -i, --stdin
          Read additional feed source from stdin

      -l <number>, --limit=<number>
          Limit number of feeds (after merge)

      -n, --cron
          Sleep from 10 up to 60 seconds prior to any actions

      -r, --reverse
          Reverse order of feeds (newest at top)

      -s <sort_key>, --sort=<sort_key>
          Sort using one of these sort keys: content, published, updated, title
          Defaults to: updated

      -v, --verbose
          Be verbose

      -w <number>, --width=<number>
          Maximum line width (intended for text rendering, default of 78 columns)
'''
    else:
        print >> sys.stderr, msg
    sys.exit(retval)


def main(argv=sys.argv[1:]):
    """
    main function
    """

    # parse opts and args
    try:
        opts, args = getopt.getopt(argv, "hil:m:nrs:tvw:", ["help",
                                                            "stdin",
                                                            "limit=",
                                                            "html=",
                                                            "cron",
                                                            "reverse",
                                                            "sort=",
                                                            "text",
                                                            "verbose",
                                                            "width="])
    except getopt.GetoptError as err:
        print str(err)
        errmsg(None)

    # initiate feed
    feedobj = Feed()

    # parse opts/args
    rendering_method = ''
    sleep = False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            errmsg(None)
        elif opt in ("-i", "--stdin"):
            feedobj.sources.append(sys.stdin.read())
        elif opt in ("-l", "--limit"):
            if not arg.isdigit():
                errmsg('number of feeds must be specified')
            feedobj.limit = int(arg)
        elif opt in ("-m", "--html"):
            rendering_method = 'render_html'
            if not os.path.isfile(arg):
                errmsg('page template \'%s\' not found' % arg)
            feedobj.page_template = arg
        elif opt in ("-n", "--cron"):
            sleep = True
        elif opt in ("-r", "--reverse"):
            feedobj.reverse = True
        elif opt in ("-s", "--sort"):
            if arg in ['content',
                       'published',
                       'updated',
                       'title']:
                feedobj.sortkey = arg
            else:
                errmsg('unknown sort key')
        elif opt in ("-t", "--text"):
            rendering_method = 'render_text'
        elif opt in ("-v", "--verbose"):
            CONSOLE_HANDLER.setLevel(logging.WARNING)
        elif opt in ("-w", "--width"):
            if not arg.isdigit():
                errmsg('number of columns must be specified')
            feedobj.width = int(arg)
    if not rendering_method:
        errmsg('rendering method must be specified')
    if not (args or feedobj.sources):
        errmsg('at least one feed source must be specified')

    # feed machinery
    if sleep:
        time.sleep(random.randint(10, 60))
    feedobj.sources.extend(args)
    output = getattr(feedobj, rendering_method)()
    print output.getvalue()
    output.close()


if __name__ == "__main__":
    main()
