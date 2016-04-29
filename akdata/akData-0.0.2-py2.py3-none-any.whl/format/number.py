from decimal import Decimal


def formatDollars(d,noneValue='',zeroValue='$0'):
    """Formats a number as a whole dollar value with alternatives for None and 0."""
    if d is None:
        return noneValue
    elif d==0:
        return zeroValue
    return '${:.0f}'.format(d)

def formatDollarsCents(d,noneValue='',zeroValue='$0.00'):
    """Formats a number as a dollar and cent value with alternatives for None and 0."""
    if d is None:
        return noneValue
    elif d==0:
        return zeroValue
    return '${:.2f}'.format(d)


def formatInteger(n,noneValue='',zeroValue='0'):
    """Formats an integer with alternatives for None and 0."""
    if n is None:
        return emptyValue
    elif n==0:
        return zeroValue
    return '{:d}'.format(n)


def formatDecimal(n,precision,noneValue='',zeroValue='0'):
    """Formats a decimal with alternatives for None and 0."""
    if n is None:
        return emptyValue
    elif n==0:
        return zeroValue
    return '{:.{}f}'.format(n,precision)


def formatPercentage(n,outOf,decimalPlaces=0,noneValue='',zeroValue='0%'):
    """Formats a percentage with alternatives for None and 0."""
    if n is None:
        return emptyValue
    elif n==0:
        return zeroValue
    if not isinstance(n,Decimal): n=Decimal('{}'.format(n))
    if not isinstance(outOf,Decimal): outOf=Decimal('{}'.format(outOf))
    percent=n*100/outOf
    return '{:0.{}f}%'.format(percent,decimalPlaces)
