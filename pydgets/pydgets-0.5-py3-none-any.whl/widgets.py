#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) 2015-2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Console widget library.
"""

import os
import sys
import textwrap
import argparse
import datetime
import time
import pprint

DFLT_TABLE_STYLE = 'utf8.b'
TERMINAL_WIDTH   = 0
TERMINAL_HEIGHT  = 0

DATA_TYPES = {
    'int':      lambda x: '{:,d}'.format(int(x)),
    'float':    lambda x: '{:,.3f}'.format(float(x)),
    'percent':  lambda x: '{:6.2f}'.format(float(x)),
    'sizekb':   lambda x: '{:,.2f}'.format(float(x)/1024),
    'sizemb':   lambda x: '{:,.2f}'.format(float(x)/1024/1024),
    'sizegb':   lambda x: '{:,.2f}'.format(float(x)/1024/1024/1024),
    'duration': lambda x: str(datetime.timedelta(seconds=int(x))),
}

# Index of terminal formating options
TEXT_FORMATING = {
    'attr': {
        'bold':      '\033[1m',
        'dark':      '\033[2m',
        'underline': '\033[4m',
        'blink':     '\033[5m',
        'reverse':   '\033[7m',
        'concealed': '\033[8m',
    },
    'fg': {
        'grey':    '\033[30m',
        'red':     '\033[31m',
        'green':   '\033[32m',
        'yellow':  '\033[33m',
        'blue':    '\033[34m',
        'magenta': '\033[35m',
        'cyan':    '\033[36m',
        'white':   '\033[37m',
        #'2purple':   '\033[95m',
        #'2cyan':     '\033[96m',
        #'2darkcyan': '\033[36m',
        #'2blue':     '\033[94m',
        #'2green':    '\033[92m',
        #'2yellow':   '\033[93m',
        #'2red':      '\033[91m',
    },
    'bg': {
        'on_grey':    '\033[40m',
        'on_red':     '\033[41m',
        'on_green':   '\033[42m',
        'on_yellow':  '\033[43m',
        'on_blue':    '\033[44m',
        'on_magenta': '\033[45m',
        'on_cyan':    '\033[46m',
        'on_white':   '\033[47m',
    },
    'rst': '\033[0m',
}

TEXT_ALIGNMENT = {
    '<': '<', 'l': '<', 'left':   '<', 'L': '<', 'LEFT':   '<',
    '>': '>', 'r': '>', 'right':  '>', 'R': '>', 'RIGHT':  '>',
    '^': '^', 'c': 'c', 'center': 'c', 'C': 'c', 'CENTER': 'c', 
}

# Index of box/table border drawing characters (https://en.wikipedia.org/wiki/Box-drawing_character)
BORDER_STYLES = {
    'none': {
        'th': '', 'tv': '', 'tl': '', 'tm': '', 'tr': '',
        'mh': '', 'mv': '', 'ml': '', 'mm': '', 'mr': '',
        'bh': '', 'bv': '', 'bl': '', 'bm': '', 'br': ''
    },
    'space': {
        'th': ' ', 'tv': ' ', 'tl': ' ', 'tm': ' ', 'tr': ' ',
        'mh': ' ', 'mv': ' ', 'ml': ' ', 'mm': ' ', 'mr': ' ',
        'bh': ' ', 'bv': ' ', 'bl': ' ', 'bm': ' ', 'br': ' '
    },
    'ascii.a': {
        'th': '-', 'tv': '|', 'tl': '+', 'tm': '+', 'tr': '+',
        'mh': '-', 'mv': '|', 'ml': '+', 'mm': '+', 'mr': '+',
        'bh': '-', 'bv': '|', 'bl': '+', 'bm': '+', 'br': '+'
    },
    'ascii.b': {
        'th': '-', 'tv': '|', 'tl': '+', 'tm': '+', 'tr': '+',
        'mh': '=', 'mv': '|', 'ml': '#', 'mm': '#', 'mr': '#',
        'bh': '-', 'bv': '|', 'bl': '+', 'bm': '+', 'br': '+'
    },
    'ascii.c': {
        'th': '=', 'tv': '|', 'tl': '#', 'tm': '#', 'tr': '#',
        'mh': '=', 'mv': '|', 'ml': '#', 'mm': '#', 'mr': '#',
        'bh': '=', 'bv': '|', 'bl': '#', 'bm': '#', 'br': '#'
    },
    'ascii.d': {
        'th': '=', 'tv': '|', 'tl': '#', 'tm': '#', 'tr': '#',
        'mh': '=', 'mv': '|', 'ml': '#', 'mm': '#', 'mr': '#',
        'bh': '-', 'bv': '|', 'bl': '+', 'bm': '+', 'br': '+'
    },
    'ascii.e': {
        'th': '#', 'tv': '#', 'tl': '#', 'tm': '#', 'tr': '#',
        'mh': '#', 'mv': '#', 'ml': '#', 'mm': '#', 'mr': '#',
        'bh': '#', 'bv': '#', 'bl': '#', 'bm': '#', 'br': '#'
    },
    'utf8.a': {
        # Alternativelly define the characters with unicode codes
        #'th': '\u2500', 'tv': '\u2502', 'tl': '\u250c', 'tm': '\u252c', 'tr': '\u2510',
        #'mh': '\u2500', 'mv': '\u2502', 'ml': '\u251c', 'mm': '\u253c', 'mr': '\u2524',
        #'bh': '\u2500', 'bv': '\u2502', 'bl': '\u2514', 'bm': '\u2534', 'br': '\u2518'
        'th': '─', 'tv': '│', 'tl': '┌', 'tm': '┬', 'tr': '┐',
        'mh': '─', 'mv': '│', 'ml': '├', 'mm': '┼', 'mr': '┤',
        'bh': '─', 'bv': '│', 'bl': '└', 'bm': '┴', 'br': '┘'
    },
    'utf8.b': {
        'th': '═', 'tv': '║', 'tl': '╔', 'tm': '╦', 'tr': '╗',
        'mh': '═', 'mv': '║', 'ml': '╠', 'mm': '╬', 'mr': '╣',
        'bh': '═', 'bv': '║', 'bl': '╚', 'bm': '╩', 'br': '╝'
    },
    'utf8.c': {
        'th': '━', 'tv': '┃', 'tl': '┏', 'tm': '┳', 'tr': '┓',
        'mh': '━', 'mv': '┃', 'ml': '┣', 'mm': '╋', 'mr': '┫',
        'bh': '━', 'bv': '┃', 'bl': '┗', 'bm': '┻', 'br': '┛'
    },
    'utf8.d': {
        'th': '─', 'tv': '│', 'tl': '┌', 'tm': '┬', 'tr': '┐',
        'mh': '═', 'mv': '│', 'ml': '╞', 'mm': '╪', 'mr': '╡',
        'bh': '─', 'bv': '│', 'bl': '└', 'bm': '┴', 'br': '┘'
    },
    'utf8.e': {
        'th': '─', 'tv': '│', 'tl': '┌', 'tm': '┬', 'tr': '┐',
        'mh': '━', 'mv': '│', 'ml': '┝', 'mm': '┿', 'mr': '┥',
        'bh': '─', 'bv': '│', 'bl': '└', 'bm': '┴', 'br': '┘'
    },
    'utf8.f': {
        'th': '═', 'tv': '║', 'tl': '╔', 'tm': '╦', 'tr': '╗',
        'mh': '─', 'mv': '║', 'ml': '╟', 'mm': '╫', 'mr': '╢',
        'bh': '═', 'bv': '║', 'bl': '╚', 'bm': '╩', 'br': '╝'
    },
    'utf8.g': {
        'th': '━', 'tv': '┃', 'tl': '┏', 'tm': '┳', 'tr': '┓',
        'mh': '─', 'mv': '┃', 'ml': '┠', 'mm': '╂', 'mr': '┨',
        'bh': '━', 'bv': '┃', 'bl': '┗', 'bm': '┻', 'br': '┛'
    }
}

# Index of list drawing characters (https://en.wikipedia.org/wiki/List_of_Unicode_characters)
LIST_STYLES = {
    'none':    '',
    'ascii.a': '-',
    'ascii.b': '+',
    'ascii.c': '*',
    'ascii.d': '#',
    'ascii.e': '>',
    'ascii.f': '=',
    'ascii.g': '->',
    'ascii.h': '=>',

    'utf8.a': '–',
    'utf8.b': '•',
    'utf8.c': '◦',
    'utf8.d': '○',
    'utf8.e': '◉',
    'utf8.f': '◎',
    'utf8.g': '◾',
    'utf8.h': '◽',
    'utf8.i': '■',
    'utf8.j': '□',
    'utf8.k': '‣',
    'utf8.l': '▶',
    'utf8.m': '▷',
    'utf8.n': '◆',
    'utf8.o': '◇',
    'utf8.p': '◈',
    'utf8.q': '◗',
    'utf8.r': '◖',
    'utf8.s': '⁍',
    'utf8.t': '⁌',
    'utf8.u': '☛',
    'utf8.v': '☞',
    'utf8.w': '⁕',
    'utf8.x': '›',
    'utf8.y': '→',
    'utf8.z': '⇒',
    'utf8.0': '⇛',
    'utf8.1': '⇨',
    'utf8.2': '⇾',
}

TREE_STYLES = {
    'none': {
        'non': '',
        'ver': '',
        '111': '',
        '11x': '',
        '1xx': '',
        '1xl': '',
        'x11': '',
        'x1x': '',
        'xxx': '',
        'xxl': '',
    },
    'ascii.a': {
        'non': ' ',
        'ver': '',
        '111': '-',
        '11x': '-',
        '1xx': '-',
        '1xl': '-',
        'x11': '-',
        'x1x': '-',
        'xxx': '-',
        'xxl': '-',
    },
    'ascii.b': {
        'non': '  ',
        'ver': BORDER_STYLES['ascii.a']['tv']+' ',                             # vertical separator
        '111': BORDER_STYLES['ascii.a']['th']+BORDER_STYLES['ascii.a']['th'],  # first level, first and only item
        '11x': BORDER_STYLES['ascii.a']['tm']+BORDER_STYLES['ascii.a']['th'],  # first level, first item, something coming next
        '1xx': BORDER_STYLES['ascii.a']['ml']+BORDER_STYLES['ascii.a']['th'],  # first level, other items
        '1xl': BORDER_STYLES['ascii.a']['bl']+BORDER_STYLES['ascii.a']['th'],  # first level, last item
        'x11': BORDER_STYLES['ascii.a']['bl']+BORDER_STYLES['ascii.a']['th'],  # next levels, first and only item
        'x1x': BORDER_STYLES['ascii.a']['ml']+BORDER_STYLES['ascii.a']['th'],  # next levels, first item, something coming next
        'xxx': BORDER_STYLES['ascii.a']['ml']+BORDER_STYLES['ascii.a']['th'],  # next levels, other items
        'xxl': BORDER_STYLES['ascii.a']['bl']+BORDER_STYLES['ascii.a']['th'],  # next levels, last item
    },
    'utf8.a': {
        'non': '  ',
        'ver': BORDER_STYLES['utf8.a']['tv']+' ',                            # vertical separator
        '111': BORDER_STYLES['utf8.a']['th']+BORDER_STYLES['utf8.a']['th'],  # first level, first and only item
        '11x': BORDER_STYLES['utf8.a']['tm']+BORDER_STYLES['utf8.a']['th'],  # first level, first item, something coming next
        '1xx': BORDER_STYLES['utf8.a']['ml']+BORDER_STYLES['utf8.a']['th'],  # first level, other items
        '1xl': BORDER_STYLES['utf8.a']['bl']+BORDER_STYLES['utf8.a']['th'],  # first level, last item
        'x11': BORDER_STYLES['utf8.a']['bl']+BORDER_STYLES['utf8.a']['th'],  # next levels, first and only item
        'x1x': BORDER_STYLES['utf8.a']['ml']+BORDER_STYLES['utf8.a']['th'],  # next levels, first item, something coming next
        'xxx': BORDER_STYLES['utf8.a']['ml']+BORDER_STYLES['utf8.a']['th'],  # next levels, other items
        'xxl': BORDER_STYLES['utf8.a']['bl']+BORDER_STYLES['utf8.a']['th'],  # next levels, last item
    },
    'utf8.b': {
        'non': '  ',
        'ver': BORDER_STYLES['utf8.b']['tv']+' ',                            # vertical separator
        '111': BORDER_STYLES['utf8.b']['th']+BORDER_STYLES['utf8.b']['th'],  # first level, first and only item
        '11x': BORDER_STYLES['utf8.b']['tm']+BORDER_STYLES['utf8.b']['th'],  # first level, first item, something coming next
        '1xx': BORDER_STYLES['utf8.b']['ml']+BORDER_STYLES['utf8.b']['th'],  # first level, other items
        '1xl': BORDER_STYLES['utf8.b']['bl']+BORDER_STYLES['utf8.b']['th'],  # first level, last item
        'x11': BORDER_STYLES['utf8.b']['bl']+BORDER_STYLES['utf8.b']['th'],  # next levels, first and only item
        'x1x': BORDER_STYLES['utf8.b']['ml']+BORDER_STYLES['utf8.b']['th'],  # next levels, first item, something coming next
        'xxx': BORDER_STYLES['utf8.b']['ml']+BORDER_STYLES['utf8.b']['th'],  # next levels, other items
        'xxl': BORDER_STYLES['utf8.b']['bl']+BORDER_STYLES['utf8.b']['th'],  # next levels, last item
    },
    'utf8.c': {
        'non': '  ',
        'ver': BORDER_STYLES['utf8.c']['tv']+' ',                            # vertical separator
        '111': BORDER_STYLES['utf8.c']['th']+BORDER_STYLES['utf8.c']['th'],  # first level, first and only item
        '11x': BORDER_STYLES['utf8.c']['tm']+BORDER_STYLES['utf8.c']['th'],  # first level, first item, something coming next
        '1xx': BORDER_STYLES['utf8.c']['ml']+BORDER_STYLES['utf8.c']['th'],  # first level, other items
        '1xl': BORDER_STYLES['utf8.c']['bl']+BORDER_STYLES['utf8.c']['th'],  # first level, last item
        'x11': BORDER_STYLES['utf8.c']['bl']+BORDER_STYLES['utf8.c']['th'],  # next levels, first and only item
        'x1x': BORDER_STYLES['utf8.c']['ml']+BORDER_STYLES['utf8.c']['th'],  # next levels, first item, something coming next
        'xxx': BORDER_STYLES['utf8.c']['ml']+BORDER_STYLES['utf8.c']['th'],  # next levels, other items
        'xxl': BORDER_STYLES['utf8.c']['bl']+BORDER_STYLES['utf8.c']['th'],  # next levels, last item
    },
}

#-------------------------------------------------------------------------------

def terminal_size():
    """
    Detect the size of terminal window in rows and columns.
    """
    try:
        (rows, columns) = os.popen('stty size', 'r').read().split()
        rows    = int(rows)
        columns = int(columns)
        return (columns, rows)
    
    # Currently ignore any errors and return some reasonable default values.
    except:
        pass
    return (80, 24)

(TERMINAL_WIDTH, TERMINAL_HEIGHT) = terminal_size()

#-------------------------------------------------------------------------------

class ConsoleWidget:
    """
    Base class for all console widgets.

    This class provides basic common methods for widget setup and rendering.
    """
    
    SETTING_FLAG_PLAIN = 'plain'
    """
    Widget setting: Plain only output flag
    
    Setting this flag to True will force the widget to be displayed without any
    fancy terminal formating (colors, emphasis, etc.).
    """
    
    SETTING_FLAG_ASCII = 'ascii'
    """
    Widget setting: ASCII only output flag

    Setting this flag to True will force the widget to be displayed using only
    ASCII characters.
    """
    
    SETTING_WIDTH          = 'width'
    SETTING_ALIGN          = 'align'
    
    SETTING_TEXT_FORMATING = 'text_formating'
    
    SETTING_DATA_FORMATING = 'data_formating'
    SETTING_DATA_TYPE      = 'data_type'
    
    SETTING_PADDING        = 'padding'
    SETTING_PADDING_CHAR   = 'padding_char'
    SETTING_PADDING_LEFT   = 'padding_left'
    SETTING_PADDING_RIGHT  = 'padding_right'
    
    SETTING_MARGIN         = 'margin'
    SETTING_MARGIN_CHAR    = 'margin_char'
    SETTING_MARGIN_LEFT    = 'margin_left'
    SETTING_MARGIN_RIGHT   = 'margin_right'
    
    def __init__(self, content = None, **kwargs):
        """
        Default object constructor.
        """
        self._settings = {}
        for setting in self.list_settings():
            self._settings[setting[0]] = kwargs.get(setting[0], setting[1])
        self.setup(content, **kwargs)
    
    def __str__(self):
        """
        Overloaded operator for direct string output.
        """
        return self.render()
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.

        The returned list is then used setup() and get_setup() methods to setup
        the widget internal settings.
        """
        return [
            (self.SETTING_FLAG_PLAIN, False),
            (self.SETTING_FLAG_ASCII, False),
            (self.SETTING_WIDTH, 0),
            (self.SETTING_ALIGN, '<'),
            (self.SETTING_TEXT_FORMATING, {}),
            (self.SETTING_DATA_FORMATING, '{:s}'),
            (self.SETTING_DATA_TYPE, None),
            (self.SETTING_PADDING, None),
            (self.SETTING_PADDING_CHAR, ' '),
            (self.SETTING_PADDING_LEFT, None),
            (self.SETTING_PADDING_RIGHT, None),
            (self.SETTING_MARGIN, None),
            (self.SETTING_MARGIN_CHAR, ' '),
            (self.SETTING_MARGIN_LEFT, None),
            (self.SETTING_MARGIN_RIGHT, None),
        ]
    
    def setup(self, content = None, **kwargs):
        """
        Store settings internally.
        """
        self.content = content

        for setting in self.list_settings():
            if setting[0] in kwargs:
                self._settings[setting[0]] = kwargs.get(setting[0])
    
    def get_setup(self, content = None, **kwargs):
        """
        Get current setup by combining internal settings with the one given.
        """
        if content is None:
            content = self.content
        if content is None:
            raise Exception("No content given to be displayed")

        setup = {}
        for setting in self.list_settings():
            if setting[0] in kwargs:
                setup[setting[0]] = kwargs.get(setting[0])
            else:
                setup[setting[0]] = self._settings.get(setting[0])

        return (content, setup)
    
    #---------------------------------------------------------------------------
    
    @staticmethod
    def _es(settings, *keys):
        """
        Extract given subset of widget settings.
        """
        return {k: settings[k] for k in keys}
    
    @staticmethod
    def _es_data(settings):
        """
        Extract data formating related subset of widget settings.
        """
        return {k: settings[k] for k in (ConsoleWidget.SETTING_DATA_FORMATING,
                                         ConsoleWidget.SETTING_DATA_TYPE)}
    
    @staticmethod
    def _es_content(settings):
        """
        Extract content formating related subset of widget settings.
        """
        return {k: settings[k] for k in (ConsoleWidget.SETTING_WIDTH,
                                         ConsoleWidget.SETTING_ALIGN,
                                         ConsoleWidget.SETTING_PADDING,
                                         ConsoleWidget.SETTING_PADDING_LEFT,
                                         ConsoleWidget.SETTING_PADDING_RIGHT,
                                         ConsoleWidget.SETTING_PADDING_CHAR)}
    
    @staticmethod
    def _es_text(settings, text_formating = {}):
        """
        Extract text formating related subset of widget settings.
        """
        s = {k: settings[k] for k in (ConsoleWidget.SETTING_FLAG_PLAIN,)}
        s.update(text_formating)
        return s
    
    @staticmethod
    def _es_margin(settings):
        """
        Extract margin formating related subset of widget settings.
        """
        return {k: settings[k] for k in (ConsoleWidget.SETTING_MARGIN,
                                         ConsoleWidget.SETTING_MARGIN_LEFT,
                                         ConsoleWidget.SETTING_MARGIN_RIGHT,
                                         ConsoleWidget.SETTING_MARGIN_CHAR)}
    
    #---------------------------------------------------------------------------
    
    @staticmethod
    def calculate_width_widget(width, margin = None, margin_left = None, margin_right = None):
        """
        Calculate actual widget width based on given margins.
        """
        if margin_left is None:
            margin_left = margin
        if margin_right is None:
            margin_right = margin
        if margin_left is not None:
            width -= int(margin_left)
        if margin_right is not None:
            width -= int(margin_right)
        return width if width > 0 else None
    
    @staticmethod
    def calculate_width_content(width, margin = None, margin_left = None, margin_right = None, padding = None, padding_left = None, padding_right = None):
        """
        Calculate actual widget content width based on given margins and paddings.
        """
        if margin_left is None:
            margin_left = margin
        if margin_right is None:
            margin_right = margin
        if margin_left is not None:
            width -= int(margin_left)
        if margin_right is not None:
            width -= int(margin_right)
        if padding_left is None:
            padding_left = padding
        if padding_right is None:
            padding_right = padding
        if padding_left is not None:
            width -= int(padding_left)
        if padding_right is not None:
            width -= int(padding_right)
        return width if width > 0 else None
    
    @staticmethod
    def fmt_data(text, data_formating = None, data_type = None):
        """
        Format given text according to given data formating pattern or data type.
        """
        if data_type:
            return DATA_TYPES[data_type](text)
        elif data_formating:
            return str(data_formating).format(text)
        return str(text)
    
    @staticmethod
    def fmt_content(text, width = 0, align = '<', padding = None, padding_left = None, padding_right = None, padding_char = ' '):
        """
        Pad given text with given padding characters, inflate it to given width
        and perform horizontal aligning.
        """
        if padding_left is None:
            padding_left = padding
        if padding_right is None:
            padding_right = padding
        if padding_left is not None:
            text = '{}{}'.format(str(padding_char)[0] * int(padding_left), text)
        if padding_right is not None:
            text = '{}{}'.format(text, str(padding_char)[0] * int(padding_right))
        if width:
            strptrn = '{:' + ('{}{}{}'.format(str(padding_char)[0], str(TEXT_ALIGNMENT[align]), str(width))) + 's}'
            text = strptrn.format(text)
        return text
    
    @staticmethod
    def fmt_text(text, bg = None, fg = None, attr = None, plain = False):
        """
        Apply given console formating around given text.
        """
        if not plain:
            if fg is not None:
                text = TEXT_FORMATING['fg'][fg] + text
            if bg is not None:
                text = TEXT_FORMATING['bg'][bg] + text
            if attr is not None:
                text = TEXT_FORMATING['attr'][attr] + text
            if (fg is not None) or (bg is not None) or (attr is not None):
                text += TEXT_FORMATING['rst']
        return text
    
    @staticmethod
    def fmt_margin(text, margin = None, margin_left = None, margin_right = None, margin_char = ' '):
        """
        Surround given text with given margin characters.
        """
        if margin_left is None:
            margin_left = margin
        if margin_right is None:
            margin_right = margin
        if margin_left is not None:
            text = '{}{}'.format(str(margin_char)[0] * int(margin_left), text)
        if margin_right is not None:
            text = '{}{}'.format(text, str(margin_char)[0] * int(margin_right))
        return text
    
    #---------------------------------------------------------------------------
    
    def _render(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        raise Exception("This method must be oveloaded and implemented in subclass")
    
    def render(self, content = None, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        (content, settings) = self.get_setup(content, **settings)
        return self._render(content, **settings)

#-------------------------------------------------------------------------------

class SingleLineWidget(ConsoleWidget):
    """
    Base class for single line only widgets.
    """
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        raise Exception("This method must be oveloaded and implemented in subclass")
    
    def _render(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        result = self._render_content(content, **settings)

        s = self._es_margin(settings)
        result = self.fmt_margin(result, **s)

        return result
    
    def display(self, content = None, **settings):
        """
        Perform widget rendering and output the result.
        """
        print(self.render(content, **settings))

#-------------------------------------------------------------------------------

class MultiLineWidget(ConsoleWidget):
    """
    Base class for widgets spanning over multiple lines.
    """
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        raise Exception("This method must be oveloaded and implemented in subclass")
    
    def _render(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        lines = self._render_content(content, **settings)

        result = []
        s = self._es_margin(settings)
        for l in lines:
            result.append(self.fmt_margin(l, **s))

        return result
    
    def display(self, content = None, **settings):
        """
        Perform widget rendering and output the result.
        """
        lines = self.render(content, **settings)
        for l in lines:
            print(l)

class BorderedMultiLineWidget(MultiLineWidget):
    """
    Base class for bordered widgets spanning over multiple lines.
    """
    
    SETTING_FLAG_BORDER      = 'border'
    SETTING_BORDER_FORMATING = 'border_formating'
    SETTING_BORDER_STYLE     = 'border_style'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_FLAG_BORDER, True))
        result.append((self.SETTING_BORDER_FORMATING, {}))
        result.append((self.SETTING_BORDER_STYLE, 'utf8.a'))
        return result
    
    @staticmethod
    def bchar(posh, posv, border_style):
        """
        Retrieve table border style for particular box border piece.
        """
        index = '{}{}'.format(posv, posh).lower()
        return BORDER_STYLES[border_style][index]
    
    #---------------------------------------------------------------------------
    
    @staticmethod
    def calculate_width_widget_int(width, border = False, margin = None, margin_left = None, margin_right = None):
        """
        Calculate actual widget content width based on given margins and paddings.
        """
        if margin_left is None:
            margin_left = margin
        if margin_right is None:
            margin_right = margin
        if margin_left is not None:
            width -= int(margin_left)
        if margin_right is not None:
            width -= int(margin_right)
        if border:
            width -= 2
        return width if width > 0 else None
    
    @staticmethod
    def calculate_width_content(width, border = False, margin = None, margin_left = None, margin_right = None, padding = None, padding_left = None, padding_right = None):
        """
        Calculate actual widget content width based on given margins and paddings.
        """
        if margin_left is None:
            margin_left = margin
        if margin_right is None:
            margin_right = margin
        if margin_left is not None:
            width -= int(margin_left)
        if margin_right is not None:
            width -= int(margin_right)
        if padding_left is None:
            padding_left = padding
        if padding_right is None:
            padding_right = padding
        if padding_left is not None:
            width -= int(padding_left)
        if padding_right is not None:
            width -= int(padding_right)
        if border:
            width -= 2
        return width if width > 0 else None

#-------------------------------------------------------------------------------

class TextWidget(SingleLineWidget):
    """
    Implementation of formatable text widget.
    """
    
    SETTING_TEXT_HIGHLIGHT = 'text_highlight'
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_TEXT_HIGHLIGHT, None))
        return result
    
    #---------------------------------------------------------------------------

    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        ocontent = content
        
        s = self._es_data(settings)
        content = self.fmt_data(content, **s)
        
        s = self._es_content(settings)
        content = self.fmt_content(content, **s)
        
        if settings[self.SETTING_TEXT_HIGHLIGHT]:
            s = self._es_text(settings, settings[self.SETTING_TEXT_HIGHLIGHT](ocontent))
        else:
            s = self._es_text(settings, settings[self.SETTING_TEXT_FORMATING])
        content = self.fmt_text(content, **s)
        
        s = self._es_margin(settings)
        content = self.fmt_margin(content, **s)

        return content

