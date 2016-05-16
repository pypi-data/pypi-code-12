# -*- coding: utf-8 -*-
from datetime import datetime


def print_bold(message, bold='\033[1m', default='\033[0m'):
    now = datetime.now().replace(microsecond=0).isoformat(' ')
    print '{} {}{}{}'.format(now, bold, message, default)
