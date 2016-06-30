# -*- coding: utf-8 -*-


class Color:
    FG_BLACK     = "\x1b[0m"
    FG_RED       = "\x1b[31m"
    FG_GREEN     = "\x1b[32m" 
    FG_YELLOW    = "\x1b[33m"
    FG_BLUE      = "\x1b[34m"
    FG_MAGENTA   = "\x1b[35m"
    FG_CYAN      = "\x1b[36m"
    FG_WHITE     = "\x1b[37m"
    FG_DEFAULT   = "\x1b[39m"
    
    BG_BLACK     = "\x1b[40m"
    BG_RED       = "\x1b[41m"
    BG_GREEN     = "\x1b[42m" 
    BG_YELLOW    = "\x1b[43m"
    BG_BLUE      = "\x1b[44m"
    BG_MAGENTA   = "\x1b[45m"
    BG_CYAN      = "\x1b[46m"
    BG_WHITE     = "\x1b[47m"
    BG_DEFAULT   = "\x1b[49m"
    
    FG_BOLD_ON   = "\x1b[01m"
    FG_BOLD_OFF  = "\x1b[21m"
    FG_ULINE_ON  = "\x1b[4m"
    FG_ULINE_OFF = "\x1b[24m"
    
    # Modifiers
    NONE         = 0x0
    BOLD         = 0x1
    UNDERLINE    = 0x2

    @classmethod
    def colored(cls, s, foreground_color=FG_DEFAULT, modifiers=NONE):
        toPrint = foreground_color + s + Color.FG_DEFAULT
        print(toPrint)