#-------------------------------------------------------------------------------

class StatusLineWidget(TextWidget):
    """
    Implementation of line widget.
    """
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        settings[self.SETTING_WIDTH] = TERMINAL_WIDTH
        return super()._render_content(content, **settings)

#-------------------------------------------------------------------------------

class ListWidget(MultiLineWidget):
    """
    Implementation of list widget.
    """
    
    INDENT = '    '
    
    SETTING_LIST_FORMATING = 'list_formating'
    SETTING_LIST_STYLE     = 'list_style'
    SETTING_LIST_TYPE      = 'list_type'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_LIST_FORMATING, {}))
        result.append((self.SETTING_LIST_STYLE, 'utf8.a'))
        result.append((self.SETTING_LIST_TYPE, 'unordered'))
        return result
    
    @staticmethod
    def lchar(list_style):
        """
        Retrieve list bullet character for particular list style.
        """
        return LIST_STYLES[list_style]
    
    #---------------------------------------------------------------------------
    
    def _render_item(self, depth, key, value = None, **settings):
        """
        Format single list item.
        """
        strptrn  = self.INDENT * depth
        
        lchar = self.lchar(settings[self.SETTING_LIST_STYLE])
        s = self._es_text(settings, settings[self.SETTING_LIST_FORMATING])
        lchar = self.fmt_text(lchar, **s)

        strptrn = "{}"
        if value is not None:
            strptrn += ": {}"
        s = self._es_text(settings, settings[self.SETTING_TEXT_FORMATING])
        strptrn = self.fmt_text(strptrn.format(key, value), **s)
        
        return '{} {} {}'.format(self.INDENT * depth, lchar, strptrn)
    
    def _render_content_list(self, content, depth, **settings):
        """
        Render the list.
        """
        result = []
        i = 0
        size = len(content)
        for value in content:
            if isinstance(value, dict):
                result.append(self._render_item(depth, "[{}]".format(i), **settings))
                result += self._render_content_dict(value, depth + 1, **settings)
            elif isinstance(value, list):
                result.append(self._render_item(depth, "[{}]".format(i), **settings))
                result += self._render_content_list(value, depth + 1, **settings)
            else:
                result.append(self._render_item(depth, value, **settings))
            i += 1
        return result
        
    def _render_content_dict(self, content, depth, **settings):
        """
        Render the dict.
        """
        result = []
        i = 0
        size = len(content)
        for key in sorted(content):
            if isinstance(content[key], dict):
                result.append(self._render_item(depth, key, **settings))
                result += self._render_content_dict(content[key], depth + 1, **settings)
            elif isinstance(content[key], list):
                result.append(self._render_item(depth, key, **settings))
                result += self._render_content_list(content[key], depth + 1, **settings)
            else:
                result.append(self._render_item(depth, key, content[key], **settings))
            i += 1
        return result

    #---------------------------------------------------------------------------

    def _render_content(self, content, **settings):
        """
        Render the tree widget.
        """
        if isinstance(content, dict):
            return self._render_content_dict(content, 0, **settings)
        elif isinstance(content, list):
            return self._render_content_list(content, 0, **settings)
        else:
            raise Exception("Received invalid data tree for rendering.")

