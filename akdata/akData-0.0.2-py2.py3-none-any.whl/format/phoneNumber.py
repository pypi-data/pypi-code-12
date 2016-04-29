def formatPhoneNumber(n,locale='au'):
    if locale=='au':
        return formatAustralianPhoneNumber(n)
    else:
        raise NotImplemented('Only AU implemented so far')


def formatAustralianPhoneNumber(n):
    """Formats a string of numbers (no spaces) into an Australian mobile or landline."""
    if len(n)!=10:
        return n
    if n[1]=='4':
        return u'{0} {1} {2}'.format(n[0:4],n[4:7],n[7:10])
    # else assume landline
    return u'({0}) {1} {2}'.format(n[0:2],n[2:6],n[6:10])
