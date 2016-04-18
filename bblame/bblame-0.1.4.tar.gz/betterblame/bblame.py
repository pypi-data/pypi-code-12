"""Entry point/main module that handles initial argument parsing and setup of
the main curses loop, that waits for user input, reacts, and redraws the screen
"""
import curses
import os
import sys
import errno
import argparse
import logging

import sh

from . import screen
from . import git
from . import actions
from . import modes
logging.basicConfig(filename='/tmp/bblame.log',
                    format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
                    datefmt='%b-%d %H:%M',
                    level=logging.DEBUG)


def curses_loop(stdscr, args):
    """main curses application loop to be fed to curses wrapper, which handles
    initializing of the screen and first blame and the user input handling loop
    """
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    git.init_git_color_pairs()
    scrobj = screen.Screen(stdscr, args.filename, args.revision)
    actiontable = actions.ActionTable(scrobj)
    if args.line_num_or_search_term:
        if isinstance(args.line_num_or_search_term, int):
            initial_line = args.line_num_or_search_term
            scrobj.init_line_arg(initial_line)
        else:
            scrobj.search_str = args.line_num_or_search_term
            scrobj.update_search_locs()
            run_and_log_user_errors(scrobj,
                                    scrobj.jump_to_next_search_string)
    scrobj.redraw_screen()

    # start waiting for and acting on user input
    while True:
        # wait for char from user
        char = scrobj.getch()

        # check if escape, if so return to normal mode
        if scrobj.check_for_escape(char):
            if scrobj.mode in [modes.MODE_VISUAL, modes.MODE_HELP]:
                scrobj.mode = modes.MODE_NORMAL
            elif scrobj.mode == modes.MODE_SHOW:
                scrobj.restore_prev_content_and_state()

        # Process the key with the action table
        run_and_log_user_errors(scrobj, actiontable.process_key, char)

        # log some state each iteration and redraw the screen
        scrobj.log_state(args.debug)
        scrobj.redraw_screen()


def run_and_log_user_errors(screenobject, func, *args):
    """Run <func> with <args> in a try/except for UserError, display any such
    errors to the user on the status bar and continue.
    Any other exceptions will crash the application.
    Returns the return value of the function or the UserError that was caught
    and logged."""
    try:
        return func(*args)
    except screen.UserError as exc:
        screenobject.set_status_bar_next_msg(str(exc),
                                             attributes=curses.A_BOLD |
                                             curses.A_STANDOUT)


def process_args():
    """Process the input to bblame, then return the file name to be
    passed to the main function"""

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--revision', '-r',
                           metavar='{revision}', default='',
                           help='The revision to initialize the blame file to')
    argparser.add_argument('--debug', action='store_true', default=False,
                           help='Increase logging and show tracebacks')
    argparser.add_argument('filename', help='Name or path to file to blame')
    # These args are positional and prefixed with '+' to match vim.
    # Both are captured in the same argparse positional arg (must be positional
    # because arg parse doesn't allow options that start with a char other than
    # '-') and then it's parsed below
    argparser.add_argument('line_num_or_search_term', nargs='?',
                           metavar='+{line_num} or +/{search_pattern}',
                           help='The line number or search pattern the cursor '
                                'will be positioned on (this arg will put '
                                'bblame in visual mode)')
    args = argparser.parse_args()
    logging.info('Command line arguments: ' + str(args))
    if args.line_num_or_search_term:
        if args.line_num_or_search_term.startswith('+/'):
            # search term was passed in
            args.line_num_or_search_term = \
                args.line_num_or_search_term.strip('+/')
        elif args.line_num_or_search_term.startswith('+'):
            # Line number was passed in
            try:
                args.line_num_or_search_term = \
                    int(args.line_num_or_search_term.strip('+'))
            except ValueError as exc:
                # It certainly does have a message member, from baseException
                # pylint: disable=no-member
                if 'invalid literal for int' in exc.message:
                    print('Invalid input for line number')
                    sys.exit(1)
        else:
            print('Invalid positional argument: %s'
                  % args.line_num_or_search_term)
            sys.exit(1)
    try:
        os.stat(args.filename)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            print(os.strerror(errno.ENOENT))
            exit(errno.ENOENT)
    return args


def main():
    """main callable that handles argument parsing the and then calls
    the curses_loop with the parsed arguments.
    Also sets up a few global settings and moves the cwd of the application
    to the appropriate location."""
    # reduce ESCAPE delay from 1s to 25ms
    os.environ['ESCDELAY'] = "25"
    # Process arguments passed from user
    args = process_args()
    # Move cwd to git root dir, to make simplify git commands later.
    # Filenames may be relative to a sub dir (bblame ../../tests/mytestfile)
    # so recreate the path relative to the git root (tests/mytestfile) since
    # the application is run from git root.
    git_root = sh.git('rev-parse', '--show-toplevel').stdout.strip()
    # Python os[.path] funcs were failing me, so using ol' faithful linux shell
    abs_file_path = sh.readlink('-f', '%s'
                                % args.filename).stdout.strip().decode('UTF-8')
    args.filename = abs_file_path.replace(git_root.decode('UTF-8'),
                                          '').strip('/')
    os.chdir(git_root)
    try:
        # Enter curses loop
        curses.wrapper(curses_loop, args)
    except sh.ErrorReturnCode_128 as exc:
        if args.debug:
            # debug enabled, raise the whole stack trace
            raise exc
        else:
            # Just return the error message from git
            print(exc.stderr)
    except (git.BadRevException, git.NoSuchRevException) as exc:
        # It certainly does have a message member, from baseException
        # pylint: disable=no-member
        print(exc.message)

if __name__ == "__main__":
    main()