#-------------------------------------------------------------------------------

class TreeWidget(MultiLineWidget):
    """
    Base class for all console widgets.
    """
    
    SETTING_TREE_FORMATING = 'tree_formating'
    SETTING_TREE_STYLE     = 'tree_style'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_TREE_FORMATING, {}))
        result.append((self.SETTING_TREE_STYLE, 'utf8.a'))
        return result
    
    @staticmethod
    def tchar(tree_style, cur_level, level, item, size):
        """
        Retrieve tree character for particular tree node.
        """
        if (cur_level == level):
            i1 = '1' if level == 0 else 'x'
            i2 = '1' if item  == 0 else 'x'
            i3 = 'x'
            if size == 1:
                i3 = '1'
            elif item == (size - 1):
                i3 = 'l'
            index = '{}{}{}'.format(i1, i2, i3)
        else:
            index = 'non' if item == (size - 1) else 'ver'
        return TREE_STYLES[tree_style][index]

    #---------------------------------------------------------------------------

    def _render_item(self, dstack, key, value = None, **settings):
        """
        Format single tree line.
        """
        cur_depth = len(dstack) - 1
        
        treeptrn = ''
        s = self._es_text(settings, settings[self.SETTING_TREE_FORMATING])
        for ds in dstack:
            treeptrn += ' ' + self.fmt_text(self.tchar(settings[self.SETTING_TREE_STYLE], cur_depth, *ds), **s) + ''

        strptrn = "{}"
        if value is not None:
            strptrn += ": {}"
        s = self._es_text(settings, settings[self.SETTING_TEXT_FORMATING])
        strptrn = self.fmt_text(strptrn.format(key, value), **s)
        
        return '{} {}'.format(treeptrn, strptrn)

    def _render_content_list(self, content, depth, dstack, **settings):
        """
        Render the list.
        """
        result = []
        i = 0
        size = len(content)
        for value in content:
            ds = [(depth, i, size)]
            ds = dstack + ds
            if isinstance(value, dict):
                result.append(self._render_item(ds, "[{}]".format(i), **settings))
                result += self._render_content_dict(value, depth + 1, ds, **settings)
            elif isinstance(value, list):
                result.append(self._render_item(ds, "[{}]".format(i), **settings))
                result += self._render_content_list(value, depth + 1, ds, **settings)
            else:
                result.append(self._render_item(ds, value, **settings))
            i += 1
        return result

    def _render_content_dict(self, content, depth, dstack, **settings):
        """
        Render the dict.
        """
        result = []
        i = 0
        size = len(content)
        for key in sorted(content):
            ds = [(depth, i, size)]
            ds = dstack + ds
            if isinstance(content[key], dict):
                result.append(self._render_item(ds, key, **settings))
                result += self._render_content_dict(content[key], depth + 1, ds, **settings)
            elif isinstance(content[key], list):
                result.append(self._render_item(ds, key, **settings))
                result += self._render_content_list(content[key], depth + 1, ds, **settings)
            else:
                result.append(self._render_item(ds, key, content[key], **settings))
            i += 1
        return result

    #---------------------------------------------------------------------------

    def _render_content(self, content, **settings):
        """
        Render the tree widget.
        """
        if isinstance(content, dict):
            return self._render_content_dict(content, 0, [], **settings)
        elif isinstance(content, list):
            return self._render_content_list(content, 0, [], **settings)
        else:
            raise Exception("Received invalid data tree for rendering.")

