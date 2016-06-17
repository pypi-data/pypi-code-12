"""Module that holds the mapping of key press to action.
Holding that mapping, along with some metadata about each mapping (user
readable title and description of the action) in a data structure makes the
main keypress loop and generating a help/man document much simpler."""
import curses
from curses import ascii as curses_ascii
import types
import logging

from . import modes


CURSES_KEY_TO_STR = {key_int: key_str[4:] for key_str, key_int in
                     list(vars(curses).items())
                     if key_str.startswith('KEY_')}


# Yeah, I know it has a lot of public methods, this is intended
# pylint: disable=too-many-public-methods
class ActionTable(object):
    """a class for accepting keys and performing actions"""
    def __init__(self, scrobj):
        self.screen = scrobj
        self._init_action_tables()

    # Not using self here, but I don't want this to be a staticmethod
    # pylint: disable=no-self-use
    def quit_action(self):
        """Quit the application"""
        # For now just exit
        exit(0)

    def resize_action(self):
        """Resize the screens on a resize event"""
        logging.info('RESIZE EVENT')
        self.screen.resize_windows()
        self.screen.redraw_screen()

    def search_action(self):
        """Start the search string editor to get the users search string
        and handle it"""
        if self._if_mode_normal() or self._if_mode_show:
            self.screen.get_search_string()

    def next_search_action(self):
        """Jump to the next search match (in the downward direction)"""
        if self._if_mode_normal() or self._if_mode_show:
            self.screen.jump_to_next_search_string()

    def prev_search_action(self):
        """Jump to the prev search match (in the upward direction)"""
        if self._if_mode_normal() or self._if_mode_show:
            self.screen.jump_to_previous_search_string()

    def vis_select_action(self):
        """Enter visual select mode (only from normal mode)"""
        if self._if_mode_normal():
            self.screen.init_vis_cursor()

    def show_line_commit_aciton(self):
        """Show a commit selected by the visual mode cursor"""
        if self._if_mode_visual():
            self.screen.init_git_show()

    def show_file_commit_aciton(self):
        """Show the current file commit"""
        self.screen.init_git_show_file()

    def parent_action(self):
        """Open a new git blame to the parent of the current commit"""
        self.screen.add_blame_parent()

    def ancestor_action(self):
        """Open a new git blame to the ancestor of the current commit"""
        self.screen.add_blame_ancestor()

    def drill_action(self):
        """Drill down past the commit highlighted in visual mode.
           Opens a new git blame"""
        if self._if_mode_visual():
            self.screen.add_blame_drill()

    def pop_action(self):
        """Pop back to previous git object"""
        self.screen.restore_prev_content_and_state()

    def move_up_action(self):
        """move the screen or visual select cursor up"""
        # if mode is visual, move line highlight
        if self._if_mode_visual():
            self.screen.move_cursor_up()
        # if mode is normal, move screen
        else:
            self.screen.move_scr_up()

    def move_down_action(self):
        """move the screen or visual select cursor down"""
        # if mode is visual, move line highlight
        if self._if_mode_visual():
            self.screen.move_cursor_down()
        # if mode is normal, move screen
        else:
            self.screen.move_scr_down()

    def page_up_action(self):
        """Move the screen up one page"""
        self.screen.move_scr_up_page()

    def page_down_action(self):
        """Move the screen down one page"""
        self.screen.move_scr_down_page()

    def page_right_action(self):
        """Move the screen half a page to the right"""
        self.screen.move_scr_right_hpage()

    def page_left_action(self):
        """Move the screen half a page to the left"""
        self.screen.move_scr_left_hpage()

    def jump_top_action(self):
        """Jump to the top of the screen"""
        self.screen.move_scr_to_top()

    def jump_bottom_action(self):
        """Jump to the bottom of the screen"""
        self.screen.move_scr_to_bottom()

    def help_action(self):
        """Display the help message"""
        help_msg = self.generate_help()
        self.screen.display_help(help_msg)

    def _if_mode_normal(self):
        """check if the screen obj is in NORMAL mode"""
        return self.screen.mode == modes.MODE_NORMAL

    def _if_mode_visual(self):
        """check if the screen obj is in VISUAL mode"""
        return self.screen.mode == modes.MODE_VISUAL

    def _if_mode_show(self):
        """check if the screen obj is in SHOW mode"""
        return self.screen.mode == modes.MODE_SHOW

    def process_key(self, key):
        """Take a key and check if we have a corresponding action, if so call
        the action function, and log the keypress"""
        isascii = curses_ascii.isascii(key)
        ascii_key = chr(key) if isascii else None
        logging.info('Actions - process_key: KEY PRESSED (int, ascii), '
                     '(%s, %s)', key, ascii_key)
        action = self.key_to_action.get(key, None)
        if action:
            logging.info('Actions. process_key: Action func: %s',
                         str(action['action_name']))
            action['action_func']()
            return True
        else:
            logging.info('Actions - process_key: Key not in action table')
        return False

    def generate_help(self):
        """Automagically generate a help document from the action descriptions
        in the action table"""

        def stringify_key(key):
            """Convert key ints into curses strings for displaying in the help
            text."""
            if isinstance(key, int):
                key_str = CURSES_KEY_TO_STR.get(key)
                if key_str:
                    return key_str
                else:
                    return ''
            return key
        help_lines = []
        help_lines.append('KEYS: ACTION - DESCRIPTION')
        help_lines.append('--------------------------')
        for keys, action in self.keys_to_action:
            if action['show_in_help_msg']:
                keys_strs = [stringify_key(key) for key in keys]
                keys_str = ', '.join([_f for _f in keys_strs if _f])
                action_name = action['action_name']
                action_desc = action['action_desc']
                help_lines.append(' %s:   %s' % (keys_str, action_name))
                help_lines.append('    %s' % (action_desc))
                help_lines.append('')
        return help_lines

    @staticmethod
    def _create_action_entry(action_name, action_func, action_desc='',
                             show_in_help_msg=False):
        """Given inputs, validate they are at least of the right type and
        create a action table entry
         Schema of a single entry:
         <keys_list>: {'action_name': <name of action str>,
                       'acton_desc': <short description of action str>,
                       'action_func': <action_function to call>
                       'show_in_help_msg': <bool>
                       }
        """
        assert isinstance(action_name, str)
        assert isinstance(action_desc, str)
        assert isinstance(action_func, types.MethodType)
        assert isinstance(show_in_help_msg, bool)

        # If no action provided use func doc
        if not action_desc:
            action_desc = action_func.__doc__

        # sanitize the desc to have no new lines or spaces/margins
        clean_lines = [x.strip() for x in action_desc.splitlines()]

        return {'action_name': action_name,
                'action_desc': ' '.join(clean_lines),
                'action_func': action_func,
                'show_in_help_msg': show_in_help_msg}

    KEYS_TUPLE_TO_ACTION2 = []

    def _init_action_tables(self):
        """Generate a list of tuples that map keys to an action that they
        perform"""
        self.keys_to_action = [
            (['q'], self._create_action_entry('Quit', self.quit_action,
                                              'Quit the application', True)),
            ([curses.KEY_RESIZE],
             self._create_action_entry('Screen Resize',
                                       self.resize_action)),
            (['/'], self._create_action_entry('Search', self.search_action,
                                              'Search for single line strings',
                                              True)),
            (['n'], self._create_action_entry('Next Search Match',
                                              self.next_search_action,
                                              self.next_search_action.__doc__,
                                              True)),
            (['N'], self._create_action_entry('Prev Search Match',
                                              self.prev_search_action,
                                              self.prev_search_action.__doc__,
                                              True)),
            (['v', 's'],
             self._create_action_entry('Visual Select Mode',
                                       self.vis_select_action,
                                       self.vis_select_action.__doc__, True)),
            (['o'],
             self._create_action_entry('Show/View Commit',
                                       self.show_line_commit_aciton,
                                       self.show_line_commit_aciton.__doc__,
                                       True)),

            (['O'],
             self._create_action_entry('Show/View file Commit',
                                       self.show_file_commit_aciton,
                                       self.show_file_commit_aciton.__doc__,
                                       True)),

            ([10, curses.KEY_ENTER, 'd'],
             self._create_action_entry('Drill Down', self.drill_action,
                                       self.drill_action.__doc__, True)),
            (['<', ','],
             self._create_action_entry('Parent blame', self.parent_action,
                                       self.parent_action.__doc__, True)),
            (['>', '.'],
             self._create_action_entry('Ancestor blame', self.ancestor_action,
                                       self.ancestor_action.__doc__, True)),
            ([8, curses.KEY_BACKSPACE, curses.KEY_DC, 127, 'f'],
             self._create_action_entry('Pop Back', self.pop_action,
                                       self.pop_action.__doc__, True)),
            (['k', curses.KEY_UP],
             self._create_action_entry('Move Up',
                                       self.move_up_action)),
            (['j', curses.KEY_DOWN],
             self._create_action_entry('Move Down',
                                       self.move_down_action)),
            ([curses.KEY_PPAGE],
             self._create_action_entry('Move Up Page',
                                       self.page_up_action)),
            ([curses.KEY_NPAGE],
             self._create_action_entry('Move Down Page',
                                       self.page_down_action)),
            ([curses.KEY_RIGHT],
             self._create_action_entry('Move Right Page',
                                       self.page_right_action)),
            ([curses.KEY_LEFT],
             self._create_action_entry('Move Left Page',
                                       self.page_left_action)),
            (['g', curses.KEY_HOME],
             self._create_action_entry('Jump to Top',
                                       self.jump_top_action)),
            (['G', curses.KEY_END],
             self._create_action_entry('Jump to Bottom',
                                       self.jump_bottom_action)),
            (['h'], self._create_action_entry('Help', self.help_action,
                                              'Generate Help Message', True)),
        ]

        # Create a second mapping of each single key (as its int keycode) to
        # the action, to make single key lookups easier in main loop
        self.key_to_action = {}
        for keys, action in self.keys_to_action:
            for key in keys:
                if isinstance(key, int):
                    self.key_to_action[key] = action
                elif isinstance(key, str):
                    # convert char to int key code
                    assert len(key) == 1, "Keys must be a single char!"
                    self.key_to_action[ord(key)] = action
