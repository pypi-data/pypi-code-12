from dateutil.parser import parse as parse_date


def parse_date_safely(x):
    x = str(x)
    try:
        return parse_date(x)
    except ValueError:
        # http://stackoverflow.com/questions/14595401
        return parse_date(x + '-01-01')