#-------------------------------------------------------------------------------

class BoxWidget(BorderedMultiLineWidget):
    """
    Implementation of box widget.
    """
    
    SETTING_FLAG_HEADER      = 'header'
    SETTING_HEADER_CONTENT   = 'header_content'
    SETTING_HEADER_FORMATING = 'header_formating'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_FLAG_HEADER, True))
        result.append((self.SETTING_HEADER_CONTENT, 'Notice'))
        result.append((self.SETTING_HEADER_FORMATING, {}))
        return result
    
    def fmt_border(self, width, t = 'm', border_style = 'utf8.a', border_formating = {}):
        """
        Format box separator line.
        """
        border = self.bchar('l', t, border_style) + (self.bchar('h', t, border_style) * (width-2)) + self.bchar('r', t, border_style)
        return self.fmt_text(border, **border_formating)
    
    #---------------------------------------------------------------------------
    
    @staticmethod
    def _wrap_content(content, width):
        """
        Wrap given content into lines of given width.
        """
        data = []
        if isinstance(content, list):
            data += content
        else:
            data.append(content)

        lines = []
        for d in data:
            l = textwrap.wrap(d, width)
            lines += l
        return lines
    
    #---------------------------------------------------------------------------
    
    def _render_border_line(self, t, settings):
        """
        Render box border line.
        """
        s = self._es(settings, self.SETTING_WIDTH, self.SETTING_MARGIN, self.SETTING_MARGIN_LEFT, self.SETTING_MARGIN_RIGHT)
        w = self.calculate_width_widget(**s)
        s = self._es(settings, self.SETTING_BORDER_STYLE, self.SETTING_BORDER_FORMATING)
        border_line = self.fmt_border(w, t, **s)
        s = self._es(settings, self.SETTING_MARGIN, self.SETTING_MARGIN_LEFT, self.SETTING_MARGIN_RIGHT, self.SETTING_MARGIN_CHAR)
        border_line = self.fmt_margin(border_line, **s)
        return border_line
    
    def _render_line(self, line, settings):
        """
        Render single box line.
        """
        s = self._es(settings, self.SETTING_WIDTH, self.SETTING_FLAG_BORDER, self.SETTING_MARGIN, self.SETTING_MARGIN_LEFT, self.SETTING_MARGIN_RIGHT)
        width_content = self.calculate_width_widget_int(**s)
        
        s = self._es_content(settings)
        s[self.SETTING_WIDTH] = width_content
        line = self.fmt_content(line, **s)
        
        s = self._es_text(settings, settings[self.SETTING_TEXT_FORMATING])
        line = self.fmt_text(line, **s)
        
        s = self._es(settings, self.SETTING_BORDER_STYLE)
        bchar = self.bchar('v', 'm', **s)
        
        s = self._es_text(settings, settings[self.SETTING_BORDER_FORMATING])
        bchar = self.fmt_text(bchar, **s)
        
        line = '{}{}{}'.format(bchar, line, bchar)
        s = self._es_margin(settings)
        line = self.fmt_margin(line, **s)
        return line

    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        if not self.SETTING_WIDTH in settings or not settings[self.SETTING_WIDTH]:
            settings[self.SETTING_WIDTH] = TERMINAL_WIDTH
        
        s = {k: settings[k] for k in (self.SETTING_WIDTH, self.SETTING_FLAG_BORDER, self.SETTING_MARGIN, self.SETTING_MARGIN_LEFT, self.SETTING_MARGIN_RIGHT, self.SETTING_PADDING, self.SETTING_PADDING_LEFT, self.SETTING_PADDING_RIGHT)}
        width_int = self.calculate_width_content(**s)
        
        lines = self._wrap_content(content, width_int)
        
        result = []
        if settings[self.SETTING_FLAG_BORDER]:
            result.append(self._render_border_line('t', settings))
        if settings[self.SETTING_FLAG_HEADER]:
            s = {k: settings[k] for k in settings.keys()}
            s[self.SETTING_TEXT_FORMATING] = s[self.SETTING_HEADER_FORMATING]
            result.append(self._render_line(settings[self.SETTING_HEADER_CONTENT], s))
            result.append(self._render_border_line('m', settings))
        for l in lines:
            result.append(self._render_line(l, settings))
        if settings[self.SETTING_FLAG_BORDER]:
            result.append(self._render_border_line('b', settings))
        return result

