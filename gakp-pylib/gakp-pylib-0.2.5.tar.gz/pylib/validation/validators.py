from decimal import Decimal


def float_validator(size, dplaces):
    def val(num):
        num = str(num)
        dec = Decimal(num).as_tuple()
        return (abs(dec.exponent) <= dplaces and
                len(dec.digits) <= size)
    return val


def enum(*options):
    def check(val):
        return val in options
    return check
