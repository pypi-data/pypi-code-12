"""handy math and statistics routines

Supported Number sets
---------------------

  *  {int} = Set of integers
  *  {float} = Set of float
  *  {decimal} = Set of Decimal
  *  {mixed-float} = {float} + {int}
  *  {mixed-decimal} = {decimal} + {int}

Return Type Precedence
-----------------------
The type returned is based on the function, input type(s), The simplest
meaningful type is returned.

  * bool
  * int
  * float
  * Decimal
"""
# :math: - https://en.wikipedia.org/wiki/Help:Displaying_a_formula#Sets
# std py3k stanza
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import Counter
from math import log, pi, factorial


class MathError(ValueError):
    '''general math error'''
    pass


class UndefinedError(MathError):
    '''When the calculation is undefined for the given input.'''
    pass


# pylint: disable=W1401
def fequal(num1, num2, delta=0.000001):
    """Compare equivalency of two numbers to a given delta.

    Both num1 and num2 must be from the same set of {mixed-float} OR
    {mixed-decimal}.

    :math:`num1 \equiv num2 \iff |num1 - num2| < delta`

    Args:
        num1 ({mixed-float}|{mixed-decimal}): The first number to compare.
        num2 (num1): The second number to compare.
        delta (float): The amount of difference allowed for equivalence.
            (default: 0.000001)

    Returns:
        (bool): True if the absolute difference between `num1` and `num2` is
            less than `delta`, else False.

    Raises:
        TypeError: If testing a float and a Decimal.
    """
    return abs(num1 - num2) < delta


def is_even(num):
    '''Return True if num is even, else False.

    An integer is even if it is 'evenly divisible' by two.

    :math:`Even = \{ 2k : k \in Z\}`

    Args:
        num (int): The num to check.
    Returns:
        (bool): True if num is even, else False.
    Raises:
        (MathError): If num is not an integer.
    '''
    if not isinstance(num, int):
        raise MathError('Only Integers can be Even.')
    return num % 2 == 0


def is_odd(num):
    '''r\Return True if num is odd, else False.

    An integer is odd if it is not even.

    :math:`Odd = \{ 2k+1 : k \in Z\}`

    A number expressed in the binary is odd if its last digit is 1 and even if
    its last digit is 0.

    Args:
        num (int): The num to check.
    Returns:
        (bool): True if num is odd, else False.
    Raises:
        (MathError): If num is not an integer.
    '''
    if not isinstance(num, int):
        raise MathError('Only Integers can be Odd.')
    return bool(num & 1)


def mean(nums):
    """Return the arithmetic mean of the list of numbers

    :math:`\\bar{X} = \dfrac{x_1 + x_2 + ... +x_N}{N}`
    :math:`= \dfrac{\sum_{i=1}^N x_i}{N}`

    Args:
        nums(list): list of numbers ({mixed-float}|{mixed-Decimal})

    Returns:
        (float|decimal): Arithmetic Mean of the list.

    Raises:
        (UndefinedError):If nums is empty. :math:`N = 0`
        (TypeError): If nums contains both float and Decimal numbers.
    """

    try:
        return sum(nums) / len(nums)
    except ZeroDivisionError:
        raise UndefinedError('mean of an empty list is undefined')


def gmean(nums):
    '''Return the geometric mean of the list of numbers.

    :math:`G = (x_1 * x_2 * ... * x_N)^\\tfrac{1}{N}`
    :math:`= (\prod_{i=1}^N x_i)^\\tfrac{1}{N}`

    Args:
        nums(list): list of numbers ({mixed-float}|{mixed-decimal})

    Returns:
        (float|decimal): Geometric Mean of the list.

    Raises:
        (UndefinedError):If nums is empty. :math:`N = 0`
        (TypeError): If nums contains both float and Decimal numbers.
    '''
    if not nums:
        raise UndefinedError('gmean of an empty list is undefined')
    accum = nums[0]
    for num in nums[1:]:
        accum *= num
    return accum**(1 / type(accum)(len(nums)))


def hmean(nums):
    '''Return the harmonic mean of a list of numbers.

    :math:`H = \dfrac{N}{\\tfrac{1}{x_1}+\\tfrac{1}{x_1}+...+\\tfrac{1}{x_N}}
    =\dfrac{N}{\sum_{i=1}^N \\tfrac{1}{x_i}}`

    Args:
        nums(list): list of numbers ({mixed-float}|{mixed-decimal})

    Returns:
        (float|decimal): Harmonic Mean of the list.

    Raises:
        (UndefinedError):If the list is empty. :math:`N = 0`
    '''
    try:
        return len(nums) / sum([1/x for x in nums])
    except ZeroDivisionError:
        raise UndefinedError('hmean of an empty list is undefined')