#-------------------------------------------------------------------------------

class TableWidget(BorderedMultiLineWidget):
    """
    Table result formater.
    """
    
    SETTING_FLAG_HEADER      = 'header'
    SETTING_HEADER_CONTENT   = 'header_content'
    SETTING_HEADER_FORMATING = 'header_formating'
    SETTING_FLAG_ENUMERATE   = 'enumerate'
    SETTING_COLUMNS          = 'columns'
    SETTING_ROW_HIGHLIGHT    = 'row_highlight'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_FLAG_HEADER, True))
        result.append((self.SETTING_HEADER_CONTENT, 'Notice'))
        result.append((self.SETTING_HEADER_FORMATING, {'attr': 'bold'}))
        result.append((self.SETTING_FLAG_ENUMERATE, False))
        result.append((self.SETTING_COLUMNS, None))
        result.append((self.SETTING_ROW_HIGHLIGHT, None))
        return result
    
    def fmt_border(self, dimensions, t = 'm', border_style = 'utf8.a', border_formating = {}):
        """
        Format table separator line.
        """
        cells = []
        for column in dimensions:
            cells.append(self.bchar('h', t, border_style) * (dimensions[column] + 2))

        border = '{}{}{}'.format(self.bchar('l', t, border_style), self.bchar('m', t, border_style).join(cells), self.bchar('r', t, border_style))
        return self.fmt_text(border, **border_formating)
    
    def fmt_cell(self, value, width, cell_formating, **text_formating):
        """
        Format sigle table cell.
        """
        strptrn = " {:" + '{:s}{:d}'.format(cell_formating.get('align', '<'), width) + "s} "
        strptrn = self.fmt_text(strptrn, **text_formating)
        return strptrn.format(value)
    
    def fmt_row(self, columns, dimensions, row, **settings):
        """
        Format single table row.
        """
        cells = []
        i = 0
        for column in columns:
            cells.append(self.fmt_cell(
                    row[i],
                    dimensions[i],
                    column,
                    **settings[self.SETTING_TEXT_FORMATING]
                )
            )
            i += 1
        return self.bchar('v', 'm', settings[self.SETTING_BORDER_STYLE], **settings[self.SETTING_BORDER_FORMATING]) + \
               self.bchar('v', 'm', settings[self.SETTING_BORDER_STYLE], **settings[self.SETTING_BORDER_FORMATING]).join(cells) + \
               self.bchar('v', 'm', settings[self.SETTING_BORDER_STYLE], **settings[self.SETTING_BORDER_FORMATING])
    
    def fmt_row_header(self, columns, dimensions, **settings):
        """
        Format table header row.
        """
        row = list(map(lambda x: x['label'], columns))
        return self.fmt_row(columns, dimensions, row, **settings)
    
    #---------------------------------------------------------------------------
    
    def table_format(self, columns, content):
        """
        Enumerate each table column.
        """
        result = []
        textw = TextWidget()
        for row in content:
            i = 0
            result_row = []
            for cell in row:
                result_row.append(textw.render(cell, **columns[i]))
                i += 1
            result.append(result_row)
        return (columns, result)
    
    def table_enumerate(self, columns, content):
        """
        Enumerate each table column.
        """
        columns.insert(0, { 'label': '#', 'enumerated': True })
        i = 0
        for row in content:
            i += 1
            row.insert(0, '{:d}'.format(i))
        return (columns, content)
    
    def table_measure(self, columns, content):
        """
        Measure the width of each table column.
        """
        dimensions = {}
        for row in content:
            i = 0
            for cell in row:
                # Calculate maximum from:
                dimensions[i] = max(
                        dimensions.get(i, 0),              # current column max width
                        len(cell),                         # current cell value width
                        len(columns[i].get('label', '')),  # column label width
                        columns[i].get('width_min', 0),    # configured column minimal width
                    )
                i += 1
        return dimensions
    
    #---------------------------------------------------------------------------
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        result = []
        columns = settings[self.SETTING_COLUMNS]
        
        # Format each table cell into string.
        (columns, content) = self.table_format(columns, content)
        
        # Enumerate each table row.
        if settings[self.SETTING_FLAG_ENUMERATE]:
            (columns, content) = self.table_enumerate(columns, content)
        
        # Calculate the dimensions of each table column.
        dimensions = self.table_measure(columns, content)
        
        # Display table header.
        sb = {k: settings[k] for k in (self.SETTING_BORDER_STYLE, self.SETTING_BORDER_FORMATING)}
        result.append(self.fmt_border(dimensions, 't', **sb))
        if settings[self.SETTING_FLAG_HEADER]:
            s = {k: settings[k] for k in (self.SETTING_FLAG_PLAIN, self.SETTING_BORDER_STYLE, self.SETTING_BORDER_FORMATING)}
            s[self.SETTING_TEXT_FORMATING] = settings[self.SETTING_HEADER_FORMATING]
            result.append(self.fmt_row_header(columns, dimensions, **s))
            result.append(self.fmt_border(dimensions, 'm', **sb))
        
        # Display table body.
        for row in content:
            s = {k: settings[k] for k in (self.SETTING_FLAG_PLAIN, self.SETTING_BORDER_STYLE, self.SETTING_BORDER_FORMATING)}
            s[self.SETTING_TEXT_FORMATING] = settings[self.SETTING_TEXT_FORMATING]
            result.append(self.fmt_row(columns, dimensions, row, **s))
        
        # Display table footer
        result.append(self.fmt_border(dimensions, 'b', **sb))
        return result

