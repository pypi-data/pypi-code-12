#!/usr/bin/env python2.7

#stdlib
from __future__ import absolute_import, division, print_function
import sys
import os.path
import urllib
import logging
from collections import namedtuple

if hasattr(__builtins__, 'raw_input'): # make python2 match python3
    input = raw_input

Podcast = namedtuple('Podcast', 'title, url')
Episode = namedtuple('Episode', 'title, description, url')

"""
try:
    import cPickle as pickle
except ImportError:
    import pickle
"""
import pickle

# imports, see requirements.txt
import podcastparser # get `podcastparser` with pip
import soco # get `soco` with pip
from clint import resources # get `clint` with pip
from clint.textui import puts, colored, indent  # get `clint` with pip
resources.init('lurtgjort.no', 'SonoPod')

class Library(object):
    def __init__(self):
        #'Read from cache'
        logging.info('read lib from %r', resources.user)
        try:
            self.podcasts = [Podcast(**e) for e in pickle.loads(resources.user.read('podcasts.db'))]
        except TypeError as e:
            #new library
            #logging.exception(e)
            self.podcasts = []
        logging.info('init podcasts Library, currently: %r', self.podcasts)


    def save(self):
        'Save self.podcasts to cache'
        prepared = [dict(vars(p)) for p in self.podcasts]
        logging.info('pik: %r', prepared)
        return resources.user.write('podcasts.db', pickle.dumps(prepared, protocol=2))

    def add(self, resource):
        'Add resource to self.podcasts if it doesnt exist'
        if resource.url in self:    
            return None

        logging.debug('adding resource to ibrary: %r', resource)
        self.podcasts.append(resource)
        return self.save()

    def __contains__(self, url):
        for e in self.podcasts:
            if e.url == url:
                return True
        return False

    @property
    def self(self):
        return self.podcasts
    

class PodcastParser(object):
    def __init__(self, url):
        self.url = url
        # get the 5 last episodes from podcast at url (podcastparser sorts by published date)
        self.pc = podcastparser.parse(self.url, 
                                      stream=urllib.urlopen(self.url),
                                      max_episodes=5)
        self.episodes = []

    def _s(self, s):
        'Normalize and remove any cruft from string'
        return podcastparser.squash_whitespace(podcastparser.remove_html_tags(s))

    def getTitle(self):
        'Get Podcast title'
        return self.pc['title']

    def getEpisodes(self):
        if len(self.episodes) == 0:
            logging.debug('Slurping podcast url: %r', self.url)
            self.episodes =  [Episode(self._s(e['title']),
                                      self._s(e['description']),
                                      e['enclosures'][0]['url']) for e in self.pc['episodes']]
        return self.episodes

class SonosPlayer(object):
    def __init__(self):
        self.players = soco.discover()
        if self.players is None or len(self.players) == 0:
            raise Exception('No Sonos players found')
            
        # get default player from config
        try:
            self.default = soco.SoCo(resources.user.read('sonosplayer.ip'))
        except TypeError as e:
            self.default = None
        if self.default is None and len(self.players) == 1: # no default sonos speaker set
            self.default = self.players.pop() # only one player found, set it as default
            self.setPlayer(self.default)

    def getPlayers(self):
        'Return a list of players that works for printing by chooseFrom'
        r = []
        for p in self.players:
            p.title = p.player_name
            r.append(p)
        return r

    def setPlayer(self, player):
        resources.user.write('sonosplayer.ip', player.ip_address)

    def play(self, episode):
        logging.debug('Playing episode %r on %r', episode, self.default)
        self.default.play_uri(uri=episode.url,
                              #meta= , # DIDL format
                              title=episode.title,
                              start=True)

def chooseFrom(title, prompt, iterable):
    'Helper function to interactively choose one item from an iterable'
    puts(colored.blue(title))
    for (idx,e) in enumerate(iterable, start=1):
        puts(colored.green('[{}]\t {} '.format(idx, e.title.encode('utf-8'))))

    idx = -1
    while not 0 <= idx < len(iterable):
        try:
            idx = int(input(prompt+'> '))-1 # deduct 1 b/c zero indexing
        except ValueError:
            pass
        except (KeyboardInterrupt, EOFError) as e:
            puts('\n')
            sys.exit(1)
    return iterable[idx]

def main():
    'Main function. '
    from clint import arguments # get `clint` with pip
    args = arguments.Args()
    
    if args.flags.contains( ['-h', '--help'] ):
        puts(colored.magenta('SonoPod is a command line client to feed your Sonos with podcasts'))
        puts(colored.magenta('Copyright 2016 <havard@gulldahl.no>, GPLv3 licensed'))
        puts('Usage: {} [-h|--help] [--setsonos] [--volume NN] [podcast_url]'.format(os.path.basename(__file__)))
        with indent(4, quote=' '):
            puts('[-h|--help]\t\tThis help text')
            puts('[--setsonos]\tSet default Sonos speaker')
            puts('[--volume NN]\tSet volume of default speaker to N, between 0 (silent) and 90 (max)')
            puts('[podcast_url]\tAdd a new podcast series to the library, and pick an episode to play')
            puts('\nIf run without arguments, presents a list of podcasts in the library')
            sys.exit(0)

    player = SonosPlayer()
    volflag = args.flags.start_with('--volume=')
    if volflag is not None:
        try:
            vol = int(volflag.get(0)[len('--volume='):], 10)
        except:
            vol = None
        if vol is None or not -1 < vol < 91:
            puts(colored.red('Need a value for volume between 0 (silent) and 90 (max)'))
            sys.exit(1)

        logging.debug('Setting volume to {}'.format(vol))
        player.default.volume = vol
        puts(colored.green('New volume of player is {}'.format(player.default.volume)))

    if args.flags.contains('--setsonos'):
        # we are started with a flag to set a new default
        player.setPlayer(chooseFrom('Choose a Sonos speaker', 
                                    'Set default', 
                                    player.getPlayers()))

    if player.default is None:
        # too many players and no default set
        player.setPlayer(chooseFrom('Choose a Sonos speaker', 
                                    'Set default', 
                                    player.getPlayers()))

    lib = Library()
    podcasturl = args.not_flags.get(0) # look at first argument that is not a flag
    if podcasturl is not None: # optional url on command line
        podcasturl = podcastparser.normalize_feed_url(podcasturl)
        if podcasturl is None:
            logging.error('invalid url on command line')
            puts(colored.red('This is not a valid url'))
            sys.exit(1)
        logging.debug('Getting podcast url: %r', podcasturl)
        pod = PodcastParser(podcasturl)
        lib.add(Podcast(pod.getTitle(), podcasturl))
    else:
        # no podcast url on command line, get a list from library
        pc = chooseFrom('Podcasts in library', 'Choose podcast', lib.self)
        pod = PodcastParser(pc.url)

    eps = pod.getEpisodes() 
    logging.debug('Got episodes : %r', eps)

    playthis = chooseFrom('Available episodes', 'Which episode to play', eps)
    logging.debug('Got episode %r from user input', playthis)

    player.play(playthis)

if __name__=='__main__':
    logging.basicConfig(level=logging.WARNING)
    main()
