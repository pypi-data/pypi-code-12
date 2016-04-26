from __future__ import print_function, unicode_literals
from string import Template
from .templates import ITEM_JSON, RECORD_JSON, TABLE_JSON, SPEC_JSON, ITEM_JAVA, RECORD_JAVA, TABLE_JAVA, SPEC_JAVA
from .logger import LOG

__author__ = "danishabdullah"


class Base(object):
    def __init__(self, item_template=None, record_template=None, table_template=None, spec_template=None,
                 field_separator=",", table_separator="\n"):
        assert item_template is not None
        assert record_template is not None
        assert table_template is not None
        self.item_template = item_template
        self.record_template = record_template
        self.table_template = table_template
        self.spec_template = spec_template
        self.field_separator = field_separator
        self.table_separator = table_separator

    def _item(self, name=None, type=None, mode=None, path_modifier=''):
        template = self.item_template.safe_substitute(path_modifier=path_modifier)
        template = template.lstrip(".")
        template = Template(template)
        res = template.substitute(name=name, type=type.upper(), mode=mode.upper())
        msg = ("Serializing Item\nIn >> <name: {name}, type: {type}, mode: {mode}. path_modifier: {path_modifier}>"
               "\nOUT << {fmt}: {result}".format(name=name, type=type, mode=mode, path_modifier=path_modifier,
                                                 fmt=self.__class__.__name__, result=res))
        LOG.debug(msg)
        return res

    def _record(self, name=None, type=None, mode=None, fields=None, path_modifier=''):
        assert type == 'record'
        serialized_fields = []
        for field in fields:
            if _is_record(field):
                serialized_fields.append(self._record(**field))
            else:
                serialized_fields.append(self._item(**field))
        template = self.record_template.safe_substitute(path_modifier=path_modifier)
        template = template.lstrip(".")
        template = Template(template)
        serialized_fields = self.field_separator.join(serialized_fields)
        res = template.substitute(name=name, type=type.upper(), mode=mode.upper(),
                                  fields=serialized_fields, path_modifier=path_modifier)
        msg = ("Serializing Record\nIn >> <name: {name}, type: {type}, mode: {mode}. path_modifier: {path_modifier}"
               " fields: {fields}>\nOUT << {fmt}: {result}".format(name=name, type=type, mode=mode, fields=fields,
                                                                   path_modifier=path_modifier,
                                                                   fmt=self.__class__.__name__, result=res))
        LOG.debug(msg)
        return res

    def table(self, name=None, fields=None):
        serialized_fields = []
        for field in fields:
            if _is_record(field):
                serialized_fields.append(self._record(**field))
            else:
                serialized_fields.append(self._item(**field))
        serialized_fields = self.field_separator.join(serialized_fields)
        res = self.table_template.substitute(name=name, fields=serialized_fields)
        msg = ("Serializing Table\nIn >> <name: {name}, fields: {fields}>\nOUT << {fmt}: {result}"
               "".format(name=name, fields=fields, fmt=self.__class__.__name__, result=res))
        LOG.debug(msg)
        return res

    def spec(self, spec):
        Base.insert_path_modifiers_to_spec(spec)
        if not self.spec_template:
            raise NotImplementedError("The spec cannot be serialized by {} transformer".format(self.__class__.__name__))
        serialzed_tables = []
        for k, v in spec.items():
            if _is_table(v):
                tbl = self.table(fields=v['fields'], name=k)
                serialzed_tables.append(tbl)
        serialzed_tables = self.table_separator.join(serialzed_tables)
        res = self.spec_template.substitute(tables=serialzed_tables)
        msg = ("Serializing Spec\nIn >> <spec: {spec}>\nOUT << {fmt}: {result}"
               "".format(spec=spec, fmt=self.__class__.__name__, result=res))
        LOG.debug(msg)
        return res

    @staticmethod
    def insert_path_modifiers_to_spec(spec, modifier="fields"):
        for name, fields in spec.items():
            Base.insert_path_modifiers_to_table(fields, modifier)
        return spec

    @staticmethod
    def insert_path_modifiers_to_table(table, modifier="fields"):
        for item in table.get("fields"):
            if isinstance(item, dict):
                item['path_modifier'] = modifier
        return table


def _is_record(dictionary):
    return dictionary.get('type', None) == 'record'


def _is_table(dictionary):
    return dictionary.get('type', None) == 'table'


class JSON(Base):
    def __init__(self, item_template=ITEM_JSON, record_template=RECORD_JSON, table_template=TABLE_JSON,
                 spec_template=SPEC_JSON):
        super().__init__(item_template, record_template, table_template, spec_template)


class Java(Base):
    def __init__(self, item_template=ITEM_JAVA, record_template=RECORD_JAVA, table_template=TABLE_JAVA,
                 spec_template=SPEC_JAVA):
        super().__init__(item_template, record_template, table_template, spec_template, field_separator="\n")
