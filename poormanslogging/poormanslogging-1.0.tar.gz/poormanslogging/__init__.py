# -*- coding: utf-8 -*-

import time
import itertools
import sys
import random

import colorama

spins = itertools.cycle(['|', '/', '-', '\\'])


def error(msg):
    print('[!] - {t} {red}|{reset} {m}'.format(red=colorama.Fore.RED, reset=colorama.Style.RESET_ALL, t=time.strftime('%H:%M:%S'), m=msg))


def warn(msg):
    print('[~] - {t} {red}|{reset} {m}'.format(red=colorama.Fore.YELLOW, reset=colorama.Style.RESET_ALL, t=time.strftime('%H:%M:%S'), m=msg))


def info(msg):
    print('[·] - {t} {green}|{reset} {m}'.format(green=colorama.Fore.GREEN, reset=colorama.Style.RESET_ALL, t=time.strftime('%H:%M:%S'), m=msg))


def wait_while(msg, lamb, oper, expected, pausebetween):
    """Call a lambda every a given number of seconds,
    WHILE the result of the lambda matches the expectation considering the given operator.
    All the while printing a message containing a spinner.
    Args:
        msg: Message to display while waiting
        lamb: Lambda to call (example: `lambda: foo(bar, baz)`)
        oper: Operator (from the `operator` module) to compare the lambda result and the expectation
        expected: What the lambda will give out while we wait
        pausebetween: Time between calls to the lambda
    """
    __waiter(msg, lamb, oper, False, expected, pausebetween)


def wait_until(msg, lamb, oper, expected, pausebetween):
    """Call a lambda every a given number of seconds,
    UNTIL the result of the lambda matches the expectation considering the given operator.
    All the while printing a message containing a spinner.
    Args:
        msg: Message to display while waiting
        lamb: Lambda to call (example: `lambda: foo(bar, baz)`)
        oper: Operator (from the `operator` module) to compare the lambda result and the expectation
        expected: What the lambda should return for the polling to end
        pausebetween: Time between calls to the lambda
    """
    __waiter(msg, lamb, oper, True, expected, pausebetween)


def __waiter(msg, lamb, oper, negated, expected, pausebetween):
    def do_print():
        mess = '[·] {s} {t} {green}|{reset} {m}'.format(s=next(spins), green=colorama.Fore.GREEN, reset=colorama.Style.RESET_ALL, t=time.strftime('%H:%M:%S'), m=msg)
        sys.stdout.write('\r' + mess)
        sys.stdout.flush()
        time.sleep(pausebetween)

    if negated:
        while not oper(lamb(), expected):
            do_print()
    else:
        while oper(lamb(), expected):
            do_print()
    sys.stdout.write('\n')
