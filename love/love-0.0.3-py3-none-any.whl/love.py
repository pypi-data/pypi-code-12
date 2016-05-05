# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse


__version__ = '0.0.3'


import os
import sys
import random
import difflib
import subprocess

import pkgtools.pypi as pp
import emoji


from travispy import TravisPy
from withlog import Info, Message

import withlog

from time import sleep
# from cookiecutter.main import generate_context, generate_files



import logging

from .github import setup_github_credentials, setup_github_repository
from .flit import python_requires

def yffoo():
    yield from range(10)

heart = """
   
                L       OOO    V   V  EEEEE
                L      O   O   V   V  E    
                L      O   O   V   V  EEE  
                L      O   O    V V   E    
    oo          LLLLL   OOO      V    EEEEE
       oo                                        
          oo     OOOOOOOO:       OOOOOOOO!       
             oOOOO!!!!;;;;O    OO.......:;!O     
            'OOO!!!;;;;;;;;O  O.......:   ;!O    
            OOO!!!!;;::::::.OO........:    ;!O   
            OO!!!!;;:::::..............:   ;!O   
            OOO!!!;::::::..............:   ;!O   
             OO!!;;::::::.............:   ;!O           Made With Love
              OO!;;::::::......oo.....::::!O     
                O!!;::::::........oo..:::O                  - M - 
                  !!!;:::::..........ooO         
                     !!;:::::.......O   oo              version : {version}
                       ;;::::.....O        oo  ,o
                          :::..O              ooo
                            ::.              oooo
                             :                   
""".format(version=__version__)

from colored import fg, attr, bg

cheart = '\n'.join(map(
        lambda l : "%s%s%s" %(fg('deep_pink_3b'),l, attr(0)),
        heart.split('\n')
        ))

class WLove(Message):
   def __init__(self, title):
        super().__init__(title,1, fg('white') + bg('deep_pink_3b') )




try:
    import curses
except ImportError:
    curses = None

def _stderr_supports_color():
    color = False
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass
    return color



emoji_level = {
        10:emoji.emojize(":broken_heart:"),
        20:emoji.emojize(":growing_heart:"),
        30:emoji.emojize(":heart_with_arrow:")
}


class LogFormatter(logging.Formatter):
    """Log formatter with colour support
    """
    DEFAULT_COLORS = {
        logging.INFO: 2, # Green
        logging.WARNING: 3, # Yellow
        logging.ERROR: 1, # Red
        logging.CRITICAL: 1,
    }

    def __init__(self, color=True, datefmt=None):
        r"""
        :arg bool color: Enables color support.
        :arg string fmt: Log message format.
        It will be applied to the attributes dict of log records. The
        text between ``%(color)s`` and ``%(end_color)s`` will be colored
        depending on the level if color support is on.
        :arg dict colors: color mappings from logging level to terminal color
        code
        :arg string datefmt: Datetime format.
        Used for formatting ``(asctime)`` placeholder in ``prefix_fmt``.
        .. versionchanged:: 3.2
        Added ``fmt`` and ``datefmt`` arguments.
        """
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._colors = {}
        if color and _stderr_supports_color():
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = str(fg_color, "ascii")

            for levelno, code in self.DEFAULT_COLORS.items():
                self._colors[levelno] = str(curses.tparm(fg_color, code), "ascii")
            self._normal = str(curses.tigetstr("sgr0"), "ascii")

            scr = curses.initscr()
            self.termwidth = scr.getmaxyx()[1]
            curses.endwin()
        else:
            self._normal = ''
            # Default width is usually 80, but too wide is worse than too narrow
            self.termwidth = 70

    def formatMessage(self, record):
        right_text = '{initial}-{name}'.format(initial=record.levelname[0],
                                               name=record.name)
        if record.levelno in self._colors:
            start_color = self._colors[record.levelno]
            end_color = self._normal
        else:
            start_color = end_color = ''
        emo = emoji_level[record.levelno]


        return emo +' '+start_color + '[' +right_text + '] ' +  record.message + end_color + ' '+emo





def main():
    with WLove('Love') as p:
        submain(p)

