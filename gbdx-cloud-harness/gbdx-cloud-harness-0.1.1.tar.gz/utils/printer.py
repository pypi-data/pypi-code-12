import json
import sys


def printer(data):
    """
    response is json or straight text.
    :param data:
    :return:
    """
    data = str(data) # Get rid of unicode
    if not isinstance(data, str):
        output = json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    elif hasattr(data, 'json'):
        output = data.json()
    else:
        output = data

    sys.stdout.write(output)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return
