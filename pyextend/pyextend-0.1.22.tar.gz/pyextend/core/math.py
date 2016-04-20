# coding: utf-8
"""
    pyextend.core.math
    ~~~~~~~~~~~~~~~~~~
    pyextend core math tools.

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""


def isprime(n):
    """Check the number is prime value. if prime value returns True, not False."""
    n = abs(int(n))

    if n < 2:
        return False
    if n == 2:
        return True
    if not n & 1:
        return False

    # 在一般领域, 对正整数n, 如果用2 到 sqrt(n) 之间所有整数去除, 均无法整除, 则n为质数.
    for x in range(3, int(n ** 0.5)+1, 2):
        if n % x == 0:
            return False

    return True
