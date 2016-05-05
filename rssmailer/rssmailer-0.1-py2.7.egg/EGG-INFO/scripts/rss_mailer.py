#!/home/arunsrin/packages/py/bin/python
import feedparser
from rssmailer.feed import Feed
from rssmailer.mail import MailGun
from twisted.web import client
from twisted.internet import reactor, defer
import os
import json
import logging
import sys

# import logging
# import sys
# log = logging.getLogger('rss_mailer')
# out_hdlr = logging.StreamHandler(sys.stdout)
# log.addHandler(out_hdlr)
# log.setLevel(logging.DEBUG)

# bah, utf-8
reload(sys)
sys.setdefaultencoding('utf-8')


def get_url(url):
    log.info('Fetching URL: {}'.format(url))
    d = client.getPage(url)
    d.addCallback(_cb_fetch_finish)
    d.addErrback(_cb_fetch_failure)
    return d


def _cb_fetch_finish(result):
    parsed = feedparser.parse(result)
    log.info('Got feed content for {}'.format(parsed['feed']['title']))
    return parsed


def _cb_fetch_failure(result):
    log.error('Error fetching feed: {}'.format(result))
    return None


def instantiate_feeds(result):
    feed_objs = []
    for current_feed in result:
        if current_feed:
            f = Feed(current_feed)
            f.get_latest_posts()
            feed_objs.append(f)
    return feed_objs


def send_mail(result):
    api_key = str(CONFIG['api_key'])
    mailgun_url = str(CONFIG['mailgun_url'])
    mail_to = str(CONFIG['mail_to'])
    mail_from = str(CONFIG['mail_from'])

    for entry in result:
        title = entry.title
        content = entry.entries_to_mail
        if not content:
            break
        log.info('Sending email for {}'.format(title))
        m = MailGun(api_key, mailgun_url, mail_to, mail_from, title, content)
        m.build_html_message()
        m.send_complex_message()
    reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)


    # parse the config file, abort if not found
    CONFIG_FILE = os.path.expanduser('~/.rssmailer.json')
    try:
        f = open(CONFIG_FILE, 'r')
    except IOError:
        log.error('Please set up ~/.rssmailer.json and retry..')
        raise SystemExit
    try:
        CONFIG = json.load(f)
    except ValueError:
        log.error('Error parsing ~/.rssmailer.json. Please correct and retry.')
        raise SystemExit

    log.info('CONFIG is {}'.format(CONFIG))
    fetched_feeds = []
    feeds = CONFIG['feeds']
    for feed in feeds:
        fetched_feeds.append(get_url(str(feed)))
    d = defer.gatherResults(fetched_feeds, consumeErrors=True)

    # create a list of Feed objects with this content
    d.addCallback(instantiate_feeds)

    # send mail for each
    d.addCallback(send_mail)

    reactor.run()
