def do_sum(args):
    """Calculate the sum of numbers.

    ...

    >>> import argparse
    >>> args = argparse.Namespace()
    >>> args.number = []
    >>> do_sum(args)
    Calculating the sum of []
    0
    0

    >>> args.number = [1]
    >>> do_sum(args)
    Calculating the sum of [1]
    1
    1

    >>> args.number = [1,2]
    >>> do_sum(args)
    Calculating the sum of [1, 2]
    3
    3
    """

    print "Calculating the sum of", args.number
    print sum(args.number)
    return sum(args.number)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