#-------------------------------------------------------------------------------

class ProgressBarWidget(SingleLineWidget):
    """
    Implementation of formatable progress bar widget.
    """

    SETTING_BAR_FORMATING = 'bar_formating'
    SETTING_BAR_CHAR      = 'bar_char'
    SETTING_BAR_WIDTH     = 'bar_width'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_BAR_FORMATING, {}))
        result.append((self.SETTING_BAR_CHAR, '='))
        result.append((self.SETTING_BAR_WIDTH, 0))
        return result
    
    #---------------------------------------------------------------------------
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        bar_len = int(settings[self.SETTING_BAR_WIDTH])
        if not bar_len:
            bar_len = TERMINAL_WIDTH - 10
        percent = content
        progress = ""
        progress += str(settings[self.SETTING_BAR_CHAR]) * int(bar_len * percent)
        s = {k: settings[k] for k in (self.SETTING_FLAG_PLAIN,)}
        s.update(settings[self.SETTING_BAR_FORMATING])
        progress = self.fmt_text(progress, **s)
        progress += ' ' * int(bar_len - int(bar_len * percent))
        return "{:6.2f}% [{:s}]".format(percent * 100, progress)
    
    def display(self, content = None, **settings):
        """
        Perform widget rendering and output the result.
        """
        sys.stdout.write("\r")
        sys.stdout.write(self.render(content, **settings))
        sys.stdout.flush()

