# coding: utf-8
from collections import defaultdict
from pandas import DataFrame


def flatten_dict(d, delimiter='.'):
    def items():
        for key, val in d.items():
            if isinstance(val, dict):
                for subkey, subval in flatten_dict(val, delimiter).items():
                    yield delimiter.join((key, subkey)), subval
            else:
                yield key, val
    return dict(items())


def day_data(data, prefix='data'):
    result = defaultdict(list)
    for item in data:
        for key, val in item.items():
            key = '{}.{}'.format(prefix, key)
            result[key].append(val)
    return result


def parse(mat_data, include_days=True):
    df_rows = []

    if include_days:
        for item in mat_data:
            meta = flatten_dict(item['meta'])
            meta.update(day_data(item['data']))
            df_rows.append(meta)
    else:
        for item in mat_data:
            meta = flatten_dict(item['meta'])
            df_rows.append(meta)
    df = DataFrame(df_rows)
    return df
