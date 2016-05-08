# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.commandline : 
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

import os
import sys
import cmd
from . import __version__, DEBUG, colored


class CheckPointCmd(cmd.Cmd):
    lastcmd = False
    prompt = colored('[EDAS Detector]> ', 'blue')

    def emptyline(self):
        pass

    def do_check(self, cp):
        """
        check all                    : check all check points
        check [check_id]             : run all check points blongs to the check_id
        check [check_id].[point_id]  : run only the given check point.
        """
        from edsd.facade import checks, failed_point, show_failed_report

        try:
            del failed_point[:]

            if cp.lower() == 'all':
                for check in checks:
                    check.check()
                return

            check_id, point_id = self.parse_cp(cp)
            if check_id is not None:
                checks[check_id].check(point_id)
                return
        except:
            if DEBUG:
                import traceback
                traceback.print_exc()
        finally:
            if len(failed_point) > 0:
                show_failed_report()
        print "\tcheck id parsed from '{0}' is not found".format(cp)

    def do_list(self, cp):
        """
        list                          : list all the checks
        list [check_id]               : list all the check points belongs to the check_id
        list [check_id].[point_id]    : list the given check  point info.
        """
        from edsd.facade import checks
        if not cp:
            for c in checks:
                c.print_me()
            return

        check_id, point_id = self.parse_cp(cp)
        if check_id is not None:
            checks[check_id].print_me(point_id, detail=True)
            return

        print "\tcheck id parsed from '{0}' is not found".format(cp)

    def do_view(self, cp):
        """
        view                          : view the solution of last fail checkpoint.
        view [check_id].[point_id]    : view the given check point's solution.
        """
        from edsd.facade import checks, show_failed_report

        if not cp:
            # print last failed solution.
            show_failed_report()
            return

        check_id, point_id = self.parse_cp(cp)
        if check_id is not None and point_id is not None:
            checks[check_id].view_solution(point_id)
            return

        print "\tcheck point parsed from '{0}' is not found".format(cp)

    def do_collect(self, _):
        """
        collect                       : collect edas environment runtime information,
                                        and package the information under /tmp/edas-collect/.
        """
        import edsd.collect
        edsd.collect.collect()

    def precmd(self, line):
        return line.lower()

    def parse_cp(self, cp):
        import re
        from edsd.facade import checks

        c = re.compile('(\d+)(?:\.(\d+))?')
        m = c.match(cp)
        if not m:
            return None, None

        check_id, point_id = m.groups()
        check_id = int(check_id) - 1 if check_id and check_id.isdigit() else None

        if check_id is not None and 0 <= check_id < len(checks):
            point_id = int(point_id) - 1\
                if point_id and point_id.isdigit() else None

        return check_id, point_id

    def do_verbose(self, cp):
        """
        verbose [on/off]               : switch on/off the debug mode, in order to
                                         view more information during the execution
        """
        cp = cp.lower().strip()
        global DEBUG
        try:
            if not cp: return

            if cp == 'on' or cp == 'true' or cp == '1':
                DEBUG = True
            elif cp == 'off' or cp == 'false' or cp == '0':
                DEBUG = False
        finally:
            print 'current verbose status is "%s"' % \
                  ('on' if DEBUG else 'off')

    def completedefault(self, *ignored):
        return ['help ', 'exit ', 'view ', 'list ', 'quit ', 'check ']

    def do_exit(self, _):
        sys.exit(0)

    def do_quit(self, _):
        sys.exit(0)

    def do_q(self, _):
        sys.exit(0)

    def do_EOF(self, _):
        sys.exit(0)

    def default(self, line):
        print "Command not found: '%s' " % line

