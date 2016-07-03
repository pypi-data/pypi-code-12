# -*- coding: utf8 -*-
"""Scraper class used to retrieve Whyd source links and download audio tracks.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
import os

from bs4 import BeautifulSoup
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
import requests

# Default output format
YDL_PARAMS = {
    'outtmpl': '%(title)s.%(ext)s',
    'nooverwrites': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256'}]
}

# Whyd root URL
ROOT_URL = 'https://whyd.com'

# Supported providers
PROVIDERS = {
    'soundcloud': {
        'prefix': '/sc/',
        'root_url': 'https://soundcloud.com/'},
    'youtube': {
        'prefix': '/yt/',
        'root_url': 'https://youtu.be/'},
    'vimeo': {
        'prefix': '/vi/',
        'root_url': 'https://vimeo.com/'}
}

# Max. tracks to scrap
PLAYLIST_LIMIT = '300'


class WhydScraper():

    """ All your tracks are belong to us. """

    def __init__(self):
        self.ydl = YoutubeDL(YDL_PARAMS)
        self.ydl.add_default_info_extractors()

    def _make_soup(self, url):
        """ Helper to make a BeautifulSoup object.

            :param url: URL to scrap.
        """
        try:
            return BeautifulSoup(requests.get(url).text)
        except ValueError:
            logging.warning('The URL you provided is not valid : "%s"' % url)
            return None

    def scrap_playlists(self, username):
        """ Scrap user playlists from his profile page.

            :param username: User name (slug) OR id (/u/xxxx).
        """
        soup = self._make_soup('{root_url}/{username}/playlists'.format(
            root_url=ROOT_URL, username=username))

        pl_tags = soup.find_all('li', class_='playlist')

        return [li.a['href'].split('/')[-1] for li in pl_tags]

    def get_playlist_by_id(self, username, pl_id, limit=PLAYLIST_LIMIT):
        """ Get tracklist by Username + ID."""
        res = requests.get(
            '{root_url}/{username}/playlist/{pl_id}?format=json&limit={limit}'.format(
                root_url=ROOT_URL, username=username, pl_id=pl_id, limit=limit))

        tracks = self._format_json(res.json())
        return tracks

    def get_playlist_by_url(self, pl_url, limit=PLAYLIST_LIMIT):
        """ Get tracklist by URL. """
        res = requests.get('{url}?format=json&limit={limit}'.format(
            url=pl_url, limit=limit))
        tracks = self._format_json(res.json())
        return tracks

    def _format_json(self, json):
        """ Parse JSON and return formated dict. """
        # format urls
        for track in json:
            for e in PROVIDERS:
                if PROVIDERS[e]['prefix'] in track['eId']:
                    track['eId'] = track['eId'].replace(
                        PROVIDERS[e]['prefix'],
                        PROVIDERS[e]['root_url']).split('#')[0]

            try:
                playlist = track['pl']['name']
            except KeyError:
                playlist = 'None'
        return [{'playlist': playlist,
                 'name': track['name'],
                 'url': track['eId']} for track in json]

    def get_user_stream(self, username, limit='20'):
        """ Get user tracklist from its added tracks stream.

            :param username: User nickname (slug) OR id (/u/xxxx).
            :param limit: Maximum number of tracks to retrieve.
        """
        res = requests.get(
            '{root_url}/{username}?format=json&limit={limit}'.format(
                root_url=ROOT_URL, username=username, limit=limit))

        tracks = self._format_json(res.json())
        return tracks

    def get_user_likes(self, username):
        """ Get user tracklist from its liked tracks stream.

            :param username: User nickname (slug) OR id (/u/xxxx).
        """
        res = requests.get(
            '{root_url}/{username}/likes?format=json'.format(
                root_url=ROOT_URL, username=username))

        tracks = self._format_json(res.json())
        return tracks

    def download(self, url, outdir, dry_run=False):
        """ Download the audio version of a given track url.

            :param url: Track URL.
            :param outdir: Output directory.
        """
        if dry_run:
            print(url)
            return
        # output root folder
        try:
            os.mkdir('output')
        except OSError:
            pass
        # playlist specific folder
        try:
            os.mkdir('output/%s' % outdir)
            logging.info('output/%s created.' % outdir)
        except OSError:
            logging.info('output directory already exists, skipping creation.')

        self.ydl.params['outtmpl'] = 'output/' + outdir + '/%(title)s.%(ext)s'
        try:
            self.ydl.extract_info(url, download=True)
        except DownloadError as e:
            logging.info(e)
            return
