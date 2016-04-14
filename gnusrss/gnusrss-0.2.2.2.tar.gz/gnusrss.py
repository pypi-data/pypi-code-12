#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import urllib.parse
import pycurl
import os.path
import sqlite3
import feedparser
import argparse
import hashlib
import time
from os import listdir
from sys import argv
from xml.dom import minidom
from io import BytesIO
from html.parser import HTMLParser
from re import findall
from sys import exit


class Database:
    """Manage the database."""
    def __init__(self, database='gnusrss.db'):
        """
        Connect to the database.

        database -- string containig the filepath of the db
            (default: gnusrss.db)
        """

        self.connection = sqlite3.connect(database)

    def create_tables(self):
        """Create table and columns."""

        current = self.connection.cursor()
        current.execute('DROP TABLE IF EXISTS items')
        current.execute('CREATE TABLE items(id INTEGER PRIMARY KEY,'
                        'feed TEXT, post TEXT, posted INTEGER, url '
                        'TEXT, lastbuild TIMESTAMP, guid TEXT)')

    def insert_data(self, param):
        """
        Insert all the article's information to the table.

        Keyword arguments:
        param -- list containing all the values
        """
        self.connection.execute('INSERT INTO items(feed, post, posted'
                                ', url, lastbuild, guid) VALUES(?, ?,'
                                '?, ?, ?, ?)', (param))
        self.connection.commit()

    def select(self, param):
        """
        Return a select.

        Keyword arguments:
        param -- string containing a sql select
        """

        current = self.connection.cursor()
        current.execute(param)
        rows = current.fetchall()

        return rows

    def close(self):
        """Close the database."""
        self.connection.close()


class StupidParser(HTMLParser):
    """Just a HTML parser."""
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.data = []

    def handle_data(self, data):
        self.data.append(data)

    def return_value(self):
        return ''.join(self.data)