#-------------------------------------------------------------------------------

class BarChartWidget(MultiLineWidget):
    """
    Implementation of formatable bar chart widget.
    """

    SETTING_BAR_FORMATING = 'bar_formating'
    SETTING_BAR_CHAR      = 'bar_char'
    SETTING_BAR_WIDTH     = 'bar_width'
    SETTING_BARS          = 'bars'
    
    #---------------------------------------------------------------------------
    
    def list_settings(self):
        """
        Get list of all appropriate settings and their default values.
        """
        result = super().list_settings()
        result.append((self.SETTING_BAR_FORMATING, {}))
        result.append((self.SETTING_BAR_CHAR, '='))
        result.append((self.SETTING_BAR_WIDTH, 0))
        result.append((self.SETTING_BARS, None))
        return result
    
    def chart_measure(self, bars):
        """
        Measure the width of each table column.
        """
        width = 0
        for bar in bars:
            # Calculate maximum from:
            width = max(
                width,                      # current label max width
                len(bar.get('label', '')),  # column label width
                bar.get('width_min', 0),    # configured column minimal width
            )
        return width
    
    #---------------------------------------------------------------------------
    
    def _render_bar(self, bar, value, max_value, label_width, bar_width, **settings):
        """
        Render single chart bar.
        """
        percent = value / max_value
        barstr = ""
        barstr += str(settings[self.SETTING_BAR_CHAR]) * int(bar_width * percent)
        s = {k: settings[k] for k in (self.SETTING_FLAG_PLAIN,)}
        s.update(settings[self.SETTING_BAR_FORMATING])
        barstr = self.fmt_text(barstr, **s)
        barstr += ' ' * int(bar_width - int(bar_width * percent))
        strptrn = "{:"+str(label_width)+"s} [{:s}]"
        return strptrn.format(bar.get('label'), barstr)
    
    def _render_content(self, content, **settings):
        """
        Perform widget rendering, but do not print anything.
        """
        result = []
        bars = settings[self.SETTING_BARS]
        
        label_width = self.chart_measure(bars)
        if not settings[self.SETTING_BAR_WIDTH]:
            settings[self.SETTING_BAR_WIDTH] = TERMINAL_WIDTH - label_width - 3
        max_value = max(content)
        i = 0
        for bar in content:
            result.append(self._render_bar(bars[i], bar, max_value, label_width, **settings))
            i += 1
        return result

