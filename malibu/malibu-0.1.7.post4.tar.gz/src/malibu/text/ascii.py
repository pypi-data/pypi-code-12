# -*- coding: utf-8 -*-
# ASCII / ANSI Escape codes.

# Graphics mode / text styles.
STYLE_OFF = '\033[0m'
STYLE_BOLD = '\033[1m'
STYLE_UNDERSCORE = '\033[4m'
STYLE_BLINK = '\033[5m'
STYLE_REVERSE_VID = '\033[7m'
STYLE_CONCEALED = '\033[8m'

# Foreground text colors.
FG_BLACK = '\033[0;30m'
FG_RED = '\033[0;31m'
FG_GREEN = '\033[0;32m'
FG_BROWN = '\033[0;33m'
FG_BLUE = '\033[0;34m'
FG_MAGENTA = '\033[0;35m'
FG_CYAN = '\033[0;36m'
FG_LGRAY = '\033[0;37m'

FG_DGRAY = '\033[1;30m'
FG_LRED = '\033[1;31m'
FG_LGREEN = '\033[1;32m'
FG_YELLOW = '\033[1;33m'
FG_LBLUE = '\033[1;34m'
FG_LPURPLE = '\033[1;35m'
FG_LCYAN = '\033[1;36m'
FG_WHITE = '\033[1;37m'

# Background text colors.
BG_BLACK = '\033[0;40m'
BG_RED = '\033[0;41m'
BG_GREEN = '\033[0;42m'
BG_BROWN = '\033[0;43m'
BG_BLUE = '\033[0;44m'
BG_MAGENTA = '\033[0;45m'
BG_CYAN = '\033[0;46m'
BG_LGRAY = '\033[0;47m'

BG_DGRAY = '\033[1;40m'
BG_LRED = '\033[1;41m'
BG_LGREEN = '\033[1;42m'
BG_YELLOW = '\033[1;43m'
BG_LBLUE = '\033[1;44m'
BG_LPURPLE = '\033[1;45m'
BG_LCYAN = '\033[1;46m'
BG_WHITE = '\033[1;47m'


def style_text(style, obj):
    """ Simple method to stringify (or coerce an object to
        a string type, for those who prefer political correctness)
        with ASCII color or style codes and automatically terminate
        with STYLE_OFF escapes.
    """

    return style + str(obj) + STYLE_OFF
