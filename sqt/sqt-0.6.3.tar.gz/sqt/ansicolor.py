"""
ANSI escape codes and some helper functions for colored terminal output.
"""

# dark foreground colors
BLACK = "\x1b[0;30m"
RED = "\x1b[0;31m"
GREEN = "\x1b[0;32m"
BROWN = "\x1b[0;33m"
BLUE = "\x1b[0;34m"
PURPLE = "\x1b[0;35m"
CYAN = "\x1b[0;36m"
GRAY = "\x1b[0;37m"

# light foreground colors
DARKGRAY = "\x1b[1;30m"
LIGHTRED = "\x1b[1;31m"
LIGHTGREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
LIGHTBLUE = "\x1b[1;34m"
LIGHTPURPLE = "\x1b[1;35m"
LIGHTCYAN = "\x1b[1;36m"
WHITE = "\x1b[1;37m"

# dark background colors
BACKGROUND_BLACK = "\x1b[0;40m"
BACKGROUND_BLUE = "\x1b[0;44m"
BACKGROUND_GREEN = "\x1b[0;42m"
BACKGROUND_CYAN = "\x1b[0;46m"
BACKGROUND_RED = "\x1b[0;41m"
BACKGROUND_PURPLE = "\x1b[0;45m"
BACKGROUND_BROWN = "\x1b[0;43m"
BACKGROUND_GRAY = "\x1b[0;47m"

# light background colors
BACKGROUND_DARKGRAY = "\x1b[1;40m"
BACKGROUND_LIGHTBLUE = "\x1b[1;44m"
BACKGROUND_LIGHTGREEN = "\x1b[1;42m"
BACKGROUND_LIGHTCYAN = "\x1b[1;46m"
BACKGROUND_LIGHTRED = "\x1b[1;41m"
BACKGROUND_LIGHTPURPLE = "\x1b[1;45m"
BACKGROUND_YELLOW = "\x1b[1;43m"
BACKGROUND_WHITE = "\x1b[1;47m"

# other codes
RESET = "\x1b[0m"

BOLD_ON = "\x1b[1m"
ITALICS_ON = "\x1b[3m"
UNDERLINE_ON = "\x1b[4m"
INVERSE_ON = "\x1b[7m"
STRIKETHROUGH_ON = "\x1b[9m"

BOLD_OFF = "\x1b[22m"
ITALICS_OFF = "\x1b[23m"
UNDERLINE_OFF = "\x1b[24m"
INVERSE_OFF = "\x1b[27m"
STRIKETHROUGH_OFF = "\x1b[29m"


def colored(s, color):
	"""
	Enclose string s in ANSI escape codes such that s appears in the given
	color when printed on a terminal.
	"""
	return color + s + RESET


def red(s):
	return colored(s, RED)


def blue(s):
	return colored(s, BLUE)


def green(s):
	return colored(s, GREEN)


def yellow(s):
	return colored(s, YELLOW)


def lightred(s):
    return colored(s, LIGHTRED)


def bgred(s):
	return colored(s, BACKGROUND_RED)


def bgblue(s):
	return colored(s, BACKGROUND_BLUE)


def bggreen(s):
	return colored(s, BACKGROUND_GREEN)

bgreen = bggreen

def bgyellow(s):
	return colored(s, BACKGROUND_YELLOW)
