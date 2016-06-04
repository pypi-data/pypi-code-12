import json
import os
import inspect
import re
from collections import namedtuple

import inflect
import sqlalchemy
from sqlalchemy.ext.automap import automap_base, generate_relationship, name_for_collection_relationship, name_for_scalar_relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.collections import attribute_mapped_collection

from iacorpus.utilities.misc import ProgressReporter, tablerepr, lazy_property

from iacorpus.datasets.generic import orm

SQLConnection = namedtuple('SQLConnection', ['engine', 'metadata', 'Base', 'session'])

class Dataset:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.database_name = kwargs['database_name'] if 'database_name' in kwargs else self.name

        self._class_table_map = dict()  # TODO: look this up from metadata or something
        # if self.connection is None:  # TODO: make singleton

        self.connection = self._load_connection(self.database_name, **kwargs)

    def __iter__(self):
        iterator = self.get_discussions()
        return iterator

    def get_discussions(self, max_discussions=None, discussion_list=None, report_progress=True, lock=None):
        class Iterator:
            def __init__(self, id_list, should_report_progress, parent):
                self.id_list = id_list
                self.progress = ProgressReporter(len(discussion_list), text='On ', lock=lock) if should_report_progress else None
                self.curr = 0
                self.parent = parent
            def __iter__(self):
                return self
            def __next__(self):
                if self.progress is not None:
                    self.progress.report()
                if self.curr >= len(self.id_list):
                    raise StopIteration
                else:
                    id = self.id_list[self.curr]
                    self.curr += 1
                    discussion = self.parent.load_discussion(id)
                    return discussion

        if discussion_list is None:
            discussion_list = self.get_discussion_ids(max_discussions=max_discussions)

        iterator = Iterator(discussion_list, report_progress, self)
        return iterator

    def get_discussion_ids(self, max_discussions=None) -> [1, 2]:
        table = sqlalchemy.Table('discussion', self.connection.metadata, autoload=True)
        q = sqlalchemy.select([table.c.discussion_id], limit=max_discussions)
        result = q.execute()
        discussion_ids = [entry[0] for entry in result]
        return discussion_ids

    def load_discussion(self, discussion_id):
        cls = self.connection.Base.classes.Discussion
        q = self.connection.session.query(cls).filter_by(discussion_id=discussion_id)
        discussion = q.scalar()
        return discussion

    def has_table(self, table_name):
        return self.connection.metadata.bind.has_table(table_name)

    @lazy_property
    def dataset_metadata(self):
        result = self.connection.session.query(self.connection.Base.classes.DatasetMetadata).all()
        metadata = {obj.metadata_field: obj.metadata_value for obj in result}
        return metadata


    def _load_connection(self, database_name, **kwargs):
        connection_details = self._load_connection_details()
        connection_details.update(kwargs)

        engine = self._setup_engine(database_name, **connection_details)
        metadata = sqlalchemy.MetaData(bind=engine)
        Base = self._setup_base(engine, metadata, database_name)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        session = Session()
        connection = SQLConnection(engine=engine, metadata=metadata, Base=Base, session=session)
        return connection

    def _setup_engine(self, database_name, dbapi, host, port, username, password):
        _connection_string = dbapi + '://' + username
        if password is not None:
            _connection_string += ':' + password
        _connection_string += '@' + host + ':' + port + '/' + database_name + '?charset=utf8mb4'

        engine = sqlalchemy.create_engine(_connection_string)
        return engine

    def _load_connection_details(self, filename=None, configuration_name=None):
        connection_details = {"host":"localhost",
                              "port":"3306",
                              "username":"iacuser",
                              "password":None,
                              "dbapi":"mysql+mysqldb"}
        if filename is None:
            filename = os.environ.get('IAC_CONNECTION_DETAILS')
        if filename is not None and os.path.exists(filename):
            connection_details_file = open(filename)
            connection_details_raw = json.load(connection_details_file)
            if configuration_name is None:
                configuration_name = connection_details_raw['default_configuration']
            connection_details.update(connection_details_raw[configuration_name])
        return connection_details

    def _setup_base(self, engine, metadata, database_name):
        Base = automap_base(metadata=metadata)
        classes = self.build_classes(Base, engine)
        for cls in classes:
            setattr(Base.classes, cls.__name__, cls)
        try:
            Base.prepare(engine, reflect=True,
                         classname_for_table=self._classname_for_table,
                         name_for_scalar_relationship=self._name_for_scalar_relationship,
                         name_for_collection_relationship=self._name_for_collection_relationship,
                         generate_relationship=self._generate_relationship
                         )
        except:
            print('Did you spell the dataset_name correctly?', '"', str(database_name), '"')
            raise
        Base.__repr__ = tablerepr
        return Base

    def build_classes(self, Base, engine):
        """This allows a dataset to add functions and details to automapped classes before they're constructed
        Could also monkey patch them in if you really wanted to"""
        classes = list()
        # TODO: if one in module/orm/, use that, otherwise use one in super/orm/ ...
        #  ... or.. just let subs implement this function
        for name, obj in inspect.getmembers(orm, inspect.ismodule):
            if engine.has_table(name):  # TODO: and not already built
                cls = obj.build_class(Base, engine)
                classes.append(cls)
        return classes

    def _classname_for_table(self, base, tablename, table):
        new_name = self._camelize_classname(base, tablename, table)
        self._class_table_map[new_name] = tablename
        return new_name

    def _camelize_classname(self, base, tablename, table):
        "Produce a 'camelized' class name, e.g. "
        "'words_and_underscores' -> 'WordsAndUnderscores'"
        return str(tablename[0].upper() + re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))

    def _name_for_scalar_relationship(self, base, local_cls, referred_cls, constraint):
        referred_class_name = referred_cls.__name__
        if referred_class_name.lower() in {'text', 'word'}:
            return referred_class_name.lower() + '_obj'
        return name_for_scalar_relationship(base, local_cls, referred_cls, constraint)

    _pluralizer = inflect.engine()
    def _name_for_collection_relationship(self, base, local_cls, referred_cls, constraint):
        class_name = local_cls.__name__
        referred_class_name = referred_cls.__name__
        collection_lookup = {('Discussion', 'Post'): 'posts', ('Post', 'Quote'): 'all_quotes'}
        collection_name = collection_lookup.get((class_name, referred_class_name))
        if collection_name is not  None:
            return collection_name
        else:
            if referred_class_name in self._class_table_map:
                referred_class_name = self._class_table_map[referred_class_name]
            else:
                referred_class_name = referred_class_name.lower()
            pluralized = self._pluralizer.plural(referred_class_name)
            return pluralized

    def _generate_relationship(self, base, direction, return_fn, attrname, local_cls, referred_cls, **kw):
        kw['viewonly'] = True
        class_name = local_cls.__name__
        if class_name == 'Discussion' and attrname == 'posts':
            kw['collection_class'] = attribute_mapped_collection('post_id')
        if class_name == 'Post' and attrname == 'all_quotes':
            kw['collection_class'] = attribute_mapped_collection('quote_index')
        return generate_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw)
