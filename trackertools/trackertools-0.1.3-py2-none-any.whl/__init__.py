#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import mechanize
import cookielib
import os
import json
import requests
import pprint
import logging
import sys
import lxml.html as lh
import subprocess
import re
import string
import helpers
import urlparse
# Monkeypatch httplib to fix file upload unicode issues
# https://bugs.python.org/file21747/python-2.7.1-fix-httplib-UnicodeDecodeError.patch
from httplib import HTTPConnection
def _send_output(self, message_body=None):
    """Send the currently buffered request and clear the buffer.

    Appends an extra \\r\\n to the buffer.
    A message_body may be specified, to be appended to the request.
    """
    self._buffer.extend(("", ""))
    msg = "\r\n".join(self._buffer)
    del self._buffer[:]
    if isinstance(message_body, str):
        #print("message_body is %s" % message_body)
        # Can't combine unicode with bytes (which is the file upload),
        # so let's ignore it
        try:
            msg += message_body
            message_body = None
        except UnicodeDecodeError:
            pass
    self.send(msg)
    if message_body is not None:
        self.send(message_body)
HTTPConnection._send_output = _send_output

class BadUploadException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NotLoggedInException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Tracker(object):

    def __init__(self, username, password, root_url, login_url, main_url, cookies_file, tools_server=None, debug=False):
        self.username = username
        self.password = password
        self.root_url = root_url
        self.login_url = login_url
        self.main_url = main_url
        self.tools_server = tools_server
        self.cookies_file = cookies_file
        self.br = mechanize.Browser()
        self.logged_in = False
        self.debug = debug

        # Set up output dir
        self.wdir=os.path.abspath(os.path.dirname(__file__))

        # Set up the logger
        FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('tcpserver')

        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def login(self, invalidate_cookies=False, user_agent=None):
        br = self.br
        br.set_handle_robots(False)
        if user_agent == "auto":
            pass
        elif user_agent:
            br.addheaders = [('User-agent', user_agent)]
        else:
            # user agent updated 2016-04-17
            br.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36')]

        # Cookie Jar
        policy = mechanize.DefaultCookiePolicy(rfc2965=True)
        cj = mechanize.LWPCookieJar(policy=policy)
        br.set_cookiejar(cj)

        if os.path.isfile(os.path.join(self.wdir, self.cookies_file)) and not invalidate_cookies:
            self.logger.debug("Found %s" % self.cookies_file)
            cj.load(os.path.join(self.wdir, self.cookies_file), ignore_discard=True, ignore_expires=True)
            torrent_index = self.main_url
            self.logger.debug("Opening url...%s" % torrent_index)
            resp = br.open(torrent_index)
            if "login.php" in resp.geturl():
                self.logger.debug("Bad url.  Invalidating cookies...")
                self.login(invalidate_cookies=True)
        else:
            # Check if existing cookies work
            resp = br.open(self.login_url)

            br.select_form(nr=0) # select second form in page (0 indexed)
            br['username'] = self.username
            br['password'] = self.password
            response = br.submit()

            self.logger.debug("Saving cookies after login form")
            cj.save(os.path.join(self.wdir, self.cookies_file), ignore_discard=True, ignore_expires=True)
            self.logger.debug("Logged in to %s" % response.geturl())

        self.logged_in = True
        return self.logged_in

    def query_isbn(self, isbn, tools_server=None):
        if not tools_server:
            tools_server = self.tools_server
        self.logger.info("+++++++++++++++++++++++++++++++")
        self.logger.info("querying %s -- Start" % isbn)
        url='http://%s/search.php?keyword=%s' % (tools_server, isbn)
        r = requests.get(url)
        json_data = json.loads(r.text)
        self.logger.info("querying %s -- Done!" % isbn)
        return json_data

    def get_epub(self, url):
        self.logger.info(url)
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)

        resp = self.br.open(url)
        helpers.write_text_to_file("torrent_page.html", resp.read())

    def _get_torrent_info(self, url):
        self.logger.info(url)
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)

        resp = self.br.open(url)
        doc = lh.document_fromstring(resp.read())

        return parse_torrent_page(doc=doc)

    def download_torrent_from_url(self, url):
        torrent_info = self._get_torrent_info(url)
        download_url = torrent_info['download_url']
        self.logger.debug("download_url is %s" % download_url)
        self.logger.info("Downloading torrent...")
        torrent_resp = self.br.open(download_url)
        with open(os.path.join(self.wdir, torrent_info['slug']),'w') as f:
            f.write(torrent_resp.read())
            self.logger.debug("Wrote to file %s" % torrent_info['slug'])

    def _convert_file_to_new_encoding(self, source_file, source_encoding="iso-8859-1", target_encoding="utf-8"):
        """Convert a file to a new encoding, normally required to maintain the
        entire HTML request as a single encoding.  If unicode is found in the
        header, typically expects everything else to be unicode and will fail
        without the conversion"""
        self.logger.warn("DEPRACATED _convert_file_to_new_encoding")

        source_encoding = "iso-8859-1"
        target_encoding = "utf-8"
        source = open(source_file, 'r')
        _, source_file_name = os.path.split(source_file)
        my_target_fname = os.path.join(self.wdir, "output", "target_utf8_%s" % source_file_name)
        target = open(my_target_fname, "w")

        target.write(unicode(source.read(), source_encoding).encode(target_encoding))
        return my_target_fname

    def add_ebook_format(self, url, isbn, torrent_file, format='MOBI', debug_write_to_file=False):
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)

        self.logger.info("Opening %s...", url)
        resp = self.br.open(url)

        # Get the right form
        for form in self.br.forms():
            if form.attrs.get('id') == 'upload_table':
                self.br.form = form
                break

        if not self.br.form:
            self.logger.info("Missing form on %s" % url)
            return False

        # fill out the form
        self.br.form['book_isbn'] = isbn.replace('-','')
        self.br.form['book_format'] = [format.upper(),]

        # now you may attach it
        self.br.form.add_file(open(torrent_file, 'r'), 'text/plain', torrent_file)
        self.br.form.set_all_readonly(False)

        query = self.query_isbn(isbn)
        #query = {'Items': [{'Author': 'David Weber', 'Publisher': 'Baen', 'ReleaseDate': '2012'}]}
        self.br.form['book_author'] = query['Items'][0]['Author']
        self.br.form['book_publisher'] = query['Items'][0]['Publisher']
        book_year = query['Items'][0]['ReleaseDate'].split('-')[0]
        if not book_year:
            book_year = query['Items'][0]['PublicationDate'].split('-')[0]

        self.br.form['book_year'] = book_year

        # The submit can't mix the 'bytes' of the upload file with the rest of
        # the 'unicode.'  Need to update the headers
        # https://stackoverflow.com/questions/7993175/how-do-i-post-non-ascii-characters-using-httplib-when-content-type-is-applicati

        for control in self.br.form.controls:
            if unicode(control.type) is not u"textarea":
                print("control is %s and type is %s" % (control, control.type))
            else:
                print("control is TextareaControl: %s" % self.br.form[control.name][0:100])

            try:
                if isinstance(self.br.form[control.name], unicode):
                    print("%s is unicode" % control.name)
                    self.br.form[control.name] = unicode(self.br.form[control.name]).encode('latin1')
                    if isinstance(self.br.form[control.name], str):
                        print("Done encoding to ascii: %s" % self.br.form[control.name])
                    else:
                        print("Failed to encode %s" % control.name)
            except ValueError:
                print("ValueError for %s" % control)
        req = self.br.submit()
        final_url = req.geturl()
        self.logger.debug("Redirected to %s" % final_url)

        if "groupid" in final_url:
            html = resp.read()
            filename = "add_ebook_format_%s.html" % isbn
            self.logger.debug("Writing url to file %s" % filename)
            helpers.write_text_to_file(filename, html)
            raise BadUploadException('ISBN %s did not upload at %s.  See error file at %s' % (isbn, url, filename))

        return final_url

    def parse_search_page(self, filename=None, doc=None, url=None):
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)
        doc = self._get_doc_from_general(filename=filename, doc=doc, url=url)

        mydict = {}

        # Prepare top level keys
        mydict['title'] = doc.xpath('//title')[0].text_content()
        mydict['torrents'] = []

        # Fill out torrent key with 'page_url' list
        view_torrent_urls = doc.xpath('//a[@title="View Torrent"]/@href')
        for vtu in view_torrent_urls:
            mydict['torrents'].append({'page_url': '/'.join([self.root_url, vtu])})

        # Get the torrent list titles
        view_torrent_titles = doc.xpath('//a[@title="View Torrent"]/text()')
        for i, vtt in enumerate(view_torrent_titles):
            mydict['torrents'][i]['title'] = vtt

        # Get the author, year, format
        view_torrent_td = doc.xpath('//a[@title="View Torrent"]/parent::td')
        regex = re.compile('\[DL \| RP \] *(.*)-.*\(([0-9]{4})\).*\[([a-zA-Z]*)\]')
        for i, vta in enumerate(view_torrent_td):
            # Get the author, format, year
            raw_td = vta.text_content().replace('\n','')
            m = regex.search(raw_td)
            cleaned_author = m.group(1).strip()
            cleaned_year = m.group(2).strip()
            cleaned_format = m.group(3).strip()
            if i%30 == 0:
                self.logger.debug("cleaned_author is %s" % cleaned_author)
                self.logger.debug("cleaned_format is %s" % cleaned_format)
            mydict['torrents'][i]['author'] = cleaned_author
            mydict['torrents'][i]['year'] = cleaned_year
            mydict['torrents'][i]['format'] = cleaned_format

        # Get the download_url
        view_torrent_td = doc.xpath('//a[@title="Download"]/@href')
        for i, vtt in enumerate(view_torrent_td):
            cleaned_url = '/'.join([self.root_url, vtt])
            if i%15 == 0:
                self.logger.debug('vtt is %s' % cleaned_url)
            mydict['torrents'][i]['download_url'] = cleaned_url

        # Get the tags
        view_torrent_tags = doc.xpath('//div[@class="tags"]')
        for i, vtt in enumerate(view_torrent_tags):
            cleaned_tags = vtt.text_content()
            if i%15 == 0:
                self.logger.debug("cleaned tags is %s" % cleaned_tags)
            mydict['torrents'][i]['tags'] = cleaned_tags

        # Get the filesize
        view_torrent_filesize = doc.xpath('//tr[@class="torrent  "]/td[5]')
        for i, vtt in enumerate(view_torrent_filesize):
            cleaned_filesize = vtt.text_content()
            if i%15 == 0:
                self.logger.debug("cleaned filesize is %s" % cleaned_filesize)
            mydict['torrents'][i]['filesize'] = cleaned_filesize

        # get the torrent_id
        page_urls = [torrent['page_url'] for torrent in mydict['torrents']]
        for i, url in enumerate(page_urls):
            url_qs = urlparse.urlparse(url).query
            mydict['torrents'][i]['torrent_id'] = dict(urlparse.parse_qsl(url_qs))['torrentid']

        return mydict

    def _get_doc_from_general(self, filename=None, doc=None, url=None):
        # One or the other
        if doc is None and filename:
            with open(filename, 'r') as f:
                doc = lh.document_fromstring(f.read())
                return doc
        elif doc is not None and not filename:
            pass
        elif url:
            self.logger.debug("Parsing %s" % url)
            if not self.logged_in:
                self.logger.debug("Not logged in.")
                return False

            resp = self.br.open(url)
            html = resp.read()
            doc = lh.document_fromstring(html)
            return doc

        self.logger.debug("No valid doc or filename")
        return False

    def parse_torrent_page(self, filename=None, doc=None, url=None):
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)
        doc = self._get_doc_from_general(filename=filename, doc=doc, url=url)

        mydict = {}
        mydict['title'] = doc.xpath('//title')[0].text_content()
        # Make a slug
        mapping = dict.fromkeys(map(ord, "-: ,?!"))
        slug = unicode(mydict['title'][0:50]).translate(mapping)
        mydict['slug'] = '.'.join([slug, 'torrent'])
        # Continue
        mydict['torrent_table'] = doc.xpath('//table[@class="torrent_table"]')

        # get the ISBN
        bbcode = doc.xpath('//div/span[@class="bbcode"]')[0].text_content().split("\n")
        for line in bbcode:
            self.logger.debug(line)
            if "ISBN" in line:
                isbn = line.split(":")[1].strip()
                mydict['isbn'] = isbn
                self.logger.debug("Using ISBN: %s" % isbn)
                break
            elif "ASIN" in line:
                asin = line.split(":")[1].strip()
                mydict['isbn'] = asin
                self.logger.debug("ISBN not found, using ASIN: %s" % asin)
                break
        else:
            mydict['isbn'] = None

        # get the torrent info
        mydict['group_id'] = doc.xpath('//input[@name="groupid"]')[0].value
        # Add torrent_ids and raw_download_urls
        mydict['raw_download_urls'] = []
        mydict['torrent_ids'] = []
        # regex for torrent_id
        tid_regex = re.compile('.*id=([^&]*)')
        for dl_url in doc.xpath('//tr[@class="group_torrent "]//a[@title="Download"]/@href'):
            raw_download_url = '/'.join([self.root_url, dl_url])
            # raw_download_urls
            mydict['raw_download_urls'].append(raw_download_url)
            self.logger.debug("raw_download_url is: %s" % raw_download_url)

            # torrent_ids
            m = tid_regex.match(dl_url)
            torrent_id = m.group(1)
            mydict['torrent_ids'].append(torrent_id)

        mydict['format_titles'] = []
        mydict['formats'] = []

        #for link, tid in zip(doc.xpath('//tr[@class="group_torrent "]/a/@onclick'), mydict['torrent_ids']):
        for link in doc.xpath('//tr[@class="group_torrent "]//a'):
            # Make sure that the order is right for torrent_id and the title. onclick contains the torrent_id

            # Strip unicode
            title = link.text_content()
            printable = set(string.printable)
            title = filter(lambda x: x in printable, title).strip()

            # Add formats
            if 'MOBI' in title:
                mydict['formats'].append('MOBI')
            elif 'EPUB' in title:
                mydict['formats'].append('EPUB')
            else:
                continue

            self.logger.debug("Link is %s and content is %s" % (link, title))
            mydict['format_titles'].append(title)

        # Get the correct filenames
        mydict['format_filenames'] = []
        for item in doc.xpath("//tr[contains(concat(' ', @class, ' '), ' pad ')]//tr[2]//td[1]/text()"):
            raw_torrent_filename = item
            torrent_filename = raw_torrent_filename
            self.logger.debug("Td is %s and content is %s" % (item, torrent_filename))
            mydict['format_filenames'].append(torrent_filename)

        # Hook up the formats and raw_download_urls into a dict
        mydict['download_urls'] = dict(zip(mydict['formats'], mydict['raw_download_urls']))
        mydict['filenames'] = dict(zip(mydict['formats'], mydict['format_filenames']))

        self.logger.debug(pprint.pprint(mydict))
        return mydict

    def _get_doc_from_general(self, filename=None, doc=None, url=None):
        # One or the other
        if doc is None and filename:
            with open(filename, 'r') as f:
                doc = lh.document_fromstring(f.read())
                return doc
        elif doc is not None and not filename:
            pass
        elif url:
            self.logger.debug("Parsing %s" % url)
            if not self.logged_in:
                self.logger.debug("Not logged in.")
                return False

            resp = self.br.open(url)
            html = resp.read()
            doc = lh.document_fromstring(html)
            return doc

        self.logger.debug("No valid doc or filename")
        return False

    def get_stats(self, filename=None, doc=None, url=None):
        if url and not self.logged_in:
            raise NotLoggedInException("url requires login: %s" % url)

        doc = self._get_doc_from_general(filename=filename, doc=doc, url=url)
        if not doc:
            self.logger.debug('get_stats doc is None')
            return None

        stats = {}
        li_stats = doc.xpath('//ul[@class="stats nobullet"]/li')
        for stat in li_stats:
            stat_list = stat.text_content().strip().split(':')
            if len(stat_list) != 2:
                continue
            try:
                cs = self._clean_stat_list(stat_list)
                stats[cs[0]] = cs[1]
            except IndexError:
                continue

        self.logger.debug(stats)

        if ' for ' in stats['requests_filled_gb']:
            num_and_gb = stats['requests_filled_gb'].split(' for ')
            stats['requests_filled_num'] = num_and_gb[0]
            stats['requests_filled_gb'] = num_and_gb[1]

        return stats

    def _clean_stat_list(self, stat_list):
        #self.logger.debug("Dirty stat is %s" % stat_list)

        cleaned = stat_list

        # Append _num to non GB
        if 'TB' in stat_list[1]:
            # convert into GB
            cleaned[1] = cleaned[1].replace('TB','').strip()
            cleaned[1] = str(int(float(cleaned[1])*1000))
            cleaned[0] = cleaned[0] + "_gb"
        elif 'GB' in stat_list[1]:
            cleaned[0] = cleaned[0] + "_gb"
            cleaned[1] = cleaned[1].replace('GB','').strip()
        elif 'View' in stat_list[1]:
            cleaned[0] = cleaned[0] + "_num"

        cleaned[0] = cleaned[0].strip().replace(' ','_').strip().lower()
        cleaned[1] = cleaned[1].strip().replace(' View','').strip().lower()

        #self.logger.debug("Cleaned stat is %s" % cleaned)
        return cleaned