def submain(p):
    """
    completly set-up a package in the target dir (using cookie cutter) 
        

    """
    parser = argparse.ArgumentParser(description='Bootstrap a Python Package with Love.')
    parser.add_argument('name', metavar='name', type=str, nargs='?',
                       help='a potential package name')
    parser.add_argument('target_dir', type=str, nargs='?',
                       help='target directory in which to create the package')
    parser.add_argument('--version', help='print version, logo and exist', action='store_true')
    parser.add_argument('--no-banner',  help='do not print banner', action='store_false')

    parser.add_argument('--no-travis', help='prevent Travis from being set-up', action='store_true')
    parser.add_argument('--no-flit', help='prevent usage of Flit to set-up-package', action='store_true')
    parser.add_argument('--no-similar', help='prevent search of similar project on PyPI', action='store_true')
    parser.add_argument('--python', help='set-up the minimal required python', action='store_true')

    args = parser.parse_args()
    proposal = args.name
    target_dir = args.target_dir
    

    LOGLEVEL = 50
    log = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(LogFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(LOGLEVEL)
    log.setLevel(LOGLEVEL)

    log.info = withlog.glog

    if args.no_banner:
        p(cheart)
    if args.version : 
       p('Version : '+ __version__)
       sys.exit(0)

    if args.python :
        python_requires()
        sys.exit(0)

    if not target_dir:
        with Info('Target directory'):
            target_dir = os.getcwd()
            log.info('Will use target dir : %s', target_dir)



    # generate a python package name

    adjectives = ['red','green','blue','purple','fluffy','soft','hard','golden','silver', 'pathetic', 'intrepid', 'jovial' , 'long']
    nouns = ['moon', 'frog', 'lake','orchid','sapphire','gem','sun','lily','ocean','lampshade','fish', 'koala', 'shark', 'kangaroo']
    if proposal and not proposal.isidentifier() and len(proposal)>3:
        log.info('package names should be valid python identifiers, and at least 3 letters long : %s', proposal)
        sys.exit(-1)


    if not proposal:
        proposal = random.choice(adjectives).capitalize()+random.choice(nouns).capitalize()
    plist = None

    #  compare name with existing package name, warn if too close
    if not args.no_similar:
        with Info('Similar projects'):
            log.info('Comparing "%s" to other existing package names...' % proposal)
            pypi = pp.PyPIXmlRpc()
            # cache that on a weekly basis ?
            if plist is None:
                plist = pypi.list_packages()
            closest = difflib.get_close_matches(proposal.lower(), map(str.lower, plist), cutoff=0.8)
            if closest:
                if proposal in closest:
                    log.info(proposal + ' already exists, maybe you would prefer to contribute to this package?')
                else:
                    log.info('%s name is close to the following package name: %s', proposal,  closest)
                response = input('Do you still want to continue ? [Y/n]')
                if not response:
                    response = 'y'
                if not response.lower() == 'y':
                    sys.exit('Aborting')
            else:
                log.info('"%s" seems like a great name !', proposal)


    #  Actually authenticate with github 
    #  Create (if do not exist) the named repo, and  clone URL.
    with Info('Github'):
        token, user = setup_github_credentials(log=log)
        slug = setup_github_repository(user, proposal, log)
        
    os.chdir(proposal)
    log.debug('I am now in %s', os.getcwd())

    if not args.no_travis:
        with Info('Continuous Integration: Configuring Travis-CI'):
            enable_travis(token, slug, log) 

    with Info('Setting up Layout'):
        project_layout(proposal, None, None, log)

    if not args.no_flit:
        with Info('Setting up Package with Flit.') as p, withlog.print_statement(p), withlog.input():
            packaging_init(log)
            with Info('Python Minimal version') as p, withlog.print_statement(p):
                python_requires('>=3.4')
                p('Package marked as requiring python >= 3.4')



def enable_travis(token, slug, log):
    """
    Enable Travis automatically for the given repo.

    this need to have access to the GitHub token.
    """

    # Done with github directly. Login to travis

    travis = TravisPy.github_auth(token, uri='https://api.travis-ci.org')
    user = travis.user()
    log.info('Travis user: %s', user.name)

    # Ask travis to sync with github, try to fetch created repo with exponentially decaying time.

    last_sync = user.synced_at
    log.info('syncing Travis with Github, this can take a while...')
    repo = travis._session.post(travis._session.uri+'/users/sync')
    for i in range(10):
        try:
            sleep((1.5)**i)
            repo = travis.repo(slug)
            if travis.user().synced_at == last_sync:
                raise ValueError('synced not really done, travis.repo() can be a duplicate')
            log.info('\nsyncing done')
            break
        # TODO: find the right exception here
        except Exception:
            pass
    ## todo , warn if not found


    #  Enable travis hook for this repository

    log.info('Enabling Travis-CI hook for this repository')
    resp = travis._session.put(travis._session.uri+"/hooks/",
                        json={
                            "hook": {
                                "id": repo.id ,
                                "active": True
                            }
                        },
                      )
    if resp.json()['result'] is True:
        log.info('Travis hook for this repository is now enabled.')
        log.info('Continuous integration test should be triggered every time you push code to github')
    else:
        log.info("I was not able to set up Travis hooks... something went wrong.")

    return user

def codecov():
    pass

def travis_yml():
    with open('.travis.yml', 'w') as f:
        f.write(
"""
language: python
python:
    - 3.5
    - 3.4
before_install:
    - pip install flit pytest
install:
    - flit install --symlink
script:
    - py.test
"""
        )



def project_layout(proposal, user=None, repo=None, log=None):
    """
    generate the project template

    proposal is the name of the project, 
    user is an object containing some information about the user. 
        - full name, 
        - github username
        - email



    """

    proposal = proposal.lower()

    #context_file = os.path.expanduser('~/.cookiecutters/cookiecutter-pypackage/cookiecutter.json')
    #context = generate_context(context_file)

    # os.chdir('..')
    # context['cookiecutter']['full_name'] = user.name
    # context['cookiecutter']['email'] = user.email
    # context['cookiecutter']['github_username'] = user.login
    # context['cookiecutter']['project_name'] = proposal
    # context['cookiecutter']['repo_name'] = proposal.lower()

    try:
        os.mkdir(proposal)
    except FileExistsError:
        log.info('Skip directory structure, as project seem to already exists')

    with open('.gitignore', 'w') as f:
        f.write('''
*.pyc
__pycache__
/build/
/dist/
''')

    with open( '/'.join([proposal, '__init__.py']), 'w') as f: 
        f.write('''
"""
a simple package
"""


__version__ = '0.0.1'

        ''')


    travis_yml()

    #generate_files(
    #        repo_dir=os.path.expanduser('~/.cookiecutters/cookiecutter-pypackage/'),
    #        context=context
    #    )

    log.info('Workig in %s', os.getcwd())
    os.listdir('.')

    subprocess.call(['git','add','.'], )

    subprocess.call(['git','commit',"-am'initial commit of %s'" % proposal])

    subprocess.call(['git', "push", "origin", "master:master"])

    #webbrowser.open('https://travis-ci.org/{slug}'.format(slug=repo.slug))

def packaging_init(log):
    log.info('Please answer the following questions: ')
    from flit.init import TerminalIniter
    TerminalIniter().initialise()