class GNUsrss:
    def parse_feed(self, feed, post_format):
        """
        Request the feed, parse it and return requested values on a list
        of lists.

        Keyword arguments:
        feed -- string containing the url or the filepath of the feed
        post_format -- string containing RSS keywords surrounded by {}

        Comment:
        Here it's saved way more tags that aren't necessary. They're added just
        to add more metadata just because it's clearer when viewing the sqlite.
        """

        article = []
        xml = feedparser.parse(feed)
        entries_keys = list(xml.entries[0].keys())
        feed_keys = list(xml.feed.keys())

        # Very ugly way to test existence, but seems to be the only way
        if 'published' in entries_keys:
            lastbuild = xml.entries[0].published
        elif 'published' in feed_keys:
            lastbuild = xml.feed.published
        elif 'updated' in entries_keys:
            lastbuild = xml.entries[0].updated
        elif 'updated' in feed_keys:
            lastbuild = xml.feed.updated
        else:
            # Since the feed doesn't have a date, I'll create it
            lastbuild = time.strftime("%a, %d %b %Y %H:%M:%S GMT")

        if 'link' in feed_keys:
            rss_link = xml.feed.link
        else:
            rss_link = 'http://' + xml.entries[0].link.split('/')[2]

        for item in xml['items']:
            values = {}
            for i in entries_keys:
                if i in post_format:
                    values[i] = item[i]
            post = post_format.format(**values)

            # Stupid HTML code adding to complete the post to parse it
            post = '<html>' + post + '</html>'
            parser = StupidParser()
            parser.feed(post)
            post = parser.return_value()

            if 'guid' in entries_keys:
                guid = item['guid']
            else:
                # Since the feed doesn't have a guid, I'll create it
                guid = hashlib.sha1(post.encode()).hexdigest()

            article.append([rss_link, post, item['link'], lastbuild, guid])

        return article

    def post(self, article, gs_node, username, password, insecure):
        """
        Post the articles to GNU Social.

        Keyword arguments:
        article -- list containing a most of what is necessary on the insert
        gs_node -- string containing the url of the GNU Social node
        username -- string containing the user of GNU Social
        password -- string containing the password of GNU Social
        """

        msg = article[1].split()
        api = (gs_node + '/api/statuses/update.xml')

        # Check for twitter images and call post_image if required
        for word in msg:
            if 'pic.twitter.com/' in word:
                image = self.post_image(word, gs_node, username, password, insecure)
                if image is not None:
                    index = msg.index(word)
                    msg[index] = image
                else:
                    pass

        msg = ' '.join(msg)

        buffer = BytesIO()
        post_data = {'status': msg, 'source': 'gnusrss'}
        postfields = urllib.parse.urlencode(post_data)

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, api)
        curl.setopt(pycurl.USERPWD, username + ':' + password)
        curl.setopt(pycurl.VERBOSE, False)
        curl.setopt(curl.POSTFIELDS, postfields)
        curl.setopt(pycurl.WRITEDATA, buffer)

        if insecure == 'yes':
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        curl.perform()
        curl.close

        response = curl.getinfo(curl.RESPONSE_CODE)

        return response

    def post_image(self, picture, gs_node, username, password, insecure):
        """
        Upload a picture to GNU Social hosting and return a string with the
        new url.

        Keyword arguments:
        picture -- string containing the twitter url of a picture
        gs_node -- string containing the url of the GNU Social node
        username -- string containing the user of GNU Social
        password -- string containing the password of GNU Social
        """

        pic = ""
        found = False
        api = gs_node + '/api/statusnet/media/upload'

        # If the picture doesn't exist or is not well written, show must go on
        try:
            html = urllib.request.urlopen('https://' + picture).read().decode(
                'utf-8').splitlines()
        except:
            return picture

        # Search the hardcoded tag name of the picture
        for part in html:
            if 'data-image-url' in part : #and found:
                pic = part.split('"')[1]
                break

        # If there's a video instead of a picture, just exit
        if not pic:
            return None

        # Pick the image and put it in the buffer
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, pic)
        curl.setopt(pycurl.VERBOSE, False)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.perform()

        pic = buffer.getvalue()
        buffer = BytesIO()

        if insecure == 'yes':
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        # Upload the buffer's image
        curl.setopt(pycurl.URL, api)
        curl.setopt(pycurl.USERPWD, username + ':' + password)
        curl.setopt(curl.HTTPPOST,[('media', (curl.FORM_BUFFER, 'useless.jpg',
                                            curl.FORM_BUFFERPTR, pic))])
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.perform()
        curl.close()

        buffer = buffer.getvalue().decode()
        xmldoc = minidom.parseString(buffer)
        item = xmldoc.getElementsByTagName('rsp')
        url = item.item(0).getElementsByTagName('mediaurl')[0].firstChild.data

        return url

    def compare(self, feeds):
        """
        Compare the picked feed to the saved on the database and return
        list of lists if new.

        Keyword argument:
        feeds -- list of lists containing all actual feeds on the RSS file
        """

        db = Database()
        old = db.select('select guid from items;')
        new_feed = []
        posted = []

        # make the list accesible
        for x in old:
            posted.append(x[0])

        for feed in feeds:
            if feed[4] not in posted:
                new_feed.append(feed)

        db.close()
        return new_feed

    def shortener(self, post):
        """
        Return a shortened url.

        Keyword argument:
        post -- string containing a url to be shortened
        """

        api = ('http://qttr.at/yourls-api.php?format=xml&action=shorturl'
                   '&signature=b6afeec983&url=' + post)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, api)
        curl.setopt(pycurl.VERBOSE, False)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.perform()

        buffer = buffer.getvalue().decode('utf-8')

        xmldoc = minidom.parseString(buffer)
        item = xmldoc.getElementsByTagName('result')
        url = item.item(0).getElementsByTagName('shorturl')[0].firstChild.data

        return url

    def shorten_all(self, post):
        """
        Short all the urls from a notice.

        Keyword arguments:
        post - list containing all the data related to the post to GS
        """

        # Regex taken from stackoverflow, thanks guys
        # It doesn't identify pic.twitter.com url, which is good
        urls = findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&~#=+]|[!*\(\),]'
                           '|(?:%[0-9a-fA-F][0-9a-fA-F]))+', post[1])

        separate = post[1].split(' ')
        # Clean shitty carriage return
        tmp = ''
        for i in separate:
            i = i.replace(u'\xa0', u'') + ' '
            i = i.replace('\n', ' ')
            tmp += i

        separate = tmp.split(' ')

        for i in urls:
            shortened = self.shortener(i)
            position = separate.index(i)
            separate[position] = shortened

        post[1] = ' '.join(separate)

        return post


class Config:
    def create(self, config_name):
        """
        Create config file.

        Keyword argument:
        config_name -- string containing the config's name to be created
        """

        print('Hi! Now we\'ll create de config file!')
        feed = input('Please introduce the feed\'s url: ')
        username = input('Please introduce your username '
                             '(user@server.com): ')
        password = input('Please introduce your password: ')
        shorten = input('Do you need to shorten the urls that you '
                            'post? Please take in account \nthat you '
                            'should only use it if your node only has 140'
                            ' characters. \nAnswer with "yes" or just press '
                            'enter if you don\'t want to use it: ')
        fallback_feed = input('Please introduce your feed\'s fallback'
                                  'url. If you don\'t want or have one,\n'
                                  'just press enter: ')
        print('Now we\'re going to fetch the feed. Please wait...')
        feed_file = feedparser.parse(feed)
        keys = list(feed_file.entries[0].keys())
        print('Done! The tags are: ')
        for tag in keys:
            print('\t' + tag)
        post_format = input('The XML has been parsed. Choose wich '
                            'format you want:\nPlease put the tags '
                            'inside the square brackets\nEx: {title}'
                            ' - {link} by @{author}: ')
        insecure = input('Do you want to allow insecure connection to your GNU '
                             'social server?\nAnswer with "yes" or just press '
                             'enter if you don\'t want to use it: ')

        config = configparser.ConfigParser()
        config['feeds'] = {}
        config['feeds']['feed'] = feed
        config['feeds']['user'] = username
        config['feeds']['password'] = password
        config['feeds']['shorten'] = shorten
        config['feeds']['fallback_feed'] = fallback_feed
        config['feeds']['format'] = post_format
        config['feeds']['insecure'] = insecure

        with open(config_name + '.ini', 'w') as configfile:
            config.write(configfile)

    def get(self, name):
        """
        Parse config file and return it on a list.

        Keyword arguments:
        name -- string containing the config's name
        """

        config = []
        parser = configparser.SafeConfigParser()
        parser.read(name)

        for name, value in parser.items('feeds'):
            config.append(value)

        return config


