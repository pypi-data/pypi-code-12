import os
import sys
from ._fmap import fmap

#-------------------------------------------------------------------------------

DESCRIPTION = '''Recusively apply a command to a filesystem tree.
'''

def process_args(args):
    import argparse
    parser = argparse.ArgumentParser(prog='fmap', description=DESCRIPTION)

    parser.add_argument('-p', '--preview', dest='preview', default=False,
                        action='store_true',
                        help="Doesn't apply the command. Instead, prints " 
                        "command invocations that would be performed.")
    parser.add_argument('-v', '--verbose', dest='verbose', default=False,
                        action='store_true',
                        help="Print command invocations as they are performed.")
    parser.add_argument('-d', '--apply-dirs', dest='apply_dirs', default=False,
                        action='store_true',
                        help="Apply the command to directories after it "
                        "is applied to files at each level of the tree.")
    parser.add_argument('-l', '--follow-links', dest='follow_links', 
                        default=False, action='store_true',
                        help="Follow symbolic links.")
    parser.add_argument('-b', '--bottom-up', dest='top_down', default=True,
                        action='store_false',
                        help="Walk the tree from the bottom up. By default, "
                        "the tree is traversed from the top down.")
    parser.add_argument('-z', '--max-depth', dest="max_depth", default=-1,
                        type=int,
                        help="Maximum recursion depth. Any negative number "
                        "results in unlimited recursion.  Default is -1.")
    parser.add_argument('-x', '--exclude', action='append', metavar='PATTERN',
                        dest='excludes',
                        help="Unix pattern that specifies "
                        "which files to exclude applying the command to.")
    parser.add_argument('-r', '--root', type=str, dest='root', metavar='DIR',
                        default=os.getcwd(),
                        help='Directory in which to begin the traversal. Is '
                        'the current directory by default.')
    parser.add_argument('command', metavar='CMD', type=str,
                        help="The command to apply. The file to be applied may "
                        "be optionally specified by '{}'. If '{}' is not "
                        "supplied, the file will be passed in as the last "
                        "argument.")
    parser.add_argument('patterns', metavar='PATTERN', nargs='*', 
                        help="Unix filename pattern that specifies "
                        "which files to apply the command to.")
    
    opts = parser.parse_args(args)
    if opts.preview:
        opts.verbose = True
    if '{}' not in opts.command:
        opts.command += ' {}'
    if not opts.patterns:
        opts.patterns = ['*']

    return opts

#-------------------------------------------------------------------------------

def main(*args):
    if not args:
        args = sys.argv[1:]
    
    opts = process_args(args)
    fmap(**vars(opts))

#-------------------------------------------------------------------------------
