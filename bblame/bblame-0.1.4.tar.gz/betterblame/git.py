"""Classes and utility functions related to git data and operations on it"""
import os
import gc
import itertools
import curses
import zlib

import sh

from .util import buildlinesdict


class BadRevException(Exception):
    """Simple custom exception to make exception handling easier up the
    stack"""
    pass


class NoSuchRevException(Exception):
    """Simple custom exception to make exception handling easier up the
    stack"""
    pass

ABBREV_LEN = 8
# Git blame appears to show always n+1 chararcters of the shaw, where n is
# the number of chars you actually asked for...
ABBREV_LEN_BLAME = ABBREV_LEN - 1
# Git color pair names
GIT_COLOR_OLD = 8
GIT_COLOR_NEW = 9
GIT_COLOR_FRAG = 10
GIT_COLOR_FUNC = 11
GIT_COLOR_SHOW = 12
GIT_COLOR_META = 13
# Git hunk constants
GIT_HUNK_MODIFIED_ADDED = 'ma'
GIT_HUNK_MODIFIED_REMOVED = 'mr'


def init_git_color_pairs():
    """ init git color pairs
    Note: -1 maps to default background color"""
    curses.init_pair(GIT_COLOR_OLD, curses.COLOR_RED, -1)
    curses.init_pair(GIT_COLOR_NEW, curses.COLOR_GREEN, -1)
    curses.init_pair(GIT_COLOR_FRAG, curses.COLOR_CYAN, -1)
    curses.init_pair(GIT_COLOR_FUNC, curses.COLOR_BLUE, -1)
    curses.init_pair(GIT_COLOR_SHOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(GIT_COLOR_META, curses.COLOR_MAGENTA, -1)


def get_head_rev(filename):
    """Get the revision pointed to by HEAD"""
    cmd = ['rev-list', '--abbrev=%d' % ABBREV_LEN, '--max-count=1',
           'HEAD', '--', filename]
    return get_commit_helper(cmd)


def get_commit_helper(cmds):
    """Get the ancestor of <current_rev>"""
    git = sh.git.bake(_cwd=os.getcwd())
    revlist = git(*cmds)
    if not revlist.splitlines():
        raise NoSuchRevException()
    else:
        # return the firs 8 chars of the revision
        return revlist.splitlines()[-1][:8]


# pylint: disable=too-few-public-methods
class GitLog(object):
    """A class to represent the git log"""

    class LogEntry(object):
        """A class object to represent an entry of the git log.
        Stores the sha and filename for that commit, and references to this
        commits parent and ancestor"""
        # pylint: disable=too-many-arguments
        def __init__(self, sha, filename, desc, parent=None, ancestor=None):
            self.sha = sha
            self.filename = filename
            self.desc = desc
            self.parent = parent
            self.ancestor = ancestor

    def __init__(self, initial_filename):
        self.gitlog = {}
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        initial_log = git.log('--no-color', '--abbrev=%d' % ABBREV_LEN,
                              '--follow', '--oneline', '--name-only', '--',
                              '%s' % initial_filename)
        previous_log_entry = None
        for sha_and_desc, filename in zip(*[iter(initial_log.splitlines())]*2):
            sha = sha_and_desc.split()[0]
            desc = str(' '.join(sha_and_desc.split()[1:]))
            curr_log_entry = self.LogEntry(sha, filename, desc,
                                           ancestor=previous_log_entry)
            if previous_log_entry:
                previous_log_entry.parent = curr_log_entry
            self.gitlog[sha] = curr_log_entry
            previous_log_entry = curr_log_entry

    def __getitem__(self, item):
        return self.gitlog[item]

    def __str__(self):
        return self.gitlog.__str__()

    def __iter__(self):
        return self.gitlog.__iter__()

    def __len__(self):
        return self.gitlog.__len__()


class Blame(object):
    """A class to represent a blame.

    Attributes:
        git_sha - The SHA of the git commit being blamed if one
        filename - The name of the file we are blaming
        lines - The output of git blame by line in a default dict
    """
    def __init__(self, filename, git_sha=''):
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        self.filename = filename
        if git_sha:
            try:
                cmd = [git_sha, '--abbrev=%d' % ABBREV_LEN_BLAME,
                       '--', filename]
                self.lines = buildlinesdict(
                    git.blame(*cmd).stdout.splitlines())
            except sh.ErrorReturnCode_128 as exc:
                if "no such path" in exc.message:
                    raise NoSuchRevException(exc.stderr)
                if "bad revision" in exc.message:
                    raise BadRevException(exc.stderr)
                raise
            self.git_sha = git_sha
        else:
            self.git_sha = get_head_rev(filename)
            self.lines = buildlinesdict(git.blame(
                '--abbrev=%d' % ABBREV_LEN_BLAME,
                filename).stdout.splitlines())
        # lines will grow if any '~' padding is added
        self.numlines = len(self.lines)
        del git
        gc.collect()

    def compress(self):
        """Compress the lines attribute which stores the content of the git
        blame. This makes storing each stack frame cheaper"""
        blame_text = '\n'.join([line[0] for line in self.lines.values()])
        compressed_lines = zlib.compress(blame_text.encode())
        del self.lines
        gc.collect()
        self.lines = compressed_lines

    def decompress(self):
        """Decompress the lines attribute which stores the content of the git
        blame."""
        temp_lines = zlib.decompress(self.lines)
        self.lines = buildlinesdict(temp_lines.splitlines())
        del temp_lines
        gc.collect()

    def __len__(self):
        return self.numlines

    def __getitem__(self, index):
        return self.lines[index]

    def __setitem__(self, index, value):
        self.lines[index] = value


class Show(object):
    """A class to represent a git show.

    Attributes:
        showobj - The function object returned by sh.git, contains attributes
                   like the return code of the command, the stdout, etc.
        git_sha - The SHA of the git commit being showed
    """
    def __init__(self, git_sha):
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        showobj = git.show('--no-color', git_sha)
        self.git_sha = git_sha
        self.lines = buildlinesdict(showobj.stdout.splitlines())
        self.colorize_lines()
        del git
        del showobj
        gc.collect()

    def colorize_lines(self):
        """Add the necessary curses attributes to each line to produce the
        desired color, highlight, etc"""
        iter_lines = self.lines.items()
        for line_idx, (line_str, line_attrs) in iter_lines:
            # commit header
            if line_str.startswith('commit'):
                self.lines[line_idx] = (line_str,
                                        curses.color_pair(GIT_COLOR_SHOW))

            # meta information block
            elif line_str.startswith('diff'):
                self.lines[line_idx] = (line_str,
                                        curses.color_pair(GIT_COLOR_META))
                for line_idx, (line_str,
                               line_attrs) in itertools.islice(iter_lines, 3):
                    self.lines[line_idx] = (line_str,
                                            curses.A_DIM |
                                            curses.color_pair(GIT_COLOR_META))
            # hunk/fragment header
            elif line_str.startswith('@@'):
                # TODO: tease out function in hunk header
                self.lines[line_idx] = (line_str,
                                        curses.color_pair(GIT_COLOR_FRAG))

            # added lines
            elif line_str.startswith('+'):
                self.lines[line_idx] = (line_str,
                                        curses.color_pair(GIT_COLOR_NEW))

            # removed lines
            elif line_str.startswith('-'):
                self.lines[line_idx] = (line_str,
                                        curses.color_pair(GIT_COLOR_OLD))

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    def __setitem__(self, index, value):
        self.lines[index] = value
