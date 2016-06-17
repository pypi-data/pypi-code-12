"""Screen object reacts to user input updating the curses screen"""
import curses
import logging

import texteditpad

from . import modes
from . import search
from . import git
from . import contentstack

from .util import BidirectionalCycle, buildlinesdict


class BadModeException(Exception):
    """Simple exception to make exception handling easier up the stack"""
    pass


class UserError(Exception):
    """Simple exception to make exception handling easier up the stack"""
    pass


class Screen(object):
    """The main class that bridges between the curses screen object and one
    or more blame or git show objects. Containing functions that are triggered
    by user interaction with the application which modify and/or read
    screen/git state.

    Attributes:
        stdscr - The curses screen object
        cursor_line - The current line the cursor is on. Relative to the
                      visible screen, E.g.: cursor_line is always between
                      0 and screen height
        current_line - The current line of content, zero indexed from the top.
                       E.g. After freshly opening a blame, current_line is 0,
                            after scrolling down 5 lines, current_line is 4
        current_width - similar to current
        search_locs_iter - bidirectional iterator of the indexes to lines that
                           contain the current search pattern
        content_stack - A stack to keep track of git blame/show objects as
                        you browse file commit history and show commits.
        mode - The current mode bblame is in, see modes.py for more details
        search_str - current search string, if any.
    """

    def __init__(self, stdscr, filename, revision):
        self.parent_stdscr = stdscr
        self.cursor_line = 0
        self.current_line = 0
        self.current_width = 0
        self.search_locs_iter = None
        self.mode = modes.MODE_NORMAL
        self.content_stack = contentstack.ContentStack()
        self.gitlog = git.GitLog(filename)
        self.search_str = None

        self.resize_windows()  # prepares the subwindows
        self.set_status_bar_next_msg('')
        self._add_content_to_stack(git.Blame(filename, revision))

    @staticmethod
    def setup_screen(scr):
        """setup screens
        set scrollingok and idlok for scrolling)
        set keypad for use of arrow keys
        """
        scr.scrollok(1)
        scr.idlok(1)
        scr.keypad(True)

    def resize_windows(self):
        """Partition stdscr into properly sized subwindows"""
        parent_stdscr = self.parent_stdscr
        height, width = parent_stdscr.getmaxyx()
        self.stdscr = parent_stdscr.derwin(height-1, width, 0, 0)
        self.status_bar = parent_stdscr.derwin(1, width, height-1, 0)
        self.setup_screen(self.stdscr)
        self.setup_screen(self.status_bar)
        self.setup_screen(parent_stdscr)

    def clear_scr(self):
        """clear the screen"""
        self.stdscr.clear()

    def erase_status_bar(self):
        """erase the screen"""
        self.status_bar.erase()

    def clear_status_bar(self):
        """clear the screen"""
        self.status_bar.erase()

    def refresh_scr(self):
        """refresh the screen"""
        self.stdscr.refresh()

    def refresh_status_bar(self):
        """refresh the statusbar"""
        self.status_bar.refresh()

    def getch(self, nodelay=False):
        """wait for char with delay or not"""
        self.stdscr.nodelay(nodelay)
        char = self.stdscr.getch()
        self.stdscr.nodelay(False)
        return char

    def check_for_escape(self, char):
        """Check if the escape key was pressed, which is tricky as the Alt
        key combos also use escape"""
        if char == 27:
            # At this point we don't know if it was ESC or an ALT key combo
            # Grab another key to see if it was an ALT combo
            next_char = self.getch(nodelay=True)
            esc = False
            if next_char == -1:
                # Escape was pressed
                esc = True
            # NOTE: Don't care about ALT right now so just drop it on the floor
            #       if it was.
            return esc

    def _get_max_yx(self):
        """return the max width and height of the screen"""
        return self.stdscr.getmaxyx()

    def _get_visible_content_len(self):
        """get the length of visible content, I.e. the number of lines of
        blame or git show that are visible to the user"""
        screen_h, screen_w = self._get_max_yx()
        scr_content = self._get_current_scr_content()
        return min(len(scr_content) - self.current_line, screen_h)

    def add_blame_parent(self):
        """Add blame of the parent of the current rev to the content stack"""
        curr_rev = self._get_current_scr_content().git_sha
        git_log_entry = self.gitlog[curr_rev]
        self._add_blame(git_log_entry.parent)

    def add_blame_ancestor(self):
        """Add blame of the ancestor of the current rev to the content stack"""
        curr_rev = self._get_current_scr_content().git_sha
        git_log_entry = self.gitlog[curr_rev]
        self._add_blame(git_log_entry.ancestor)

    def add_blame_drill(self):
        """Add a blame to the content stack for the revision under
        the cursor"""
        rev_to_drill = self._get_cursor_rev()
        if rev_to_drill == '0'*len(rev_to_drill):
            # This is likely a non-committed change. The parent of a
            # non-committed change is HEAD of the file
            git_log_entry = self.gitlog[self._get_current_scr_content().git_sha]
            self._add_blame(git_log_entry.parent)
        elif rev_to_drill.startswith('^'):
            # This is a boundary commit, can't drill past this
            raise UserError('Can\'t drill past boundary commit, no parent')
        else:
            git_log_entry = self.gitlog[rev_to_drill]
            self._add_blame(git_log_entry.parent)

    def _add_blame(self, git_log_entry):
        """Add a blame to the content stack. Takes the file we're blaming and
        a function that when called returns the revision of the file we're
        blaming"""
        try:
            if git_log_entry is None:
                logging.warning('YOU HAVE REACHED THE BOTTOM OF THE WELL!')
                current_rev = self._get_current_scr_content().git_sha
                raise UserError('Error: No commit before %s', current_rev)
            filename = git_log_entry.filename
            revision = git_log_entry.sha
            newblame = git.Blame(filename, '%s' % revision)
        except git.BadRevException:
            logging.warning('BAD REV SELECTED! %s', revision)
            raise UserError('Error: bad revision (%s) selected', revision)
        self._add_content_to_stack(newblame)
        self.update_search_locs()
        self.mode = modes.MODE_NORMAL

    def _get_current_scr_content(self):
        """return the current screen content"""
        stackframe = self.content_stack.peek()
        return stackframe.content

    def _add_content_to_stack(self, content):
        """Add content to the content_stack, along with the current state
        needed to restore the screen after we remove it"""
        self.content_stack.add(content, self.current_line, self.current_width,
                               self.cursor_line, self.mode)

    def restore_prev_content_and_state(self):
        """delete the current frame of the content stack, restore the
        snapshot of the previous screen state it stored"""
        try:
            stackframe = self.content_stack.pop()
        except IndexError:
            raise UserError('No content to pop')

        self.current_line = stackframe.last_current_line
        self.current_width = stackframe.last_current_width
        self.cursor_line = stackframe.last_cursor_line
        self.mode = stackframe.last_mode

        self.update_search_locs()

    def display_help(self, help_msg):
        """display help"""
        self.mode = modes.MODE_HELP
        self._add_content_to_stack(buildlinesdict(help_msg))

    def _get_cursor_rev(self):
        """return the git revision under the cursor.
        Only in visual mode and not in show mode"""
        if self.mode != modes.MODE_VISUAL or self.mode == modes.MODE_SHOW:
            raise BadModeException('Cannot get cursor revision in mode (%s)',
                                   self.mode)
        cursline_2_bline = self.cursor_line + self.current_line - 1
        line_str, line_attrs = self._get_line(cursline_2_bline)
        # the first component of the line is the git rev
        return line_str.split()[0]

    def _get_line(self, line):
        """Return the content at index <line> from the current content being
        displayed and the attributes of that line"""
        scr_content = self._get_current_scr_content()
        return scr_content[line]

    def set_status_bar_next_msg(self, content,
                                attributes=curses.A_DIM | curses.A_STANDOUT):
        """Set a message to be displayed in the status bar on the next screen
        refresh. Returns a tuple with the message content and any
        attributes"""
        self.status_bar_next_msg = (content, attributes)

    def set_status_bar_next_msg_bold(self, content):
        """Set a message to be displayed in the status bar on the next screen
        refresh with bold attribute"""
        # This attr is set in __init__ but in a function call, so pylint
        # misses it
        # pylint: disable=attribute-defined-outside-init
        self.status_bar_next_msg = (content, curses.A_BOLD | curses.A_STANDOUT)

    def get_status_bar_content(self):
        """Return content to be displayed in the status bar. A standard
        template for each mode will be displayed unless an explicit status
        bar messages was set to be displayed"""
        scr_content = self._get_current_scr_content()
        height, width = self._get_max_yx()
        ret_msg = ''
        ret_attrs = curses.A_DIM | curses.A_STANDOUT

        if self.status_bar_next_msg[0]:
            ret_msg, ret_attrs = self.status_bar_next_msg
            self.set_status_bar_next_msg("")
        elif self.mode == modes.MODE_HELP:
            ret_msg = 'Help'
        else:
            git_sha = scr_content.git_sha
            if self.mode == modes.MODE_SHOW:
                ret_msg = '%s: %s' % ('show', git_sha)
            else:
                filename = scr_content.filename
                ret_msg = '%s: %s (%s)' % ('blame', filename, git_sha)
        return ret_msg, ret_attrs

    def _draw_status_bar(self):
        """Fetch the correct content to be displayed in the status bar and
        draw it in the status bar window."""
        content, attributes = self.get_status_bar_content()
        _, width = self._get_max_yx()
        content.ljust(width-1)
        # If the message is too long for the width of the screen, truncate it
        # and add an ellipses to indicate we've done so.
        if len(content) > width - 1:
            content = content[:width-4] + '...'

        self.erase_status_bar()
        self.status_bar.addstr(content[:width-1], attributes)
        self.refresh_status_bar()

    def init_git_show_file(self):
        """Setup for a git show for the file commit"""
        git_sha = self._get_current_scr_content().git_sha
        self.init_git_show(git_sha)

    def init_git_show(self, rev_to_show=None):
        """Setup for a git show"""
        rev = rev_to_show if rev_to_show else self._get_cursor_rev()
        show = git.Show(rev)
        self._add_content_to_stack(show)
        self.mode = modes.MODE_SHOW
        # Snap to top of git show
        self.current_line = 0
        self.current_width = 0
        self.update_search_locs()

    def get_search_string(self):
        """Get search string using texteditpad and some trickery"""
        # Create a subwindow in the statusbar to contain the single line
        # Textbox editor
        screen_h, screen_w = self._get_max_yx()
        # Create massive window to avoid hitting max width
        temp_search_win = curses.newwin(1, 900, screen_h, 1)
        txtbox = texteditpad.Textbox(temp_search_win, insert_mode=True)
        # Clear the status bar of status indicators, and print the search
        # string entry '/'
        self.clear_status_bar()
        self.status_bar.addstr(0, 0, '/')
        self.refresh_status_bar()
        # Enable the cursor and begin excepting text until the user hits return
        curses.curs_set(1)
        self.search_str = search.collect_search_string(txtbox)
        curses.curs_set(0)
        logging.info('SEARCH: search string: %s~', self.search_str)
        self.update_search_locs()
        self.jump_to_next_search_string()

    def jump_to_next_search_string(self):
        """Jump to the next search string"""
        self._jump_to_search_string_helper(search.SEARCH_STRING_JUMP_FORWARD)

    def jump_to_previous_search_string(self):
        """Jump to the previous search string"""
        self._jump_to_search_string_helper(search.SEARCH_STRING_JUMP_BACKWARD)

    def _jump_to_search_string_helper(self, direction):
        """Jump to next search string in <direction>"""
        if self.search_locs_iter is not None:
            try:
                if direction == search.SEARCH_STRING_JUMP_FORWARD:
                    self.current_line = next(self.search_locs_iter)
                elif direction == search.SEARCH_STRING_JUMP_BACKWARD:
                    self.current_line = self.search_locs_iter.prev()
                else:
                    raise Exception('Unknown search direction (%s) passed',
                                    direction)
            except StopIteration:
                self.set_status_bar_next_msg_bold('Error: Pattern not found')
        else:
            logging.info('No search pattern entered')

    def init_line_arg(self, content_line):
        """Setup the screen given the provided <content_line> from the user,
        passed from the command line.
        This is roughly:
            - centre the screen on that line if possible (stopping at top or
              bottom of content).
            - enable visual mode (placing the cursor on the location of the
              screen that is over overtop of <content_line>)."""
        screen_h, screen_w = self._get_max_yx()
        screen_loc_of_line = self._center_screen_on_line(content_line)
        self.init_vis_cursor(screen_loc_of_line)

    def init_vis_cursor(self, cursor_line=None):
        """init visual select cursor mode.
        Move to the correct mode and initialize the cursor to a either
        the provided line <cursor_line> or the default (in the middle of
        the visible content)"""
        self.mode = modes.MODE_VISUAL
        screen_h, screen_w = self._get_max_yx()
        # If our blame has less lines than height, then we want to init
        # the cursor to the middle of the blame content, not into the middle
        # of the screen which could be off of the edge of file content
        self.cursor_line = cursor_line if cursor_line \
            else self._get_visible_content_len()//2

    def _center_screen_on_line(self, line):
        """Centers the screen around the line of the blame as best as possible.
        Returns the location on the viewable screen space, where the line we
        wanted to center on ended up. In most cases this will indeed be the
        center (height/2) but may be elsewhere if we've reached the end of the
        git blame"""
        screen_h, screen_w = self._get_max_yx()
        scrn_content_len = len(self._get_current_scr_content())
        if line < screen_h//2:
            # Centering the screen at a line which would leave less than half
            # a screen height worth of content above wouldn't leave us with
            # enough content to fill the screen, so cap it at 0
            self.current_line = 0
        elif line > (scrn_content_len - screen_h//2 - 1):
            # Same as above but we'd run off the bottom of the content, cap
            # things such that we have at least one screens worth of content
            # to display.
            self.current_line = scrn_content_len - screen_h
        else:
            self.current_line = line - screen_h//2
        return max(1, min(line - self.current_line, screen_h))

    def _re_center_screen(self):
        """Called to recenter the screen.
        Redrawing the screen after drilling into a blame or popping back may
        leave all or part of the screen outside of the content, so recenter
        the screen on the new/changed content"""
        scrn_content = self._get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        # recenter the screen if we're out of the content
        if self.current_line > len(scrn_content):
            if len(scrn_content) < screen_h//2:
                self.current_line = 0
            else:
                self.current_line = len(scrn_content) - screen_h//2
        # recenter the visual mode cursor if it's outside the content
        if self.cursor_line > self._get_visible_content_len():
            self.cursor_line = self._get_visible_content_len()//2

    def _highlight_for_vis_cursor(self, content_index):
        """determines whether the current line should be highlighted for
        visual mode cursor"""
        # Pylint doesn't see both halves of the and as one. (no need for '\'
        # inside parens either)
        # pylint: disable=pointless-statement
        if (self.mode == modes.MODE_VISUAL and
                content_index == (self.cursor_line - 1)):
            return True
        else:
            False

    def update_search_locs(self):
        """Creates a bi-directional iterator of all lines that contain the
        search pattern."""
        scr_content = self._get_current_scr_content()
        search_locs = search.find_search_locs(scr_content, self.search_str)
        self.search_locs_iter = BidirectionalCycle(search_locs)
        logging.info('SEARCH: Done updating search locs')

    def _draw_mapped_tokens(self, mapped_tokens, current_index):
        """Draw line that is a list of tokens for search.
        This process is novel because the tokens have different curses attrs,
        so they must be added to the scr in pieces, and we also must be
        careful to stay within the current screen y position and width"""
        screen_h, screen_w = self._get_max_yx()
        curr_x_pos = start_pos = 0
        for token_str, highlight_for_search, token_attrs in mapped_tokens:
            token_len = len(token_str)
            if curr_x_pos == 0:
                # Until we've started printing the line check how much, if
                # any, of the current token fits in the screen width, it may
                # need to be clipped
                len_before_begin = (start_pos + token_len) - self.current_width
                if len_before_begin < 0:
                    # Line not yet in the current width, (I.e. The user has
                    # shifted the screen over to the right, and the token we're
                    # currently processing doesn't fall in the viewable area
                    start_pos += token_len
                    continue
                # clip the token, as only part of it is in the viewable area
                token_str = token_str[token_len-len_before_begin:]
                token_len = len(token_str)
            # Check if the token will go past the width of the screen
            len_past_end = (curr_x_pos + token_len) - screen_w + 1
            if len_past_end > 0:
                # line would be longer than screen width, so trim
                token_str = token_str[0:-len_past_end]
            # If the current visual cursor line contains a search match, then
            # invert the highlight of the match so it still stands out
            if self._highlight_for_vis_cursor(current_index):
                highlight_for_search = not highlight_for_search
            if highlight_for_search:
                self.stdscr.addstr(current_index, curr_x_pos, token_str,
                                   curses.A_STANDOUT | token_attrs)
            else:
                self.stdscr.addstr(current_index, curr_x_pos,
                                   token_str, token_attrs)
            # Increment the x position by the length of the token we've added
            curr_x_pos += token_len
            if len_past_end > 0:
                break

    def redraw_screen(self):
        """Clear and redraw the screen, print each line and be sure to
        highlight the cursor line if we are in visual mode"""
        self.log_state()
        self.clear_scr()
        self._re_center_screen()
        screen_h, screen_w = self._get_max_yx()
        # <line> is the index to the actual line of text from the file that's
        # being printed to the screen at line <idx>. <idx> is always between 0
        # and height of the screen
        for idx, line in enumerate(range(self.current_line,
                                         self.current_line + screen_h)):
            str_to_add, str_attrs = self._get_line(line)
            if self.search_locs_iter and line in self.search_locs_iter:
                # This line contains at least one instance of the search string
                mapped_tokens = search.tokenize_line_search(self.search_str,
                                                            str_to_add,
                                                            str_attrs)
                logging.info('MAPPED_TOKENS: %s', mapped_tokens)
                self._draw_mapped_tokens(mapped_tokens, idx)
                continue
            curr_width = self.current_width
            # Only print as much of the line that will fit in the screen width
            str_to_add = str_to_add[curr_width:curr_width+screen_w-1]
            if self._highlight_for_vis_cursor(idx):
                self.stdscr.addstr(idx, 0, str_to_add,
                                   curses.A_STANDOUT | str_attrs)
                continue
            self.stdscr.addstr(idx, 0, str_to_add, str_attrs)
        self.refresh_scr()
        self._draw_status_bar()

    def move_scr_down_page(self):
        """Move down by a page or less if there isn't a page full of content
        left"""
        scr_content = self._get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        len_left = len(scr_content) - self.current_line - screen_h
        if (len_left) > 0:
            decr = min(len_left, screen_h)
            self.current_line += decr

    def move_scr_up_page(self):
        """move up by a page or less if there isn't a page full of content
        left"""
        screen_h, screen_w = self._get_max_yx()
        if self.current_line > 0:
            incr = min(screen_h, self.current_line)
            self.current_line -= incr

    def move_scr_right_hpage(self):
        """Move screen to the right by half a page width"""
        screen_h, screen_w = self._get_max_yx()
        self.current_width += screen_w//2

    def move_scr_left_hpage(self):
        """Move screen to the left by half a page width"""
        screen_h, screen_w = self._get_max_yx()
        if self.current_width > 0:
            self.current_width -= screen_w//2

    def move_scr_down(self):
        """move the screen down one line if we haven't reached the bottom yet
        """
        scr_content = self._get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        if (len(scr_content) - self.current_line - screen_h) > 0:
            self.current_line += 1

    def move_scr_to_top(self):
        """snap screen to top of content"""
        self.current_line = 0

    def move_scr_to_bottom(self):
        """snap screen to bottom of content"""
        scr_content = self._get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        self.current_line = len(scr_content) - screen_h

    def move_scr_up(self):
        """move the screen up one lines if we haven't reached the top yet"""
        if self.current_line > 0:
            self.current_line -= 1

    def move_cursor_down(self):
        """Move the highlighted cursor line down by one line line"""
        visable_content_len = self._get_visible_content_len()
        if self.cursor_line <= visable_content_len:
            if self.cursor_line == visable_content_len:
                # highlight is at the bottom of the screen
                self.move_scr_down()
            else:
                self.cursor_line += 1

    def move_cursor_up(self):
        """Move the highlighted cursor line up by one line line"""
        if self.cursor_line > 0:
            if self.cursor_line == 1:
                # highlight is at the top of the screen
                self.move_scr_up()
            else:
                self.cursor_line -= 1

    def log_state(self, debug=False):
        """print some state to a log file"""
        if debug:
            content = self._get_current_scr_content()
            screen_h, screen_w = self._get_max_yx()
            logging.info('Content stack len: %s', len(self.content_stack))
            logging.info('Mode: %s', self.mode)
            logging.info('Screen height: %s', screen_h)
            logging.info('Screen width: %s', screen_w)
            logging.info('Current line: %s', self.current_line)
            logging.info('Current width: %s', self.current_width)
            logging.info('Cursor line: %s', self.cursor_line)
            logging.info('Length of file: %s', len(content))
            logging.info('Length of file exposed: %d',
                         self._get_visible_content_len())
            logging.info('length of file - currline %s',
                         (len(content) - self.current_line))
            logging.info('range: %s\n',
                         str(range(self.current_line,
                                   self.current_line + screen_h)))
