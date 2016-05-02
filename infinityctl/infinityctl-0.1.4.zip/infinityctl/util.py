import sys
import shutil

def print_status(T):
    (width, height) = shutil.get_terminal_size()
    if T == "OK":
        msg = "[\033[92m OK \033[0m]\n"
        sys.stdout.write(msg.rjust(23, '.'))
    elif T == "FAIL":
        msg = "[\033[91m FAIL \033[0m]\n"
        sys.stdout.write(msg.rjust(23, '.'))
    pass
