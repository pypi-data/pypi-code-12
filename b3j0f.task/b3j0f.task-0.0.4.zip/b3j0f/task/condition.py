# -*- coding: utf-8 -*-
# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""
Task condition functions such as duration/rrule condition, switch, all and any.
"""

__all__ = ['during', '_any', '_all', '_not', 'condition', 'switch']

from six import string_types
from .core import register, run

from time import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule as rrule_class


@register('during')
def during(rrule, duration=None, timestamp=None, **kwargs):
    """
    Check if input timestamp is in rrule+duration period

    :param rrule: rrule to check
    :type rrule: str or dict
        (freq, dtstart, interval, count, wkst, until, bymonth, byminute, etc.)
    :param dict duration: time duration from rrule step. Ex:{'minutes': 60}
    :param float timestamp: timestamp to check between rrule+duration. If None,
        use now
    """

    result = False

    # if rrule is a string expression
    if isinstance(rrule, string_types):
        rrule_object = rrule_class.rrulestr(rrule)

    else:
        rrule_object = rrule_class(**rrule)

    # if timestamp is None, use now
    if timestamp is None:
        timestamp = time()

    # get now object
    now = datetime.fromtimestamp(timestamp)

    # get delta object
    duration_delta = now if duration is None else relativedelta(**duration)

    # get last date
    last_date = rrule_object.before(now, inc=True)

    # if a previous date exists
    if last_date is not None:
        next_date = last_date + duration_delta

        # check if now is between last_date and next_date
        result = last_date <= now <= next_date

    return result


@register('any')
def _any(confs=None, **kwargs):
    """
    True iif at least one input condition is equivalent to True.

    :param confs: confs to check.
    :type confs: list or dict or str
    :param kwargs: additional task kwargs.

    :return: True if at least one condition is checked (compared to True, but
            not an strict equivalence to True). False otherwise.
    :rtype: bool
    """

    result = False

    if confs is not None:
        # ensure confs is a list
        if isinstance(confs, string_types) or isinstance(confs, dict):
            confs = [confs]
        for conf in confs:
            result = run(conf, **kwargs)
            if result:  # leave function as soon as a result if True
                break

    return result


@register('all')
def _all(confs=None, **kwargs):
    """
    True iif all input confs are True.

    :param confs: confs to check.
    :type confs: list or dict or str
    :param kwargs: additional task kwargs.

    :return: True if all conditions are checked. False otherwise.
    :rtype: bool
    """

    result = False

    if confs is not None:
        # ensure confs is a list
        if isinstance(confs, string_types) or isinstance(confs, dict):
            confs = [confs]
        # if at least one conf exists, result is True by default
        result = True
        for conf in confs:
            result = run(conf, **kwargs)
            # stop when a result is False
            if not result:
                break

    return result


STATEMENT = 'statement'


@register('not')
def _not(condition=None, **kwargs):
    """
    Return the opposite of input condition.

    :param condition: condition to process.

    :result: not condition.
    :rtype: bool
    """

    result = True

    if condition is not None:
        result = not run(condition, **kwargs)

    return result


@register('condition')
def condition(condition=None, statement=None, _else=None, **kwargs):
    """
    Run an statement if input condition is checked and return statement result.

    :param condition: condition to check.
    :type condition: str or dict
    :param statement: statement to process if condition is checked.
    :type statement: str or dict
    :param _else: else statement.
    :type _else: str or dict
    :param kwargs: condition and statement additional parameters.

    :return: statement result.
    """

    result = None

    checked = False

    if condition is not None:
        checked = run(condition, **kwargs)

    if checked:  # if condition is checked
        if statement is not None:  # process statement
            result = run(statement, **kwargs)

    elif _else is not None:  # else process _else statement
        result = run(_else, **kwargs)

    return result


@register('switch')
def switch(
        confs=None, remain=False, all_checked=False, _default=None, **kwargs
):
    """
    Execute first statement among conf where task result is True.
    If remain, process all statements conf starting from the first checked
    conf.

    :param confs: task confs to check. Each one may contain a task action at
        the key 'action' in conf.
    :type confs: str or dict or list
    :param bool remain: if True, execute all remaining actions after the
        first checked condition.
    :param bool all_checked: execute all statements where conditions are
        checked.
    :param _default: default task to process if others have not been checked.
    :type _default: str or dict

    :return: statement result or list of statement results if remain.
    :rtype: list or object
    """

    # init result
    result = [] if remain else None

        # check if remain and one task has already been checked.
    remaining = False

    if confs is not None:
        if isinstance(confs, string_types) or isinstance(confs, dict):
            confs = [confs]

        for conf in confs:
            # check if task has to be checked or not
            check = remaining

            if not check:
                # try to check current conf
                check = run(conf=conf, **kwargs)

            # if task is checked or remaining
            if check:

                if STATEMENT in conf:  # if statements exist, run them
                    statement = conf[STATEMENT]
                    statement_result = run(statement, **kwargs)

                    # save result
                    if not remain:  # if not remain, result is statement_result
                        result = statement_result

                    else:  # else, add statement_result to result
                        result.append(statement_result)

                # if remain
                if remain:
                    # change of remaining status
                    if not remaining:
                        remaining = True

                elif all_checked:
                    pass

                else:  # leave execution if one statement has been executed
                    break

    # process _default statement if necessary
    if _default is not None and (remaining or (not result) or all_checked):
        last_result = run(_default, **kwargs)

        if not remain:
            result = last_result

        else:
            result.append(last_result)

    return result
