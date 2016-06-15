# The MIT License (MIT)
#
# Copyright (c) 2016 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import cmd
import logging
import os
from os.path import normpath, join, split
from pwd import getpwuid
from grp import getgrgid
from glob import glob
import sys
import time
import requests
from requests.packages.urllib3 import disable_warnings
from collections import OrderedDict, namedtuple
from json import loads, dumps
from getpass import getpass, getuser
from clint.textui import progress
from pprint import pprint

from awftp import calctime, calcByteSize, splitfilename, _print, _
from .init import INTRO, no_redir_cmds
from .parse import paramcheck, convertaw

PIPE = '|'  # output shall be piped
OUTFILE = '>'  # output shall be written to a file
EXTENDFILE = '>>'  # output shall extend a file
S_IFDIR =  0o040000 # used to identify a directory...


# noinspection PyUnresolvedReferences
class Awftpshell(cmd.Cmd):
    intro = INTRO

    prompt = 'awftp> '

    def __init__(self, *args, target='', nossl=False, **kwargs):
        # if awftp was called with an HCP Anywhere system, we split it up into
        # the various components later used to connect.
        if 'target':
            aw = convertaw(target, nossl=nossl)
            self.aw = aw.netloc
            self.scheme = aw.scheme
            self.user = aw.user
        else:
            self.aw = self.user = self.expires = ''
            self.scheme = 'http' if nossl else 'https'
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.connected = False  # indicates that we are connected
        self.cwd = '/'

    def preloop(self):
        # disable SSL certificate verification warning
        disable_warnings()

        if self.aw and self.scheme:
            self.cmdqueue.append('open -x')

    def precmd(self, arg):
        """
        This overwrites the pre-command hook to strip off redirections from a
        command and sys.stdout accordingly accordingly.

        We are relying on everything being printed to sys.std. We realize
        redirections by simply mapping sys.stdout to a different file handle.

        :param arg:     the paramaters given with the command
        :return:        the command w/o the redirection or an empty string
                        if parsing failed
        """

        # first let's see if we need to look for pipe/outfile
        redir_type = redir_arg = None
        try:
            if arg.find(EXTENDFILE) != -1:
                redir_type = EXTENDFILE
                arg, redir_arg = arg.split(EXTENDFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(OUTFILE) != -1:
                redir_type = OUTFILE
                arg, redir_arg = arg.split(OUTFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(PIPE) != -1:
                redir_type = PIPE
                arg, redir_arg = arg.split(PIPE)
                redir_arg = redir_arg.strip()
        except Exception as e:
            _print('parsing redirction failed...\nhint: {}'.format(e))
            return ''

        if redir_type and arg.split()[0] in no_redir_cmds:
            print('error: no redirection for command "{}"...'
                  .format(arg.split()[0]))
            return ''

        if redir_type and not redir_arg:
            print('error: redirection without arguments...')
            return ''

        if redir_type == PIPE:
            self.logger.debug('will pipe to "{}"'.format(redir_arg))
            try:
                sys.stdout = os.popen(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == OUTFILE:
            self.logger.debug('will output to "{}"'.format(redir_arg))
            try:
                sys.stdout = open(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == EXTENDFILE:
            self.logger.debug('will append to "{}"'.format(redir_arg))
            try:
                sys.stdout = open(redir_arg, 'a')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''

        return arg

    def postcmd(self, stop, line):
        """
        This overwrites the post-command hook to reset sys.stdout to what it
        should be after a command with redirection was executed.
        """
        # make sure we flush the file handle to which sys.stdout points to at
        # the moment.
        print('', end='', flush=True)
        if sys.stdout != sys.__stdout__:
            sys.stdout.close()
            sys.stdout = sys.__stdout__
        return stop

    def emptyline(self):
        """Disable repetition of last command by pressing Enter"""
        pass

    def do_bye(self, args):
        'bye\n'\
        '    terminate awftp session and exit.'
        self.logger.info('--> called "bye {}" --> forwarded to "quit"'
                         .format(args))
        return self.do_quit(args)

    def do_cd(self, args):
        'cd [remote-directory]\n'\
        '    Change remote working directory to remote-directory, if given,\n'\
        '    otherwise to /'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) > 1:
                print('error: at max 1 parameter is allowed...',
                      file=sys.stderr)
                return
            else:
                if len(para.args):
                    cwd = normpath(join(self.cwd, para.args[0]))
                else:
                    cwd = '/'

                # test the new current directory for existence
                req = {'path': cwd}
                r = self.session.post('://'.join(
                    [self.scheme, self.aw]) + '/fss/public/path/info/get',
                                      json=req)
                if r.status_code == 200:
                    self.cwd = cwd
                    print('CWD command successful.')
                else:
                    print('CWD to {} failed ({} {})'.format(cwd, r.status_code,
                                                                   r.reason))

    def do_cdup(self, args):
        'cdup\n'\
        '    change remote working directory to parent directory.'
        if not self.connected:
            print('Not connected.')
            return

        if self.cwd == '/':
            print('CWD command successful.')
        else:
            cwd = normpath(join(self.cwd, '..'))
            req = {'path': cwd}
            r = self.session.post('://'.join(
                [self.scheme, self.aw]) + '/fss/public/path/info/get',
                                  json=req)
            if r.status_code == 200:
                self.cwd = cwd
                print('CWD command successful.')
            else:
                print('CWD to {} failed ({} {})'.format(cwd, r.status_code,
                                                        r.reason))

    def do_close(self, args):
        'close\n'\
        '    terminate awftp session.'
        if self.connected:
            self.session.close()
            self.session = None
            self.connected = False
            self.expires = ''
            print('Disconnected from {}.'.format(self.aw))
        else:
            print('error: not connected', file=sys.stderr)


    def do_dir(self, args):
        'dir [remote-path]\n'\
        '    list contents of remote path'
        self.do_ls(args)

    def do_exit(self, args):
        'exit\n'\
        '    terminate awftp session and exit'
        self.logger.info('--> called "exit {}" --> forwarded to "quit"'
                         .format(args))
        return self.do_quit(args)

    def do_get(self, args):
        'get [-p] remote-file [local-file]\n'\
        '    receive file\n'\
        '    -p shows a progress meter'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='p')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) not in [1, 2]:
                _print('error: one or two parameters are required...',
                       file=sys.stderr)
                return
            elif len(para.args) == 1:
                src = normpath(join(self.cwd, splitfilename(para.args[0])))
                tgt = splitfilename(para.args[0])
            else:  # len(para.args) == 2
                src = normpath(join(self.cwd, splitfilename(para.args[0])))
                tgt = para.args[1] if para.args[1].startswith('/') else para.args[1]

                # if the put target is an existing folder, make sure we move
                # the source into the folder with the source name
                # r = self.session.post(
                #     '://'.join(
                #         [self.scheme, self.aw]) + '/fss/public/path/info/get',
                #     json={'path': tgt})
                # if r.status_code == 200:
                #     tgtres = r.json()
                #
                # if r.status_code == 200 and tgtres['type'] == 'FOLDER':
                #     tgt = join(_target, splitfilename(para.args[0]))

        print('get from src = {} to tgt = {}'.format(src, tgt))
        self.logger.debug('get from src = {} to tgt = {}'.format(src, tgt))

        # get the source file size
        _size = self.__getmeta(src)['size'] or 0


        try:
            with open(tgt, 'wb') as tgthdl:
                src = normpath(join(self.cwd, src))
                r = self.session.get('://'.join(
                    [self.scheme, self.aw]) + '/fss/public/file/stream/read',
                                      params={'path': src},
                                      headers={'Accept':
                                                   'application/octet-stream'},
                                     stream=True if 'p' in para.flags else False)
                if r.status_code == 200:
                    self.logger.debug('GET {} to {} successful.'.format(src,
                                                                        tgt))

                    if 'p' in para.flags:
                        gotnow = 0
                        with progress.Bar(label="GET {} ".format(src),
                                          expected_size=_size) as bar:
                            for chunk in r.iter_content(chunk_size=32*1024):
                                gotnow += len(chunk)
                                bar.show(gotnow)
                                tgthdl.write(chunk)
                    else:
                        tgthdl.write(r.content)
                    print('GET command successful.')
                else:

                    _print('GET {} {} failed ({} {}){}'
                           .format(src, tgt, r.status_code, r.reason,
                                   '\n'+r.text if r.status_code == 400 else ''))
        except Exception as e:
            _print('GET command failed...\nhint: {}'.format(e),
                   file=sys.stderr)
            return

    def do_lcd(self, args):
        'lcd [local-directory]\n'\
        '    change the local working dirkectory to local-directory (or to\n'\
        '    home directory, if local-directory isn\'t given)'
        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) > 1:
                print('error: at max 1 parameter is allowed...',
                      file=sys.stderr)
                return
            else:
                newd = para.args[0] if len(para.args) else os.path.expanduser("~")
                try:
                    os.chdir(newd)
                except Exception as e:
                    _print('error: {}'.format(e),
                           file=sys.stderr)
                    return
                print('Local CWD command{}successful.'
                      .format(' to {} '.format(newd) if not len(para.args) else ' '))

    def do_link(self, args):
        'link [-a] [-i|-p] -r|-u|-ru [expiration_days] file|folder\n'\
        '    create a link to share a file or folder\n'\
        '    -a add an access code\n'\
        '    -i force creating an internal link\n'\
        '    -p force creating a public link\n'\
        '    -r the link is good for view and download of files\n'\
        '    -u the link is good for uploading files\n'\
        '       (at least one of -r and -u is required)'
        '\n'\
        '    expiration_days must be an integer'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='aipru')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if 'i' in para.flags and 'p' in para.flags:
                _print('error: you can\'t force both internal and public...',
                       file=sys.stderr)
                return
            elif len(para.args) < 1 or len(para.args) > 2:
                _print('error: one or two parameter required...',
                       file=sys.stderr)
                return
            elif not 'r' in para.flags and not 'u' in para.flags:
                _print('error: at least one of -r and -u is required...',
                       file=sys.stderr)
                return

        req = {'permissions': []}
        # care for expiration days, if given
        if len(para.args) == 2:
            try:
                req['expirationDays'] = int(para.args[0])
            except ValueError:
                _print('error: expiration_days needs to be integer...',
                       file=sys.stderr)
                return

        # care for the path to link
        if para.args[-1].startswith('/'):
            req['path'] = para.args[-1]
        else:
            req['path'] = normpath(join(self.cwd, para.args[-1]))

        # care for the flags
        if 'a' in para.flags:
            req['accessCode'] = True
        if 'i' in para.flags:
            req['public'] = False
        if 'p' in para.flags:
            req['public'] = True
        if 'r' in para.flags:
            req['permissions'].append('READ')
        if 'u' in para.flags:
            req['permissions'].append('UPLOAD')

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/link/create',
                              json=req)
        if r.status_code == 200:
            res = r.json()
            print('Link for {} created:'.format(res['path']))
            print('    link:          {}'.format(res['url']))
            print('    visibility:    {}'.format('public' if res['public'] else 'internal'))
            print('    accessCode:    {}'
                  .format(res['accessCode'] if 'accessCode' in res.keys() else
                                            '-'))
            print('    permission(s): {}'.format(','.join(res['permissions'])))
            print('    expires:       {}'
                  .format(time.strftime('%Y/%m/%d %H:%M:%S',
                                        time.localtime(res['expirationDate'] /
                                                       1000))))
        elif r.status_code == 403:
            _print('CLNK failed for {} ({} {})\nuse the "user" command to check'
                   ' your permissions...'
                  .format(req['path'], r.status_code, r.reason))
        elif r.status_code == 404:
            _print('CLNK failed for {} ({} {})\nmake sure the file/folder to '
                   'be shared exists...'
                  .format(req['path'], r.status_code, r.reason))
        else:
            print('CLNK failed for {} ({} {})'
                  .format(req['path'], r.status_code, r.reason))



    def do_lpwd(self, args):
        'lpwd\n'\
        '    Print the local working directory.'
        print('Local directory: {}'.format(os.getcwd()))

    def do_lls(self, arg):
        'lls [local-path]\n'\
        '    list contents of local path'
        try:
            para = paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max one parameter required...',
                       file=sys.stderr)
                return
            else:
                # if len(para.args):
                #     cwd = normpath(join(os.getcwd(), para.args[0]))
                # else:
                #     cwd = os.getcwd()
                if len(para.args):
                    try:
                        isdir = True if os.stat(para.args[0]).st_mode & S_IFDIR == S_IFDIR else False
                    except FileNotFoundError:
                        cwd = para.args[0]
                    else:
                        cwd = join(para.args[0], '*') if isdir else para.args[0]
                else:
                    cwd = '*'

        # this is to make sure we use os.scandir() for better performance,
        # if it's available; else we use os.listdir()
        # try:
        #     scan = os.scandir
        # except ImportError:
        #     scan = os.listdir
        #
        # for f in scan(path=cwd):

        # TODO: remove test code (glob.glob() instead of scandir())
        for f in glob(cwd):
            # drwxr-xr-x   1 root users         4096 May  9 14:47 hcp_a
            # -rwxrwxrwx   1 admin    users           14656 May 04  2015 2013 IP-Umstellung.ods
            st = os.stat(f)
            # print('{}{} {:>4} {:8} {:8} {:>12} {} {}'
            print('{} {:>4} {:8} {:8} {:>12} {} {}'
                  .format(#'d' if st.st_mode ^ S_IFDIR == S_IFDIR else '-',
                          self.__mode(st.st_mode),
                          st.st_nlink,
                          getpwuid(st.st_uid).pw_name,
                          getgrgid(st.st_gid).gr_name,
                          calcByteSize(st.st_size),
                          time.strftime('%Y/%m/%d %H:%M:%S',
                                        time.localtime(st.st_mtime)),
                          f))

            # if scan != os.listdir:
            #     # drwxr-xr-x   1 root users         4096 May  9 14:47 hcp_a
            #     # -rwxrwxrwx   1 admin    users           14656 May 04  2015 2013 IP-Umstellung.ods
            #     st = f.stat()
            #     print('{}{} {:>4} {:8} {:8} {:>12} {} {}'
            #           .format('d' if f.is_dir() else '-',
            #                   self.__mode(st.st_mode),
            #                   st.st_nlink,
            #                   getpwuid(st.st_uid).pw_name,
            #                   getgrgid(st.st_gid).gr_name,
            #                   calcByteSize(st.st_size),
            #                   time.strftime('%Y/%m/%d %H:%M:%S',
            #                                 time.localtime(st.st_mtime)),
            #                   f.name))

    def do_ls(self, arg):
        'ls [remote-path]\n'\
        '    list contents of remote path'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max one parameter required...',
                       file=sys.stderr)
                return
            else:
                if len(para.args):
                    cwd = normpath(join(self.cwd, para.args[0]))
                else:
                    cwd = self.cwd

        req = {'path': cwd}
        cont = True
        res = {}

        while cont:
            r = self.session.post('://'.join(
                [self.scheme, self.aw]) + '/fss/public/folder/entries/list',
                                  json=req)
            if r.status_code != 200:
                # maybe cwd is a single file?
                if r.status_code == 404 and not res:
                    r1 = self.session.post('://'.join(
                        [self.scheme,
                         self.aw]) + '/fss/public/path/info/get',
                                          json=req)
                    if r1.status_code == 200:
                        c = r1.json()
                        res[c['name']] = {'type': c['type'],
                                          'size': c[
                                              'size'] if 'size' in c.keys() else 0,
                                          'changeTime': c['changeTime']}
                        break
                _print('ls failed ({} {})'.format(r.status_code, r.reason))
                return
            else:
                c = r.json()
                if 'pageToken' in c.keys():
                    req['pageToken'] = c['pageToken']
                    del req['path']
                else:
                    cont = False

                for f in c['entries']:
                    res[f['name']] = {'type': f['type'],
                                      'size': f['size'] if 'size' in f.keys() else 0,
                                      'changeTime': f['changeTime']}

        for f in sorted(res.keys()):
            print('{}{:>9} {:>4} {:8} {:8} {:>12} {} {}'
                  .format('d' if res[f]['type'] == 'FOLDER' else '-',
                          '', # the permission bitmask
                          '-', # the number of hardlinks
                          '-', # the user
                          '-', # the group
                          calcByteSize(res[f]['size']) if 'size' in res[f].keys() else '',
                          time.strftime('%Y/%m/%d %H:%M:%S',
                                        time.localtime(res[f]['changeTime'] / 1000)),
                          join(para.args[0], f) if len(para.args) else f))

    def do_mkdir(self, args):
        'mkdir [-R] directory-name\n'\
        '    make directory on the remote machine.\n'\
        '    -R recursively make parent directories if required.'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='R')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if not len(para.args):
                _print('error: exactly one parameter required...',
                       file=sys.stderr)
                return
            else:
                if para.args[0].startswith('/'):
                    newd = para.args[0]
                else:
                    newd = normpath(join(self.cwd, para.args[0]))

        req = {'path': newd,
               'createParents': True if 'R' in para.flags else False}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/folder/create',
                              json=req)
        if r.status_code == 201:
            print('RMD command successful.')
        else:
            print('RMD {} ({} {})'.format(newd, r.status_code, r.reason))

    def do_mv(self, args):
        'mv [-R] old_name new_name\n'\
        '    move a file or directory to a new name or position\n'\
        '    -R recursively make parent directories if required.'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='R')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) != 2:
                _print('error: exactly two parameters required...',
                       file=sys.stderr)
                return
            elif para.args[0] == '/':
                _print('error: / can\'t be moved, as you should know!',
                       file=sys.stderr)
                return
            elif para.args[1].endswith('/') and para.args[1] != '/':
                _print('error: move target may not end with /!',
                       file=sys.stderr)
                return

        # get sources etag and type
        req = {
            'path': para.args[0] if para.args[0].startswith('/') else normpath(
                join(self.cwd, para.args[0]))}
        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            srcres = r.json()
        elif r.status_code == 404:
            _print('error: {} doesn\'t exist...'.format(para.args[0]),
                   file=sys.stderr)
            return
        else:
            _print('error: failed to stat {} ({} {})...'
                   .format(para.args[0], r.status_code, r.reason),
                   file=sys.stderr)
            return

        # check target
        req = {
            'path': para.args[1] if para.args[1].startswith('/') else normpath(
                join(self.cwd, para.args[1]))}
        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            tgtres = r.json()
        elif r.status_code != 404:
            _print('error: failed to stat {} ({} {})...'
                   .format(para.args[1], r.status_code, r.reason),
                   file=sys.stderr)
            return

        # if the move target is an existing folder, make sure we move the
        # source into the folder with the source name
        _target = para.args[1] if para.args[1].startswith('/') else normpath(join(self.cwd, para.args[1]))
        if r.status_code == 200 and tgtres['type'] == 'FOLDER':
            _target = join(_target, split(para.args[0])[1])

        req = {'sourcePath': para.args[0] if para.args[0].startswith('/') else normpath(join(self.cwd, para.args[0])),
               'destinationPath': _target,
               'etag': srcres['etag'],
               'createParents': True if 'R' in para.flags else False}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/move',
                              json=req)
        if r.status_code == 200:
            print('MV command successful.')
        else:
            print('MV {} {} ({} {})'.format(para.args[0], para.args[1],
                                            r.status_code, r.reason))

    def do_open(self, args):
        'open [host-name]\n'\
        '    connect to remote HCP Anywhere server'

        # make sure we are not connected, yet
        if self.connected:
            print('error: already connected to {} - use "close" to disconnect.'
                  .format(self.aw), file=sys.stderr)
            return

        if not args == '-x':
            # request aw server
            while True:
                aw = input('to ({}) '.format(self.aw))
                if not aw and self.aw:
                    aw = self.aw
                if aw:
                    break
            self.aw = aw

        self.session = requests.Session()
        # set default headers required by HCP Anywhere FSS-API
        self.session.headers.update({'X-HCPAW-FSS-API-VERSION': '2.1.1',
                                     'Accept': 'application/json',
                                     'Content-Type': 'application/json'})
        # disable SSL certificate verification
        self.session.verify = False

        # request user, if not already known
        print('About to connect to {}.'.format(self.aw))
        self.user = self.user or getuser()
        while True:
            user = input('Name ({}): '.format(self.user))
            if not user and self.user:
                user = self.user
            if user:
                break
        self.user = user

        # request the password
        print('Password required for {}.'.format(self.user), flush=True)
        while True:
            passwd = getpass('Password: ')
            if passwd:
                break
        if not passwd:
            return
        auth = OrderedDict([('username', self.user),
                            ('password', passwd),
                            ('grant_type', 'urn:hds:oauth:negotiate-client')])

        try:
            r = self.session.post('://'.join([self.scheme, self.aw])+'/fss/public/login/oauth',
                                  data=dumps(auth))
        except requests.exceptions.ConnectionError as e:
            _print('Connection to {} failed...\nhint: {}'
                   .format(self.aw, e), file=sys.stderr, flush=True)
        else:
            if r.status_code == 200:
                rr = r.json()
                self.session.headers.update({'Authorization': '{} {}'
                                            .format(rr['token_type'],
                                                    rr['access_token'])})
                self.expires = time.strftime('%Y/%m/%d %H:%M:%S',
                                             time.localtime(time.time() +
                                                            rr['expires_in']))
                self.connected = True
                self.logger.debug('acquire_token returned: {} {} {}'
                                  .format(r.status_code, r.reason, r.elapsed))
                print('User {} logged in.'.format(self.user))
                print('Remote system type is HCP Anywhere.')
                print('Using binary mode to transfer files.')
            else:
                print('Login incorrect ({} {}).'
                      .format(r.status_code, r.reason))
                print('awftp: Login failed')

    def do_put(self, args):
        'put local-file [remote-file]\n'\
        '    send one file.'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) not in [1, 2]:
                _print('error: one or two parameters are required...',
                       file=sys.stderr)
                return
            elif para.args[0].endswith('/') or para.args[0].endswith('\\'):
                _print('error: PUT src can\'t be a folder...',
                       file=sys.stderr)
                return
            elif len(para.args) == 1:
                src = para.args[0]
                tgt = normpath(join(self.cwd, splitfilename(src)))
            else: # len(para.args) == 2
                src = para.args[0]
                tgt = para.args[1] if para.args[1].startswith('/') else normpath(join(self.cwd, para.args[1]))

                # if the put target is an existing folder, make sure we move
                # the source into the folder with the source name
                r = self.session.post(
                    '://'.join([self.scheme, self.aw]) + '/fss/public/path/info/get',
                    json={'path': tgt})
                if r.status_code == 200:
                    tgtres = r.json()

                if r.status_code == 200 and tgtres['type'] == 'FOLDER':
                    tgt = join(_target, splitfilename(para.args[0]))

        self.logger.debug('put from src = {} to tgt = {}'.format(src, tgt))

        try:
            with open(src, 'rb') as sendhdl:
                tgt = normpath(join(self.cwd, tgt))
                r = self.session.post('://'.join(
                    [self.scheme, self.aw]) + '/fss/public/file/stream/create',
                                      data=sendhdl,
                                      params={'path': tgt,
                                              'createParents': False},
                                      headers={'Content-Type':
                                                   'application/octet-stream'})
                if r.status_code == 201:
                    print('PUT command successful.')
                else:
                    print('PUT {} {} failed ({} {})'.format(src, tgt,
                                                    r.status_code, r.reason))
        except Exception as e:
            _print('PUT command failed...\nhint: {}'.format(e),
                   file=sys.stderr)
            return

    def do_pwd(self, args):
        'pwd\n'\
        '    Print the remote working directory.'
        if not self.connected:
            print('Not connected.')
            return

        print('Remote directory: {}'.format(self.cwd))

    def do_quit(self, arg):
        'quit\n'\
        '    terminate awftp session and exit.'
        self.logger.info('--> called "quit {}"'.format(arg))

        print('Goodbye.')
        return True

    def do_rmdir(self, args):
        'rmdir [-R] directory-name\n'\
        '    remove a directory on the remote machine.\n'\
        '    -R recursively delete a the directory and *all* its content.'
        if not self.connected:
            print('Not connected.')
            return

        try:
            para = paramcheck(args, flags='R')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if not len(para.args):
                _print('error: exactly one parameter required...',
                       file=sys.stderr)
                return
            else:
                if para.args[0] == '/':
                    _print('error: can\'t delete /',
                           file=sys.stderr)
                    return
                if para.args[0].startswith('/'):
                    rmd = para.args[0]
                else:
                    rmd = normpath(join(self.cwd, para.args[0]))

        etag = self.__getmeta(rmd)['etag']
        if not etag:
            print('error: stat({}) failed'.format(rmd))
            return

        req = {'path': rmd,
               'recursive': True if 'R' in para.flags else False,
               'etag': etag}


        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/delete',
                              json=req)
        if r.status_code == 204:
            print('RMD command successful.')
        else:
            if r.status_code == 400:
                print('    {}'.format(r.text))
            print('RMD {} ({} {})'.format(rmd, r.status_code, r.reason))

    # def do_run(self, arg):
    #     'run <script>\n' \
    #     '    Run a batch of commands stored in file <script>.'
    #     try:
    #         para = paramcheck(arg)
    #     except Exception as e:
    #         _print('error: parameters invalid...\nhint: {}'.format(e),
    #                file=sys.stderr)
    #         return
    #     else:
    #         if not len(para.args):
    #             _print('error: at least one parameter required...',
    #                    file=sys.stderr)
    #
    #     try:
    #         with open(para.args[0], 'r') as inhdl:
    #             for cmnd in inhdl.readlines():
    #                 cmnd = cmnd.strip()
    #                 # skip comments and empty lines
    #                 if cmnd and not cmnd.startswith('#'):
    #                     if cmnd.startswith('run'):
    #                         print('skipping "{}"...'.format(cmnd))
    #                     else:
    #                         self.cmdqueue.append('_exec ' + cmnd.strip())
    #     except Exception as e:
    #         _print('error: running script "{}" failed...\nhint: {}'
    #                .format(para.args[0], e), file=sys.stderr)

    def do_status(self, arg):
        'status\n' \
        '    Show the session status.'
        self.logger.info('--> called "status {}"'.format(arg))
        if self.connected:
            print('Connected to:       {}@{}'.format(self.user, self.aw))
            print('Session expires:    {}'.format(self.expires))
            print('Current')
            print('  remote directory: {}'.format(self.cwd))
            print('  local directory:  {}'.format(os.getcwd()))
        else:
            if self.aw:
                print('Not connected, but preset to {}{}'
                      .format(self.user+'@', self.aw))
            else:
                print('Not connected.')

    def do_time(self, arg):
        'time command [args]\n' \
        '    measure the time command takes to complete'
        self.logger.info('--> called "time {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        st = time.time()
        if command:
            try:
                result = eval('self.do_{}("{}")'.format(command, params))
            except Exception as e:
                print('error: time command failed...\n\thint: {}'.format(e),
                      file=sys.stderr)
            else:
                time.sleep(.25)
                print('[time: {}]'.format(calctime(time.time() - st)), file=sys.stderr,
                      flush=True)
                return result
        else:
            print('error: time command failed - no command given...',
                  file=sys.stderr)

    # def do_test(self, args):
    #     try:
    #         para = paramcheck(args, flags='flags')
    #     except Exception as e:
    #         _print('error: parameters invalid...\nhint: {}'.format(e),
    #                file=sys.stderr)
    #         return
    #     else:
    #         if len(para.args) > 2:
    #             print('error: at max 2 parameters are required...',
    #                   file=sys.stderr)
    #             return
    #         else:
    #             print(str(para))
    #             for i in range(30):
    #                 print(i)

    def do_user(self, args):
        'user\n'\
        '    get information about the user\s settings in HCP Anywhere.'
        if not self.connected:
            print('Not connected.')
            return

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/user/get')
        if r.status_code == 200:
            res = r.json()
            print('User:  {} ({})'.format(res['username'], res['email']))
            print('usage: {} of {}'.format(calcByteSize(res['usageBytes']),
                                           calcByteSize(res['quotaBytes'])))
            print('Settings:')
            print('    Sharing enabled: {} (public sharing {}allowed)'.format(
                'yes' if res['linkSettings']['sharingEnabled'] else 'no',
                '' if res['linkSettings']['publicSharingEnabled'] else 'not '))
            print('    Upload enabled:  {} (public upload {}allowed)'.format(
                'yes' if res['linkSettings']['uploadEnabled'] else 'no',
                '' if res['linkSettings']['publicUploadEnabled'] else 'not '))
            print('    default is {} sharing'.format(
                'public' if res['linkSettings'][
                    'sharingDefaultPublic'] else 'internal'))
            print('    {} days to share per default, max. {} days'.format(
                res['linkSettings']['defaultDaysToShare'],
                res['linkSettings']['maxDaysToShare']))
        else:
            print('USR command failed ({} {})'.format(r.status_code, r.reason))


    def __exec(self, arg):
        # Run a command given as parameters, but make sure to print a prompt
        # before. This is for running scripted commands (~/.hs3shrc)

        self.logger.debug('--> called "_run {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        if command:
            print(self.prompt + arg, flush=True)
            return eval('self.do_{}("{}")'.format(command, params))
        else:
            return

    def __getmeta(self, path):
        '''
        Get a files or directories metadata.

        :param path:    the file or directory to query
        :return:        the response json converted to dict
        '''
        req = {'path': path}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug('getmeta failed ({} {})'.format(r.status_code,
                                                              r.reason))
            return None

    def __mode(self, mode):
        '''
        From a st_mode Integer, calculate the ls-alike string

        :param mode:    a st_mode Integer
        :return:        a string
        '''
        ret = 'd' if mode & S_IFDIR == S_IFDIR else '-'
        cnt = 0

        for i in str(bin(mode))[-9:]:
            # rwxr-xr-x
            if cnt in [0, 3, 6]:
                ret += 'r' if i == '1' else '-'
            elif cnt in [1, 4, 7]:
                ret += 'w' if i == '1' else '-'
            else:
                ret += 'x' if i == '1' else '-'
            cnt += 1

        return ret
