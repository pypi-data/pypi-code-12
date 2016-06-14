# interface to subversion repository

import os, subprocess, tempfile, traceback, sys
from lxml import etree
from bl.dict import Dict
from bl.url import URL

class SVN(Dict):
    "direct interface to a Subversion repository using svn and svnmucc via subprocess"

    def __init__(self, log=print, 
            url=None, local=None, parent_path=None,
            username=None, password=None, trust_server_cert=True, 
            svn=None, svnmucc=None, svnlook=None, 
            access_file=None):
        Dict.__init__(self, log_=log, 
            url=URL(url or ''), local=local, parent_path=parent_path,
            username=username, password=password, trust_server_cert=trust_server_cert, 
            svn=svn or 'svn', svnmucc=svnmucc or 'svnmucc', svnlook=svnlook or 'svnlook')
        if access_file is not None: # load the access file
            from .svn_access_file import SVNAccessFile
            self.access_file = SVNAccessFile(access_file)

    def __repr__(self):
        return "SVN(url='%s')" % self.url

    def __call__(self, *args):
        "uses svn to access the repository"
        result = self._subprocess(self.svn, *args)
        if '--xml' in args:
            return etree.XML(result)
        else:
            return result

    def mucc(self, *args):
        "use svnmucc to access the repository"
        return self._subprocess(self.svnmucc or 'svnmucc', *args)

    def look(self, *args):
        "use svnlook to access the repository"
        modargs = [arg for arg in args]
        for arg in modargs:
            # if --revision HEAD, just omit the argument, because svnlook doesn't like or need it.
            if arg=='--revision' and modargs[modargs.index(arg)+1] in ['HEAD', None]:
                modargs.remove(modargs[modargs.index(arg)+1])
                modargs.remove(arg)
        return self._subprocess(self.svnlook or 'svnlook', *modargs)

    def _subprocess(self, cmd, *args):
        """uses subprocess.check_output to get and return the output of svn or svnmucc,
        or raise an error if the cmd raises an error.
        """
        stderr = tempfile.NamedTemporaryFile()
        cmdlist = [cmd]
        if 'svnlook' not in cmd:
            cmdlist += ['--non-interactive']
            if self.trust_server_cert==True and 'svnmucc' not in cmd:
                cmdlist += ['--trust-server-cert']
            if self.username is not None:
                cmdlist += ['--username', self.username]
            if self.password is not None:
                cmdlist += ['--password', self.password]
        cmdlist += list(args)
        cmdlist = list(cmdlist)
        # self.log_("['" + "', '".join(cmdlist) + "']")
        # The following overcomes a bug in svn: svn needs os.curdir to be something sensible.
        os.chdir(os.environ.get('HOME') or self.local or self.parent_path)
        try:
            res = subprocess.check_output(cmdlist, stderr=stderr)
            return res
        except subprocess.CalledProcessError as e:
            with open(stderr.name, 'r') as f:
                output = f.read()
            self.log_(traceback.format_exc())
            self.log_(output)
            raise RuntimeError(output).with_traceback(sys.exc_info()[2]) from None

    # == USER API COMMANDS == 

    def cat(self, url, rev=None, peg=None):
        if self.local not in [None, '']:
            # fast: svnlook cat
            path = os.path.relpath(URL(url).unquoted(), str(self.url.unquoted()))
            args = ['cat']
            if rev is not None: args += ['--revision', rev]
            args += [self.local, path]
            return self.look('cat', '--revision', rev, self.local, path)
        else:
            # slow: svn cat
            url = URL(url).quoted()
            if peg is not None or rev is not None:
                url += '@'+(peg or rev).split(':')[-1]
            args = []
            if rev is not None: args += ['--revision', rev] 
            args += [url]
            return self('cat', *args)

    def copy(self, src_url, dest_url, msg='', rev=None, peg=None):
        src_url = URL(src_url).quoted()
        dest_url = URL(dest_url).quoted()
        if peg is not None or rev is not None:
            src_url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None: args += ['--revision', rev]
        args += ['--message', msg, src_url, dest_url]
        return self('copy', *args)

    def delete(self, *urls, msg='', force=False):
        args = ['--message', msg]
        if force==True:
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('delete', *args)

    def diff(self, *args):
        return self('diff', *args)

    def export(self, src_url, dest_path, rev=None, peg=None, depth='infinity'):
        src_url = URL(src_url).quoted()
        if peg is not None or rev is not None:
            src_url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None: args += ['--revision', rev]
        args += ['--depth', depth, src_url, dest_path]
        return self('export', *args)

    def filesize(self, url, rev=None, peg=None):
        if self.local not in [None, '']:
            # fast: svnlook filesize
            path = os.path.relpath(URL(url).unquoted(), str(self.url.unquoted()))
            args = []
            if rev is not None: args += ['--revision', rev]
            args += [self.local, path]
            return int(self.look('filesize', *args))
        else:
            # slow: svn cat
            return len(self.cat(url, rev=rev, peg=peg))

    def importe(self, src_path, dest_url, msg='', depth='infinity', force=False):
        args = ['--message', msg, '--depth', depth]
        if force==True: args.append('--force')
        args += [src_path, URL(dest_url).quoted()]
        return self('import', *args)

    def info(self, url, rev=None, peg=None, depth='empty', verbose=True, xml=True):
        url = URL(url).quoted()
        if peg is not None or rev is not None:
            url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None: args += ['--revision', rev.split(':')[0]]
        args += ['--depth', depth]
        if xml==True: args.append('--xml')
        if verbose==True and xml!=True: 
            args.append('--verbose')
        args.append(url)
        return self('info', *args)

    def list(self, url, rev=None, peg=None, depth='infinity', verbose=True, xml=True):
        url = URL(url).quoted()
        if peg is not None or rev is not None:
            url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None: args += ['--revision', rev.split(':')[0]]
        ['--depth', depth]
        if xml==True: 
            args.append('--xml')
        if verbose==True and xml != True: 
            args.append('--verbose')
        args.append(url)
        return self('list', *args)

    def lock(self, *urls, msg='', force=False): 
        args = ['--message', msg]
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        self('lock', *args)

    def log(self, url=None, rev=None, peg=None, search=None, verbose=True, xml=True):
        url = URL(url or self.url).quoted()
        if peg is not None or rev is not None:
            url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None:
            args += ['--revision', rev]
        if search is not None: args += ['--search', search]
        if verbose==True: args.append('--verbose')
        if xml==True: args.append('--xml')
        args.append(url)
        return self('log', *args)

    def mkdir(self, url, msg='', parents=True):
        args = ['--message', msg]
        if parents==True: 
            args.append('--parents')
        args.append(URL(url).quoted())
        return self('mkdir', *args)

    def move(self, src_url, dest_url, msg='', rev=None, peg=None, force=False):
        src_url = URL(src_url).quoted()
        dest_url = URL(dest_url).quoted()
        if peg is not None or rev is not None:
            url += '@'+(peg or rev).split(':')[-1]
        args = []
        if rev is not None: args += ['--revision', rev]
        args += ['--message', msg]
        if force==True: 
            args.append('--force')
        args += [src_url, dest_url]
        return self('move', *args)

    def put(self, path, dest_url, msg=''):
        args = ['--message', msg, path, URL(dest_url).quoted()]
        return self.mucc('put', *args)

    def remove(self, *urls, msg='', force=False):
        args = ['--message', msg]
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('remove', *args)

    def unlock(self, *urls, force=False):
        args = []
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('unlock', *args)

    # == Properties == 

    def proplist(self, url, rev=None, peg=None, depth='infinity', 
            xml=True, verbose=True, inherited=True, changelist=None):
        url = URL(url).quoted()
        args = []
        if rev is not None: args += ['--revision', rev] 
        if xml==True: args += ['--xml']
        if verbose==True: args += ['--verbose']
        if inherited==True: args += ['--show-inherited-props']
        if self.local not in [None, '']:
            # fast: svnlook cat
            path = os.path.relpath(URL(url).unquoted(), str(self.url.unquoted()))
            args += [self.local, path]
            return etree.XML(self.look('proplist', *args))
        else:
            if peg is not None or rev is not None:
                url += '@'+(peg or rev).split(':')[-1]                
            if changelist is not None: args += ['--changelist', changelist]
            args += [url]
            return self('proplist', *args)

    def propget(self, name, url, rev=None, peg=None, depth='infinity', xml=True):
        pass

    def propset(self, name, url, msg='', depth='infinity', force=False):
        pass

    def propdel(self, name, url, depth='infinity'):
        pass

    def propedit(self, name, url, rev=None, msg='', force=False):
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
