"""A module containing functions related to search"""
import re
import os
import curses
import logging

from . import util

SEARCH_STRING_JUMP_FORWARD = 'forward'
SEARCH_STRING_JUMP_BACKWARD = 'backward'
BBLAMEHST_PATH = os.path.join(os.path.expanduser('~'), '.bblamehst')
HISTORY_LIMIT = 50


def find_search_locs(scr_content, search_str):
    """find all the indexes of lines that contain the search string"""
    search_locs = []
    if search_str:
        for idx, (line_str, line_attrs) in enumerate(scr_content):
            if search_str in line_str:
                search_locs.append(idx)
            if idx == len(scr_content) - 1:
                break
    return search_locs


def tokenize_line_search(search_str, line, line_attrs):
    """generate a list of tuples, each tuple is a chunk of the line,
    representing essentially an inclusive "split" of the line by the
    search pattern. The schema of the tuple is:
    (<str, line chunk>,
     <bool, should chunk be highlighted>,
     <extra curses string attributes for>)
    """
    def search_map(string, line_attrs):
        """If string matches the search pattern set to_highlight to True"""
        to_highlight = string == search_str
        return (string, to_highlight, line_attrs)

    search_str_re = re.escape(search_str)
    tokenized_str = re.split('(%s)' % search_str_re, line)
    logging.info('SEARCH: tokens %s', tokenized_str)
    return [search_map(token, line_attrs) for token in tokenized_str]


def read_search_history():
    """Load the stored search history from disk. File is .bblamehst.
    History is limited to 50 entries"""
    if os.path.isfile(BBLAMEHST_PATH):
        with open(BBLAMEHST_PATH, 'r') as bblamehst_file:
            return bblamehst_file.read().splitlines()
    else:
        return []


def write_search_history(history):
    """Write the stored search history to disk. File is ~/.bblamehst
    History is limited to 50 entries"""
    with open(BBLAMEHST_PATH, 'w') as bblamehst_file:
        for search_pattern in history:
            bblamehst_file.write(search_pattern + '\n')


def add_search_str_to_history(search_history, search_str):
    """Add the search_str to the search history to be written to disk.
    Ensuring to keep the history <= the history limit"""
    search_history.insert(0, search_str)
    logging.info('search history: %s', search_history)
    return search_history[-HISTORY_LIMIT:]


def append_string(txtbox, str_to_append):
    """Add string to the texteditpad textbox. This is not an append, will
    overwrite the existing text"""
    txtbox.text = [str_to_append]
    set_txtbox_cursor_pos(txtbox, 0, len(str_to_append))
    txtbox.redraw_vlines(txtbox.vptl, (0, 0))


def clear_search_txtbox(txtbox):
    """Clear the current text from the txtbox"""
    if len(''.join(txtbox.text)) > 0:
        txtbox.text = ['']
        set_txtbox_cursor_pos(txtbox, 0, 0)
        txtbox.redraw_vlines(txtbox.vptl, (0, 0))


def set_txtbox_cursor_pos(txtbox, x_pos, y_pos):
    """Set the cursor position of the texteditpad cursor"""
    txtbox.ppos = (x_pos, y_pos)  # physical position of the cursor
    txtbox.vpos = (x_pos, y_pos)  # virtual position of the cursor


def collect_search_string(txtbox):
    """Collect the search string from the user. Handling each charcter
    inputted into the txtbox, and handling the result
    """
    search_history = read_search_history()
    history_iter = util.BidirectionalCycle(search_history, no_wrap=True)
    logging.info("SEARCH: history iter %s", history_iter)
    while True:
        char = txtbox.win.getch()
        if len(''.join(txtbox.text)) == 0:
            history_enabled = True
        # Enter key breaks out of the collection loop
        if char == curses.KEY_ENTER or char == ord('\n'):
            break
        # Handle backspace here if the textbox is empty, if so, exit the
        # collection loop
        elif char in [8, curses.KEY_BACKSPACE, curses.KEY_DC] and \
                len(''.join(txtbox.text)) == 0:
            return
        # Handle key up and down here if the textbox is empty, if so, cycle
        # through the past search history
        elif char in [curses.KEY_DOWN,
                      curses.KEY_UP] and history_iter and history_enabled:
            clear_search_txtbox(txtbox)
            if char == curses.KEY_UP:
                next_search = next(history_iter)
            else:
                next_search = history_iter.prev()
            append_string(txtbox, next_search)
            logging.info('SEARCH: history next: %s', next_search)
        # Pass the key off to the textpad to handle from here
        else:
            history_enabled = False
            txtbox.do_command(char)

    search_str = ''.join(txtbox.text)
    search_history = add_search_str_to_history(search_history, search_str)
    write_search_history(search_history)
    return search_str
