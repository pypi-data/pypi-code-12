from __future__ import print_function, unicode_literals
from .consts import BQ_PRIMITIVES
from .logger import LOG

__author__ = "danishabdullah"


def get_nodes_by_type(spec, typ='record'):
    assert typ in ('record', 'table')
    records = {}
    for k, v in spec.items():
        if v.get('type', '').lower() == typ:
            records[k] = v
    return records


def sniff_cycles(spec, records=None, valid_types=None, parent_path=[]):
    LOG.info("Sniffing record cycles.")
    known_records = set([n for n in spec.keys() if n])
    records = records or spec
    if not valid_types:
        tmp = list(BQ_PRIMITIVES)
        tmp.extend(known_records)
        valid_types = set(tmp)
    for k, v in records.items():
        valid = valid_types.copy()
        valid.remove(k)
        fields_types = set([field['type'] for field in v['fields']])
        record_fields = fields_types.difference(BQ_PRIMITIVES)
        path = ".".join(parent_path)
        path = path.upper() + "." if path else ""
        if record_fields:
            msg = "{}{} references: {}".format(path, k.upper(),
                                               ",".join([n.upper() for n in record_fields]))
            LOG.info(msg)
            cycle = record_fields.difference(valid)
            if cycle:
                msg = "{}{} contains cyclical reference to {}".format(path, k.upper(),
                                                                      ",".join([n.upper() for n in cycle]))
                LOG.error(msg)
                raise ValueError(msg)
        child_records = record_fields.intersection(known_records)
        if child_records:
            for record in child_records:
                child_path = parent_path[:]
                child_path.append(k)
                sniff_cycles(spec, {record: spec[record]}, valid, child_path)
    LOG.info("No cyclical references to records found.")


def flatten_records(spec, records=None):
    LOG.info("Flattening records.")
    known_records = set([n for n in spec.keys() if n])
    records = records or spec
    for k, v in records.items():
        fields_types = set([field['type'] for field in v['fields']])
        child_records = fields_types.intersection(known_records)
        for child in child_records:
            for idx, field in enumerate(v['fields']):
                if field['type'] == child:
                    field['type'] = 'record'
                    field['fields'] = spec[child]['fields']
                    child_fields = set([field['type'] for field in field['fields']])
                    grandchild_records = child_fields.intersection(known_records)
                    if grandchild_records:
                        flatten_records(spec, {field['name']: field})
    LOG.debug("Flattened records specification is:\n".format(spec))
    return spec


def flatten_tables(tables, records):
    LOG.info("Flattening tables.")
    known_records = set([n for n in records.keys() if n])
    for k, v in tables.items():
        for field in v['fields']:
            field_type = field['type']
            if field_type in known_records:
                field['fields'] = records[field_type]['fields']
                field['type'] = 'record'
    LOG.debug("Flattened tables specification is:\n".format(tables))
    return tables


def has_valid_types(spec, records_spec):
    def get_types(dictionary, types=[]):
        for k, v in dictionary.items():
            if k == 'type':
                types.append(v)
            elif isinstance(v, dict):
                get_types(v, types)
            else:
                continue
        return set(types)

    records = set(records_spec.keys())
    valid_types = records.union(BQ_PRIMITIVES)
    valid_types_stringified = ", ".join(valid_types)
    LOG.info("Valid types are: {}".format(valid_types_stringified))
    types = get_types(spec)
    types_stringified = ", ".join(types)
    LOG.info("Found these types referenced in the spec: {}".format(types_stringified))
    res = any(n not in valid_types for n in types)
    if res:
        LOG.info("All referenced types are valid")
    else:
        LOG.error("Invalid types referenced")
        raise ValueError("Invalid types referenced")
    return res