def median(nums):
    '''Return the median value from the list.

    Given: :math:`a < b < c < d`
    The median of the list [a, b, c] is b, and,
    the median of the list [a, b, c, d] is the mean
    of b and c; i.e. :math:`\dfrac{b + c}{2}`

    Args:
        nums (list):list of numbers ({mixed-float}|{mixed-decimal})

    Returns:
        (int|float|decimal):The median of the list of numbers.
    '''
    sorted_nums = sorted(nums)
    size = len(sorted_nums)
    if size == 0:
        raise UndefinedError('median of an empty list is undefined')
    mid = size // 2
    if is_even(size):
        return mean(sorted_nums[mid-1:mid+1])
    else:
        return sorted_nums[mid]


def pvariance(lst):
    '''return the population variance for the list of numbers'''
    mu = mean([x for x in lst])     # pylint:disable=c0103
    return sum([(x-mu)**2 for x in lst])/len(lst)


def svariance(lst):
    '''return the sample population variance for the list of numbers'''
    xbar = mean([float(x) for x in lst])
    return sum([(x-xbar)**2 for x in lst])/(len(lst) - 1)


def pstddev(lst):
    """return the population standard deviation of the elements in the list"""
    return pvariance(lst)**.5


def sstddev(lst):
    """return the sample standard deviation of the elements in the list"""
    return svariance(lst)**.5


def mode(lst):
    '''Return the mode (most common element value) from the list.

    Args:
        lst(list):list of hashable objects to search for the mode.

    Returns:
        (list element): The most common value in lst.

    Raises:
        (UndefinedError): If lst is empty.
        (MathError): If lst is multi-modal.
    '''
    if not lst:
        raise UndefinedError('mode of an empty list is undefined.')
    cntr = Counter(lst)
    # test for multi-modal
    cnts = cntr.most_common(2)
    if cnts[0][1] == cnts[1][1]:
        raise MathError('Mutiple Modes found')
    return cnts[0][0]


def ttest_independent(lst1, lst2):
    '''calc the ttest for two independent samples'''
    cnt1 = len(lst1)
    cnt2 = len(lst2)
    term1 = (((cnt1-1) * sstddev(lst1)**2) + ((cnt2-1) * sstddev(lst2)**2))
    term1 /= (cnt1+cnt2-2)
    term2 = (cnt1 + cnt2)/(cnt1*cnt2)
    return (mean(lst1) - mean(lst2))/(term1 * term2)**.5


# def ttest_dependent(lst, lst_prime):
#     '''calculate the ttest for two dependent samples. i.e. pre/post'''
#     pass


def log_nfactorial(n):      # pylint:disable=c0103
    """calculate approximation of log n! using Srinivasa Ramanujan's
    approximation of log n!

    :math:`\log n! \\approx n\log n - n+\\dfrac{\log(n(1+4n(1+2n)))}
    {6}+\\dfrac{\log(\pi)}{2}`

    Args:
        n(int): a very large integer

    Returns:
        (float): log n!

    """
    return n * log(n) - n + (log(n * (1 + 4*n * (1 + 2*n)))/6) + (log(pi)/2)


def prob_unique(nvals, ssize):
    """return the Probability of Uniqueness given:

    where N is nvals and r is ssize:

    :math:`p = \\dfrac {N!} {N^r (N-r)!}`

    Args:
        nvals (int): number of unique points (i.e. birthdays=365)
        ssize (int): size of sample (i.e. people)

    Returns:
        (float): probability that all samples are unique

    """
    return factorial(nvals) / ((nvals**ssize) * factorial(nvals-ssize))


def choose(n, k):       # pylint:disable=c0103
    """Return the number of combinations of n choose k (nCk).

    :math:`\\dbinom{n}{k} = \\dfrac{n!}{k!(n-k)!}` when :math:`k<n` and 0 for
    :math:`k>n`

    Args:
        n (int): the size of the pool of choices
        k (int): the size of the sample

    Returns:
        (int): the number of k-combinations of pool size n

    """
    if not 0 <= k <= n:  # sanity check
        return 0
    # simple optimizations
    if k == n or k == 0:
        return 1
    if k > n // 2:  # make k equivalent but smaller
        k = n - k
    return factorial(n) // (factorial(k) * factorial(n-k))
