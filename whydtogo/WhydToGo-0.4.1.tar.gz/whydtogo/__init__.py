# coding: utf8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging

import click
from slugify import slugify
from whydtogo.scraper import WhydScraper


__author__ = 'Julien Tanay'
__version__ = '0.4.1'
VERSION = __version__

@click.group()
def main():
    pass

@main.command()
@click.argument('username')
@click.option('--likes', default=False, help='Fetch user likes (last tracks)')
@click.option('--stream', default=False, help='Fetch user stream (last tracks)')
@click.option('--total', default=False, help='Fetch all user tracks (caution!)')
@click.option('--dryrun', default=False, help='Only print the result')
def user(username, likes, stream, total, dryrun):
    ws = WhydScraper()
    if likes:
        tracklist = ws.get_user_likes(username)
        for track in tracklist:
            ws.download(
                track['url'],
                outdir=slugify('{user}_likes'.format(
                    user=username)),
                dry_run=dryrun)

    elif stream:
        tracklist = ws.get_user_stream(username)
        for track in tracklist:
            ws.download(
                track['url'],
                outdir=slugify(username),
                dry_run=dryrun)

    elif total:
        tracklist = ws.get_user_stream(username, limit='3000')
        for track in tracklist:
                ws.download(
                    track['url'],
                    outdir=slugify(username),
                    dry_run=dryrun)

    else:
        for playlist_id in ws.scrap_playlists(username):
            playlist = ws.get_playlist_by_id(
                username, playlist_id)

            for track in playlist:
                    ws.download(
                        track['url'],
                        outdir=slugify(track['playlist']),
                        dry_run=dryrun)
    return


@main.command()
@click.argument('urls', nargs=-1)
@click.option('--dryrun', help='Only print the result')
def playlist(url, print):
    ws = WhydScraper()
    for url in urls:
        playlist = ws.get_playlist_by_url(url)

        for track in playlist:
            ws.download(
                track['url'],
                outdir=slugify(track['playlist']),
                dry_run=dryrun)
    return

if __name__ == '__main__':
    main()