class ParseOptions():
    """Parse command line options of this program."""
    def __init__(self):
        parser = argparse.ArgumentParser(description='Post feeds to GNU '
                                             'Social', prog='gnusrss')
        parser.add_argument('-c', '--create-config', metavar='file_name',
                            dest='create_config', help='creates a config file')
        parser.add_argument('-C', '--create-db', dest='create_database',
                            action='store_true', help='creates the database')
        parser.add_argument('-p', '--post', metavar='config_file',
                            dest='post', help='posts feeds')
        parser.add_argument('-P', '--post-all', dest='post_all',
                            action='store_true', help='posts all feeds')
        parser.add_argument('-k', '--populate-database', metavar='file_name',
                            dest='populate_database', help='fetch the RSS and'
                            ' save it in the database')
        parser.add_argument('-v', '--version', dest='version',
                            action='store_true', help='show version in the '
                            'database')

        self.db = Database()
        self.gs = GNUsrss()
        self.cnf = Config()

        self.args = parser.parse_args()
        # Make all options accesible within self
        self.create_database = self.args.create_database
        self.create_config = self.args.create_config
        self.post = self.args.post
        self.post_all = self.args.post_all
        self.populate_database = self.args.populate_database
        self.version = self.args.version
        self.parser = parser

    def declare_config(self):
        """Assign all config parameters to a self object."""

        config = self.cnf.get(self.config_name)
        self.feed = config[0]
        self.user = config[1].split('@')[0]
        self.password = config[2]
        self.shorten = config[3]
        self.fallback_feed = config[4]
        self.format = config[5]
        # Always use SSL
        self.server = 'https://' + config[1].split('@')[1]
        # Test since in versions previous to 0.2.2 didn't exist
        try:
            self.insecure = config[6]
        except:
            self.insecure = ''

    def post_notice(self):
        """Post notice to GNU social."""

        file_name = self.config_name

        # If first feed and fallback feed aren't available, fail gracefully
        try:
            posts = self.gs.parse_feed(self.feed, self.format)
        except:
            if self.fallback_feed:
                posts = self.gs.parse_feed(self.fallback_feed, self.format)
            else:
                print('There\'s been a problem with ' + file_name + ' file.')
                return None

        posts = list(reversed(posts))
        new = self.gs.compare(posts)

        if new:
            # Post only the older item
            self.to_post = new[0]
            if self.shorten == 'yes':
                self.to_post = self.gs.shorten_all(self.to_post)

            if not self.populate_database:
                code = self.gs.post(self.to_post, self.server, self.user,
                                        self.password, self.insecure)

                self.save_in_database(code)


    def save_in_database(self, code):
        """
        Save posts in database

        Keyword arguments:
        code -- HTML code of the notice's post to GNU social
        """

        if self.create_config or self.populate_database or int(code) == \
                int(200):
            self.db.insert_data([self.to_post[0], self.to_post[1], 1,
                                     self.to_post[2], self.to_post[3],
                                     self.to_post[4]])
        elif code == 400:
            print('The notice couldn\'t be posted')

    def pointers(self):
        """This are the options of the program."""

        if self.version:
            print("v0.2.2.2")
            exit()
        if self.create_database:
            if os.path.exists('gnusrss.db'):
                overwrite = input('The database already exists. Are you '
                                'sure you want to overwrite it? (y/n) ')

                if overwrite == 'y':
                    self.db.create_tables()
            else:
                self.db.create_tables()

            if not self.create_config and not self.populate_database and \
                    not self.post and not self.post_all:
                self.db.close()

        if self.create_config:
            self.config_name = self.create_config + '.ini'
            self.cnf.create(self.create_config)

            populate = input('Do you want to populate the database? (y) Or you'
                                 ' prefer to post old items? (n) ')

            if populate == 'y':
                self.declare_config()
                posts = self.gs.parse_feed(self.feed, self.format)

                for post in posts:
                    self.to_post = post
                    self.save_in_database(0)
                self.db.close()

        elif self.post:
            self.config_name = self.post
            self.declare_config()
            self.post_notice()
            self.db.close()

        elif self.post_all:
            for config in listdir('.'):
                if config.endswith('.ini'):
                    self.config_name = config
                    self.declare_config()
                    self.post_notice()
            self.db.close()

        elif self.populate_database:
            self.config_name = self.populate_database
            self.declare_config()
            posts = self.gs.parse_feed(self.feed, self.format)

            for post in posts:
                self.to_post = post
                self.save_in_database(0)

            self.db.close()

        elif len(argv) == 1:
             self.parser.print_help()


if __name__ == "__main__":
    options = ParseOptions()
    options.pointers()
