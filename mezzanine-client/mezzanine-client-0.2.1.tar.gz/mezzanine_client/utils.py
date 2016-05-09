class TerminalColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def str_header(_str):
    return TerminalColors.HEADER + _str + TerminalColors.RESET


def str_warning(_str):
    return TerminalColors.WARNING + _str + TerminalColors.RESET


def str_green(_str):
    return TerminalColors.GREEN + _str + TerminalColors.RESET


def str_blue(_str):
    return TerminalColors.BLUE + _str + TerminalColors.RESET
