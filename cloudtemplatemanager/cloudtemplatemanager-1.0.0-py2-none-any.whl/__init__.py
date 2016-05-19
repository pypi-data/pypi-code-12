import json


def json_pprint(data):
    print(json.dumps(
        data,
        sort_keys=True,
        indent=4,
        separators=(',', ': '),
        cls=CommonJSONEncoder
    ))


class CommonJSONEncoder(json.JSONEncoder):
    """
    Common JSON Encoder
    json.dumps(myString, cls=CommonJSONEncoder)
    """

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
