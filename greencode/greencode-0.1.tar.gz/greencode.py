#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Green Code is a simple LED based textual representation that aims
to be useful in LED grid based applications.

For more infomation see: http://ledui.github.io/

One possible use:

message = "Hello World"
from sense_hat import SenseHat
sense_hat = SenseHat()
gcode = GreenCode()
grids = gcode.parse_message(message)
for grid in grids:
    self.hat.set_pixels(grid)
    # Do something more clever with it
    input()

"""

from itertools import permutations
from string import ascii_lowercase, digits

__version__ = "0.1"

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (102, 0, 204)
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
OFF = (0, 0, 0)

BLANK = '    '

COLOURS = (
    (' ', OFF),      # Off
    ('.', BLUE),    # Dark
    ('-', RED),     # Light
    ('#', GREEN),   # Numbers
    ('&', YELLOW),  # Punctuation
    ('^', PURPLE),  # Symbols
    (';', ORANGE),  # European letters
    ('=', CYAN)     # European letters
)

LETTERS = (
    '.-  ',  # a
    '-...',  # b
    '-.-.',  # c
    '-.. ',  # d
    '.   ',  # e
    '..-.',  # f
    '--. ',  # g
    '....',  # h
    '..  ',  # i
    '.---',  # j
    '-.- ',  # k
    '.-..',  # l
    '--  ',  # m
    '-.  ',  # n
    '--- ',  # o
    '.--.',  # p
    '--.-',  # q
    '.-. ',  # r
    '... ',  # s
    '-   ',  # t
    '..- ',  # u
    '...-',  # v
    '.-- ',  # w
    '-..-',  # x
    '-.--',  # y
    '--..'   # z
)

NUMBERS = (
    '#   ',  # 0
    '#.  ',  # 1
    '#.. ',  # 2
    '#...',  # 3
    '#.- ',  # 4 i.e. IV
    '#-  ',  # 5 i.e. V
    '#-. ',  # 6 i.e. VI
    '#-..',  # 7 i.e. VII
    '#..-',  # 8 - Imagine it is  #..-- i.e. IIVV
    '#.--',  # 9 i.e. IVV
)

SYMBOLS = (
    ('\n', '.-.-'),  # New line/full stop
    (' ', '    '),  # Space
    (',', '----'),  # Comma
    ('?', '..--'),  # Question Mark
    ('!', '---.'),  # Exclamation Mark
    ('+', '#--.'),  # Plus/Add
    ('-', '#-- '),  # Hypen/minus
    ('=', '#---'),  # Equals
    ('/', '#.-.'),  # Slash or divide i.e dot line dot: ÷
    ('*', '#-.-'),  # Asterisk/multiply
    ('.', '&   '),  # Full stop/period
    ('%', '&.-.'),  # Percent
    ("'", '&-  '),  # Single Quote/Apostrophe
    ('"', '&-- '),  # Double Quote
    (':', '&.. '),  # Colon
    (';', '&.- '),  # Semi Colon
    ('@', '&.--'),  # At Sign
    ('(', '&---'),  # Open Parenthesis
    (')', '&--.'),  # Close Parenthesis
    ('_', '&-. '),  # Underscore
    ('$', '&-.-'),  # Dollar sign
    ('>', '&-..'),  # Greater than
    ('#', '&.  '),  # Number sign/Hash
    ('<', '&..-'),  # Less than
    ('&', '&...'),  # Ampersand
    ('\\', '^.-.'),  # Back Slash
    ('^', '^   '),  # Caret
    ('`', '^-  '),  # Grave accent/backtick
    ('|', '^-- '),  # Vertical bar
    ('~', '^-. '),  # Tilde
    ('{', '^-.-'),  # Open brace/curly bracket
    ('}', '^-..'),  # Close brace/curly bracket
    ('[', '^.  '),  # Open Square brackets
    (']', '^.. '),  # Close Square brackets
    ('£', '^--.'),  # Pound Sign
    ('€', '^.--'),  # Euro sign
)

DIACRITICS = (
    ('ß', '^...'),  # sharp s
    ('ä', '^.- '),  # a with diaeresis
    ('ö', '^---'),  # o with diaeresis
    ('ü', '^..-'),  # u with diaeresis
    ('ï', ';-- '),  # i with diaeresis
    ('ë', ';-. '),  # e with diaeresis
    ('ÿ', ';---'),  # y with diaeresis
    ('é', ';.  '),  # e with acute accent
    ('à', ';.- '),  # a with grave accent
    ('è', ';.. '),  # e with grave accent
    ('ù', ';..-'),  # u with grave accent
    ('â', ';.--'),  # a with circumflex
    ('ê', ';...'),  # e with circumflex
    ('î', ';-..'),  # i with circumflex
    ('ô', ';--.'),  # o with circumflex
    ('û', ';-  '),  # u with circumflex
    ('ç', ';-.-'),  # c with cedilla
    ('í', ';.-.'),  # i with acute accent
    ('ú', ';   '),  # u with acute accent
    ('ó', '=...'),  # o with acute accent
    ('á', '=.- '),  # a with acute accent
    ('å', '=-.-'),  # a with ring
    ('ñ', '=-. '),  # n with virgulilla
    ('ã', '=.. '),  # a with virgulilla
    ('õ', '=---'),  # o with virgulilla
    ('¿', '=..-'),  # Inverted question mark
    ('¡', '=--.'),  # Inverted exclamation point
    ('ø', '=-- '),  # o with stroke
    ('ý', '=-..'),  # y with acute accent
    ('ò', '=.  '),  # o with grave accent
    ('ì', '=.-.'),  # i with grave accesnt
    ('æ', '=-  '),  # ash (ae ligature)
    ('ð', '=.--'),  # eth
    ('þ', '=   '),  # thorn
)


def chunk_string(string, length):
    """Chunk string into length long chunks."""
    return [string[0+i:length+i] for i in range(0, len(string), length)]


class GreenCode(object):
    """Green code text representation."""
    def __init__(self):
        self.characters = dict(zip(ascii_lowercase, LETTERS))
        self.characters.update(zip(digits, NUMBERS))
        self.characters.update(SYMBOLS)
        self.characters.update(DIACRITICS)
        self.colours = dict(COLOURS)
        self.height = 8
        self.width = 8
        self.blankpart = [OFF for _ in range(0, 32)]

    def parse_message(self, message):
        """Parse a message into grid matrixes."""
        screens = self._split_message(message.lower())
        grids = [self._convert_screen_to_matrix(screen) for screen in screens]
        return grids

    def _split_message(self, message):
        """Split a message into screen sized amounts."""
        screens = []
        last_screen_length = 0
        carry_over_space = False
        for word in message.split():
            if carry_over_space:
                word = ' ' + word
                carry_over_space = False
            if len(word) < 8:
                if last_screen_length == 1:
                    screens[-1].append(word)
                    last_screen_length = 2
                else:
                    screens.append([word, ])
                    last_screen_length = 1
            else:
                chunks = chunk_string(word, 8)
                if len(chunks[-1]) == 8:
                    carry_over_space = True
                if last_screen_length == 1:
                    screens[-1].append(chunks.pop(0))
                    if not chunks:
                        last_screen_length = 2
                        continue
                while len(chunks) > 2:
                    screens.append([chunks.pop(0),
                                    chunks.pop(0)])

                last_screen_length = len(chunks)
                screens.append(chunks)
        return screens

    def _convert_screen_to_matrix(self, screen):
        """Convert screen of text to matrix that at least the Raspberry Pi
        Sense HAT library and the ledgrid module understands.

        """
        grid = []
        for word in screen:
            part = []
            for letter in word:
                try:
                    part.append(self.characters[letter])
                except KeyError:
                    part.append(BLANK)
            while len(part) < 8:
                part.append(BLANK)
            for row in range(0, 4):
                for column in range(0, 8):
                    grid.append(self.colours[part[column][row]])
        if len(screen) == 1:
            grid.extend(self.blankpart)
        return grid

    def parse_character(self, character):
        """Parse a single character."""
        return [self.colours[symbol] for symbol in self.characters[character]]


def example():
    """A simple example."""
    gcode = GreenCode()
    gcode.parse_message("hello world")

if __name__ == "__main__":
    example()