class Seedbox(object):

    def __init__(self, seed_dir=None):
        self.seed_dir = seed_dir

        # Set up the logger
        FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('tcpserver')
        self.logger.setLevel(logging.DEBUG)

    def add_torrent(self, url=None):
        if url:
            self.logger.debug("add_torrent: %s" % url)
        else:
            self.logger.error("add_torrent: Mising url")
            return False
        self.logger.debug('adding to transmission: %s' % url)
        subprocess.call(["transmission-remote", "-a", url])
        self.logger.debug('Done! adding to transmission: %s' % url)
        return True

    def _get_last_transmission_id(self):
        try:
            output = subprocess.check_output(["transmission-remote", "-l"])
        except subprocess.CalledProcessError, e:
            "stdout output:\n", e.output

        # Clean output
        #print(output.decode('latin1').split('\n'))
        last_item = output.decode('latin1').split('\n')[-3]
        first_number = last_item.strip().split(' ')[0]
        return first_number

    def _get_last_transmission_info(self):
        last_id = self._get_last_transmission_id()
        return self.get_transmission_info(transmission_id=last_id)

    def get_transmission_info(self, transmission_id):
        try:
            output = subprocess.check_output(["transmission-remote", "-t", str(transmission_id), "--info"])
        except subprocess.CalledProcessError, e:
            "stdout output:\n", e.output

        # Clean output
        myinfo = {}
        for row in output.split('\n'):
            try:
                key, value = row.split(': ')
            except ValueError:
                continue
            key_slug = key.strip().lower().replace(' ','_')
            myinfo[key_slug] = value.strip()
        self.logger.debug(pprint.pprint(myinfo))
        return myinfo

    def move_to_seed_dir(self, filename):
        if not self.seed_dir:
            logger.error("No seed_dir specified")
            return False

        return subprocess.call(["mv", "-v", filename, self.seed_dir])

    def _verify_transmission_id(self, transmission_id):
        if not self.seed_dir:
            logger.error("No seed_dir specified")
            return False

        subprocess.call(["transmission-remote", "-t", transmission_id, "--find", self.seed_dir])
        return subprocess.call(["transmission-remote", "-t", transmission_id, "-v"])

    def verify_last_transmission_id(self):
        last_tid = self._get_last_transmission_id()
        return self._verify_transmission_id(last_tid)
