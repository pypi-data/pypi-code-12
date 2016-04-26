from __future__ import print_function, unicode_literals
from .io import load
from .utils import get_nodes_by_type, has_valid_types, sniff_cycles, flatten_records, flatten_tables
from .transformers import JSON, Java
from .logger import LOG

__author__ = "danishabdullah"


def workflow(filename, output_type='dict'):
    assert output_type in ('json', 'java', 'dict')
    spec = load(filename)
    records = get_nodes_by_type(spec)
    tables = get_nodes_by_type(spec, 'table')
    has_valid_types(spec, records)
    sniff_cycles(records)
    flatten_records(records)
    flatten_tables(tables, records)
    res = {}
    LOG.info("Transforming to '{}'".format(output_type.upper()))
    if output_type == 'json':
        transformer = JSON()
        for k, v in tables.items():
            res[k] = transformer.table(fields=v['fields'])
        return res
    elif output_type == 'java':
        transformer = Java()
        return {"pipeline": transformer.spec(tables)}
    elif output_type == 'dict':
        return tables
    else:
        raise ValueError("This should never happen")