if __name__ == "__main__":
    """
    Perform the demonstration.
    """
    argparser = argparse.ArgumentParser(description = "pydgets - Console widget library for Python 3")
    argparser.add_argument('--group', help = 'pick a group of widgets', choices = ['all', 'data', 'text', 'line', 'box', 'list', 'tree', 'table', 'progress', 'barchart'], default='all')
    args = argparser.parse_args()

    (columns, rows) = terminal_size()
    print("Detected terminal size {} x {} (WxH)".format(columns, rows))

    if args.group in ('all', 'data'):
        print("")
        labelptrn = " {:<60s} "
        textw = TextWidget()
        print("Demonstrations of TextWidget data formating capabilities...")
        print("")
        for conv in (
            [523689,        'int'],
            [123523.689111, 'float'],
            [52.689111,     'percent'],
            [52368922,      'sizekb'],
            [52368922,      'sizemb'],
            [52368922,      'sizegb'],
            [523689,        'duration'],
        ):
            label = " Data conversion '{}' to '{}'".format(conv[0], conv[1])
            label = labelptrn.format(label)
            print(label, textw.render(conv[0], data_type = conv[1]))
        
        print("Demonstrations of TextWidget data highlighting capabilities...")
        print("")

        def deco(val):
            if int(val) > 100:
                return {'fg': 'red'}
            else:
                return {'fg': 'green'}

        for val in ('50', '150'):
            label = " Data decoration '{}'".format(val)
            print(label, textw.render(val, text_highlight = deco))

    if args.group in ('all', 'text'):
        print("")
        labelptrn = " {:<60s} "
        textw = TextWidget()
        print("Demonstrations of TextWidget...")
        print("")
        for attr in sorted(TEXT_FORMATING["attr"]):
            label = " Text attribute '{}'".format(attr)
            label = labelptrn.format(label)
            print(label, textw.render(label, text_formating = {"attr": attr}))
        print("")
        print("Test of text colors only...")
        print("")
        for fg in sorted(TEXT_FORMATING["fg"]):
            label = " Text color '{}'".format(fg)
            label = labelptrn.format(label)
            print(label, textw.render(label, text_formating = {"fg": fg}))
        print("")
        print("Test of background colors only...")
        print("")
        for bg in sorted(TEXT_FORMATING["bg"]):
            label = " Background color '{}' ".format(bg)
            label = labelptrn.format(label)
            print(label, textw.render(label, text_formating = {"bg": bg}))
        print("")
        print("Test of color combinations (foreground - background)...")
        print("")
        for bg in sorted(TEXT_FORMATING["bg"]):
            for fg in sorted(TEXT_FORMATING["fg"]):
                label = " Combination fg '{}' bg '{}'".format(fg, bg)
                label = labelptrn.format(label)
                print(label, textw.render(label, text_formating = {"fg": fg, "bg": bg}))
        print("")
        print("Test of all combinations (foreground - background - attribute)...")
        print("")
        for bg in sorted(TEXT_FORMATING["bg"]):
            for fg in sorted(TEXT_FORMATING["fg"]):
                for attr in sorted(TEXT_FORMATING["attr"]):
                    label = " Combination fg '{}' bg '{}' attr '{}'".format(fg, bg, attr)
                    label = labelptrn.format(label)
                    print(labelptrn.format(label), textw.render(label, text_formating = {"fg": fg, "bg": bg, "attr": attr}))

    if args.group in ('all', 'line'):
        print("")
        print("Demonstrations of StatusLineWidget...")
        print("")
        linew = StatusLineWidget()
        print(linew.render('Test status line text, left align, left padding', padding_left = 5, text_formating = {"bg": "on_yellow"}))
        print(linew.render('Test status line text, centered', align = '^', text_formating = {"bg": "on_red"}))
        print(linew.render('Test status line text, right align, right padding with custom character', padding_right = 5, padding_char = '#', align = '>', text_formating = {"bg": "on_blue"}))
        print(linew.render('Test status line text, margin', margin = 5, text_formating = {"bg": "on_yellow"}))

    if args.group in ('all', 'list'):
        print("")
        print("Demonstrations of ListWidget...")
        print("")
        data = {
            'x': 1,
            'y': 2,
            'z': 3,
            'dict': {
                'a': 4,
                'b': 5,
                'c': 6,
            },
            'dict_o_dict': {
                'u': { 'm': 11, 'n': 12 },
                'v': { 'o': 21, 'p': 22 },
                'w': { 'q': 31, 'r': 32 },
            },
            'list': [
                'aaa',
                'bbb',
                'ccc',
            ],
            'list_o_list': [
                ['qq', 'rr', 'ss'],
                ['aa', 'bb', 'cc'],
                ['mm', 'nn', 'oo'],
            ],
        }
        listw = ListWidget()
        listw.display(data)

    if args.group in ('all', 'tree'):
        print("")
        print("Demonstrations of TreeWidget...")
        for s in sorted(TREE_STYLES):
            print("")
            print("Style {}".format(s))
            data = {
                'x': 1,
                'y': 2,
                'z': 3,
                'dict': {
                    'a': 4,
                    'b': 5,
                    'c': 6,
                },
                'dict_o_dict': {
                    'u': { 'm': 11, 'n': 12 },
                    'v': { 'o': 21, 'p': 22 },
                    'w': { 'q': 31, 'r': 32 },
                },
                'list': [
                    'aaa',
                    'bbb',
                    'ccc',
                ],
                'list_o_list': [
                    ['qq', 'rr', 'ss'],
                    ['aa', 'bb', 'cc'],
                    ['mm', 'nn', 'oo'],
                ],
            }
            treew = TreeWidget()
            treew.display(data, tree_style = s)
        
    if args.group in ('all', 'box'):
        print("")
        print("Demonstrations of BoxWidget...")
        boxw = BoxWidget()
        text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumyeirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diamvoluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumyeirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diamvoluptua. At vero eos et accusam et justo duo dolores et ea reb."
        for s in sorted(BORDER_STYLES):
            h = "Style {}".format(s)
            print("")
            boxw.display(text, header_content = h, width = 150, padding = 1, border_style = s, header_formating = {"bg": "on_red"})

    if args.group in ('all', 'table'):
        print("")
        print("Demonstrations of TableWidget...")
        print("")
        tablew = TableWidget()
        tcols = [
                { 'label': 'X' },
                { 'label': 'Y', 'data_formating': '{:,d}', 'align': '>' },
                { 'label': 'Z', 'data_formating': '{:.2f}', 'align': '>' },
            ]
        tbody = [
                ['abc', 55, 12.134],
                ['abc', 666, 14.156],
                ['abc', 7777, 16.178],
                ['abc', 88888, 18.199],
            ]
        tablew.display(tbody, columns = tcols)

    if args.group in ('all', 'progress'):
        print("")
        print("Demonstrations of ProgressBarWidget...")
        print("")
        progw = ProgressBarWidget(bar_formating = {"bg": "on_blue"}, bar_char = ' ')
        for i in range(0, 100, 10):
            progw.display(i/100)
            time.sleep(1)

    if args.group in ('all', 'barchart'):
        print("")
        print("Demonstrations of BarChartWidget...")
        print("")
        barch = BarChartWidget()
        chbars = [
                { 'label': 'X' },
                { 'label': 'Y' },
                { 'label': 'Z' },
                { 'label': 'A' },
                { 'label': 'B' },
                { 'label': 'C' },
                { 'label': 'D' },
            ]
        chbody = [
                55,
                88,
                150,
                250,
                22,
                324,
                12,
            ]
        barch.display(chbody, bars = chbars)
