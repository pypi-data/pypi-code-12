
import fcntl
import struct
import sys
import termios

import wayround_org.utils.text


def get_terminal_size(fd=1):
    res = None
    io_res = None
    arg = struct.pack('HHHH', 0, 0, 0, 0)

    try:
        io_res = fcntl.ioctl(
            fd,
            termios.TIOCGWINSZ,
            arg
            )
    except:
        res = None
    else:
        try:
            res = struct.unpack('HHHH', io_res)
        except:
            res = None

    if res is not None:
        res = {
            'ws_row': res[0],
            'ws_col': res[1],
            'ws_xpixel': res[2],
            'ws_ypixel': res[3]
            }

    return res


# TODO: output descriptor selector
def progress_write_finish():
    sys.stdout.write('\n')
    sys.stdout.flush()
    return


# TODO: output descriptor selector
def progress_write(line_to_write, new_line=False):

    new_line_str = ''

    if line_to_write.endswith('\n'):
        new_line = True
        line_to_write = line_to_write.rstrip('\n')

    if new_line:
        new_line = True
        new_line_str = '\n'

    width = 80
    ts = get_terminal_size(sys.stdout.fileno())
    if ts is not None:
        width = ts['ws_col']

    line_to_write_l = len(line_to_write)

    line_to_out = '\r{ltw}{spaces}{new_line}\r'.format_map(
        {
            'ltw': line_to_write,
            'spaces': ' ' * (width - line_to_write_l),
            'new_line': new_line_str
            }
        )

    if len(line_to_out) > width:
        line_to_out = line_to_out[:width + 1] + new_line_str + '\r'

    # TODO: put sys.stdout to parameters

    sys.stdout.write(line_to_out)
    sys.stdout.flush()
    return
