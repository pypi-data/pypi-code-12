import re
from datetime import date
import termcolor


class DateParser():
    def __init__(self, line):
        self.DATE_RE = '([0-9]{1,2})\-([0-9]{1,2})-([0-9]{4})'
        self.THRESHOLD = 5
        self.CRITICAL = '[CRITICAL]'
        self.OVERDUE = '[OVERDUE]'
        self.NORMAL = '[NORMAL]'
        self.ONDUE = '[ONDUE]'
        self.line = line

    def parse(self):
        if self.get_date():
            todo_date = self.get_date()
            curr_date = date.today()
            diff = (todo_date - curr_date).days
            if diff >= self.THRESHOLD:
                return termcolor.colored(self.NORMAL, 'green',
                                         attrs=['bold'])
            elif self.THRESHOLD > diff > 0:
                return termcolor.colored(self.CRITICAL, 'yellow',
                                         attrs=['bold'])
            elif diff == 0:
                return termcolor.colored(self.ONDUE, 'red',
                                         attrs=['bold'])
            elif diff < 0:
                return termcolor.colored(self.OVERDUE, 'red',
                                         attrs=['bold'])
        else:
            return termcolor.colored('[NO-DUE]', 'yellow', attrs=['bold'])

    def get_date(self):
        match = re.search(self.DATE_RE, self.line)
        if hasattr(match, 'groups'):
            if len(match.groups()) == 3:
                todo_date = date(int(match.group(3)), int(match.group(2)),
                                 int(match.group(1)))
                return todo_date
            else:
                return None
