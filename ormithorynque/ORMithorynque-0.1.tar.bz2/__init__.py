# -*- coding: utf-8 -*-
# ORMithorynque
# Copyright (C) 2016 Jean-Baptiste LAMY

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, weakref, sqlite3, datetime
from collections import defaultdict

__all__ = ["Database"]

class _BaseObject(object): pass

class Database(object):
  def __init__(database, filename = "", debug_sql = False):
    if debug_sql:
      def debug_decorate(f):
        def df(sql, *args):
          print("* ORMithorynque * Debug SQL :", file = sys.stderr)
          print(sql, file = sys.stderr)
          if args: print("  Params:  ", ", ".join(repr(arg) for arg in args[0]), file = sys.stderr)
          rs = f(sql, *args)
          if rs: print("  Returned:", ", ".join(repr(r) for r in rs), file = sys.stderr)
          print(file = sys.stderr)
          return rs
        return df
      database.select_one    = debug_decorate(database.select_one)
      database.select_all    = debug_decorate(database.select_all)
      database.execute       = debug_decorate(database.execute)
      database.executescript = debug_decorate(database.executescript)
      
    class Meta(type):
      def __new__(metaclass, name, superclasses, obj_dict):
        Class = type.__new__(metaclass, name, superclasses, obj_dict)
        if hasattr(database, "Object"): Class.finalize() # Else, the Class being created IS mode.Object
        return Class
      
    class Object(metaclass = Meta):
      def __init__(self, **kargs):
        database.execute(self._sql_create)
        kargs["id"] = id = database.cursor.lastrowid
        self.__dict__.update(self._sql_default_dict)
        self.__dict__.update(kargs)
        
        for sql, sql_attributes in self._sql_insert_at_inits:
          params = (id,) + tuple(sql_attribute.convert_value(self.__dict__[sql_attribute.name]) for sql_attribute in sql_attributes)
          database.execute(sql, params)
        database.commit()
        
        #database.cache[id] = self
        database.cache[id] = database.strong_cache[database.strong_cache_index] = self
        database.strong_cache_index += 1
        if database.strong_cache_index == 256: database.strong_cache_index = 0
        
      def sql_load(self, id):
        for sql, sql_attributes in self._sql_get_at_inits:
          values = database.select_one(sql, (id,))
          if values is None: raise ValueError("No object with id=%s !" % id)
          for sql_attribute, value in zip(sql_attributes, values):
            value = sql_attribute.adapt_value(value)
            self.__dict__[sql_attribute.name] = value
            
      def __repr__(self): return """<%s id=%s %s>""" % (self.__class__.__name__, self.id, " ".join("%s=%s" % (attr, repr(getattr(self, attr))) for attr in self._sql_attributes_indirect))
      
      def __getattr__(self, attr):
        sql_attribute = self._sql_indirect.get(attr)
        if not sql_attribute: raise AttributeError(attr)
        return sql_attribute.get_for(self)
      
      def __setattr__(self, attr, value):
        sql_attribute = self._sql_indirect.get(attr)
        if not sql_attribute: raise AttributeError(attr)
        self.__dict__[attr] = value
        if database.in_transaction: database.dirties.add(self)
        else:
          r = database.execute(sql_attribute.sql_update, (sql_attribute.convert_value(value), self.id))
          database.connexion.commit()
          
      def sql_invalidate(self):
        for name in self._sql_attributes_indirect: del self.__dict__[name]
        
      def sql_update(self):
        changed = False
        for table, sql_attributes in self._sql_insert_at_inits:
          sql_attributes = [sql_attribute for sql_attribute in sql_attributes if sql_attribute.name in self.__dict__]
          if sql_attributes:
            sets   = ", ".join("%s = ?" % sql_attribute.name for sql_attribute in sql_attributes)
            params = tuple(sql_attribute.convert_value(self.__dict__[sql_attribute.name]) for sql_attribute in sql_attributes) + (self.id,)
            database.execute("update %s set %s where id = ?" % (self._sql_table, sets), params)
            changed = True
        if changed and not database.in_transaction: database.connexion.commit()
        
      def sql_destroy(self):
        r = database.execute(self._sql_delete, (self.id,))
        
        
      @classmethod
      def finalize(self):
        if not "_sql_table" in self.__dict__: self._sql_table = self.__name__
        database.classes[self.__name__] = self
        
        self._sql_attributes = {}
        self._sql_relations  = {}
        for attr, sql_attribute in list(self.__dict__.items()):
          if   isinstance(sql_attribute, database.SQLAttribute):
            sql_attribute.finalize(self, attr)
            self._sql_attributes[sql_attribute.name] = sql_attribute
            delattr(self, attr)
          elif isinstance(sql_attribute, SQLRelation):
            sql_attribute.finalize(self, attr)
            self._sql_relations[sql_attribute.name] = sql_attribute
            delattr(self, attr)
            
        self._sql_attributes_indirect = {}
        self._sql_relations_indirect  = {}
        for ParentClass in self.__bases__:
          if issubclass(ParentClass, database.Object) and not (ParentClass is database.Object):
            self._sql_attributes_indirect.update(ParentClass._sql_attributes_indirect)
            self._sql_relations_indirect .update(ParentClass._sql_relations_indirect)
        self._sql_attributes_indirect.update(self._sql_attributes)
        self._sql_relations_indirect .update(self._sql_relations)
        self._sql_indirect = dict(self._sql_attributes_indirect)
        self._sql_indirect.update(self._sql_relations_indirect)
        
        get_at_inits = defaultdict(list)
        for sql_attribute in self._sql_attributes_indirect.values():
          if sql_attribute.get_at_init: get_at_inits[sql_attribute.sql_table].append(sql_attribute)
          
        self._sql_get_at_inits = []
        for sql_table, sql_attributes in get_at_inits.items():
          sql = "select %s from %s where id = ?" % (", ".join(sql_attribute.name for sql_attribute in sql_attributes), sql_table)
          self._sql_get_at_inits.append((sql, sql_attributes))
          
        self._sql_default_dict = {}
        for sql_attribute in self._sql_attributes_indirect.values():
          self._sql_default_dict[sql_attribute.name] = sql_attribute.default
          
        insert_at_inits = defaultdict(list)
        for sql_attribute in self._sql_attributes_indirect.values():
          insert_at_inits[sql_attribute.sql_table].append(sql_attribute)
          
        if self._sql_attributes:
          attrs = database.check_existing_table(self._sql_table)
          if attrs: self._sql_attributes_order = [self._sql_attributes[attr] for attr in attrs]
          else:     self._sql_attributes_order = []
          if attrs is None: # New table
            database.executescript(self.sql_schema()) # self.sql_schema() updates self._sql_attributes_order
          else:
            existing_sql_attributes = set(attrs)
            for sql_attribute in self._sql_attributes.values():
              if not sql_attribute.name in existing_sql_attributes: # New sql_attribute
                self._sql_attributes_order.append(sql_attribute)
                database.execute("alter table %s add %s %s" % (self._sql_table, sql_attribute.name, sql_attribute.sql_type()))
                database.execute("update %s set %s = ?" % (self._sql_table, sql_attribute.name), (sql_attribute.convert_value(sql_attribute.default),))
                
        # Create indexes
        for sql_attribute in self._sql_attributes.values(): sql_attribute.finalize2()
        for sql_relation  in self._sql_relations .values(): sql_relation .finalize2()
          
        self._sql_insert_at_inits = []
        for sql_table, sql_attributes in insert_at_inits.items():
          Class = database.classes[sql_table]
          sql_attributes = [sql_attribute for sql_attribute in Class._sql_attributes_order if sql_attribute in sql_attributes]
          sql = "insert into %s values (?%s)" % (sql_table, "".join(", ?" for sql_attribute in sql_attributes))
          self._sql_insert_at_inits.append((sql, sql_attributes))
          
        self._sql_create = """insert into Object values (null, "%s")""" % self._sql_table
        self._sql_delete = """delete from %s where id = ?""" % self._sql_table
        
        database.connexion.commit()
        
      @classmethod
      def sql_schema(self):
        self._sql_attributes_order = list(self._sql_attributes.values())
        sql  = "create table %s (\n  id integer primary key autoincrement,\n" % self._sql_table
        sql += ",\n".join(sql_attribute.sql_schema() for sql_attribute in self._sql_attributes_order)
        sql += "\n);\n"
        return sql
      
    database.Object = Object
    
    class SQLAttribute(object):
      #def __init__(self, type_or_default, indexed = False, full_text_indexed = False, get_at_init = None):
      def __init__(self, type_or_default, indexed = False, get_at_init = None):
        if   type_or_default is str:               self.type = str;               self.default = ""
        elif type_or_default is object:            self.type = object;            self.default = None
        elif type_or_default is int:               self.type = int;               self.default = 0
        elif type_or_default is float:             self.type = float;             self.default = 0.0
        elif type_or_default is bytes:             self.type = bytes;             self.default = b""
        elif type_or_default is datetime.date:     self.type = datetime.date;     self.default = None
        elif type_or_default is datetime.datetime: self.type = datetime.datetime; self.default = None
        
        elif isinstance(type_or_default, str):               self.type = str;    self.default = type_or_default
        elif isinstance(type_or_default, database.Object):      self.type = object; self.default = type_or_default
        elif isinstance(type_or_default, int):               self.type = int;    self.default = type_or_default
        elif isinstance(type_or_default, float):             self.type = float;  self.default = type_or_default
        elif isinstance(type_or_default, bytes):             self.type = bytes;  self.default = type_or_default
        elif isinstance(type_or_default, datetime.date):     self.type = datetime.date;     self.default = type_or_default
        elif isinstance(type_or_default, datetime.datetime): self.type = datetime.datetime; self.default = type_or_default
        
        else: raise ValueError(type_or_default)
        
        if self.type is object: self.__class__ = SQLObjectAttribute
        
        self.sql_table         = ""
        self.name              = ""
        self.indexed           = indexed
        #self.full_text_indexed = full_text_indexed
        if get_at_init is None: get_at_init = not self.type is object
        self.get_at_init = get_at_init
        
      def __repr__(self): return "SQLAttribute(type = %s, sql_table = %s, name = %s)" % (self.type, self.sql_table, self.name)
      
      def sql_type(self):
        if   self.type is str:               return "text"
        elif self.type is int:               return "integer"
        elif self.type is float:             return "real"
        elif self.type is object:            return "integer"
        elif self.type is bytes:             return "blob"
        elif self.type is datetime.date:     return "date"
        elif self.type is datetime.datetime: return "timestamp"
        raise ValueError
      
      def finalize(self, Class, attr):
        if not self.sql_table: self.sql_table = Class.__name__
        if not self.name:      self.name      = attr
        self.sql_select = "select %s from %s where id = ?" % (self.name, self.sql_table)
        self.sql_update = "update  %s set %s = ? where id = ?" % (self.sql_table, self.name)
        
      def finalize2(self):
        if self.indexed: create_index(self.sql_table, self.name)
        #if self.full_text_indexed and not database.check_existing_index(index_name):
        
      def sql_schema(self): return "  %s %s" % (self.name, self.sql_type())
      
      def convert_value(self, value): return value
      def adapt_value  (self, value): return value
      
      def get_for(self, obj):
        r = database.select_one(self.sql_select, (obj.id,))[0]
        obj.__dict__[self.name] = r
        return r
      
    def create_index(table, col):
      index_name = "%s_%s_index" % (table, col)
      if not database.check_existing_index(index_name):
        sql = "create index %s on %s(%s)" % (index_name, table, col)
        database.executescript(sql)
        
    database.SQLAttribute = SQLAttribute
    
    class SQLObjectAttribute(SQLAttribute):
      def convert_value(self, value): return (value and value.id) or 0
      def adapt_value  (self, value): return database[value]
      
      def get_for(self, obj):
        r = database[database.select_one(self.sql_select, (obj.id,))[0]]
        obj.__dict__[self.name] = r
        return r
      
    
    class SQLRelation(object):
      def finalize2(self): pass
      
    class SQLOneTo(SQLRelation):
      def __init__(self, sql_table, reverse_name, name = ""):
        self.sql_table    = sql_table
        self.reverse_name = reverse_name
        self.name         = name
        
      def __repr__(self): return "%s(sql_table = %s, reverse_name = %s, name = %s)" % (self.__class__.__name__, self.sql_table, self.reverse_name, self.name)
      
      def finalize(self, Class, attr):
        if not self.name: self.name = attr
        self.sql_select = "select id from %s where %s = ?" % (self.sql_table, self.reverse_name)
        
    class SQLOneToOne(SQLOneTo):
      def get_for(self, obj):
        r = database.select_one(self.sql_select, (obj.id,))
        if not r: return None
        return database[r[0]]
      
    database.SQLOneToOne = SQLOneToOne
    
    class SQLOneToMany(SQLOneTo):
      def get_for(self, obj):
        r = database.select_all(self.sql_select, (obj.id,))
        return [database[i[0]] for i in r]
      
      def finalize2(self):
        create_index(self.sql_table, self.reverse_name)
        
    database.SQLOneToMany = SQLOneToMany
    
    
    class SQLManyToMany(SQLRelation):
      def __init__(self, direct_name, reverse_name, sql_table = "", name = ""):
        self.name         = name
        self.reverse_name = reverse_name
        self.direct_name  = direct_name
        self.sql_table    = sql_table
        
      def __repr__(self): return "SQLManyToMany(direct_name = %s, reverse_name = %s, sql_table = %s)" % (self.direct_name, self.reverse_name, self.sql_table)
      
      def finalize(self, Class, attr):
        if not self.name:       self.name       = attr
        if not self.sql_table:  self.sql_table  = "relation_%s_%s" % tuple(sorted([self.direct_name, self.reverse_name]))
        self.sql_select = "select %s from %s where %s = ?" % (self.direct_name, self.sql_table, self.reverse_name)
        self.sql_insert = "insert into %s values (?, ?)" % self.sql_table
        self.sql_delete = "delete from %s where %s = ? and %s = ?" % (self.sql_table, self.reverse_name, self.direct_name)
        
        if self.direct_name < self.reverse_name:
          def add_func(obj, value):
            database.execute(self.sql_insert, (value.id, obj.id))
            database.commit()
        else:
          def add_func(obj, value):
            database.execute(self.sql_insert, (obj.id, value.id))
            database.commit()
          
        def remove_func(obj, value):
          database.execute(self.sql_delete, (obj.id, value.id))
          database.commit()
          
        setattr(Class, "add_%s"    % self.direct_name, add_func)
        setattr(Class, "remove_%s" % self.direct_name, remove_func)
        
        if not database.check_existing_index("%s_index" % self.sql_table):
          database.executescript(self.sql_schema())
          
      def sql_schema(self):
        attrs = list(sorted([self.direct_name, self.reverse_name]))
        sql  = "create table %s (\n" % self.sql_table
        sql += "  %s integer,\n" % attrs[0]
        sql += "  %s integer\n" % attrs[1]
        sql += ");\n"
        sql += "create index %s_index on %s(%s, %s);\n" % (self.sql_table, self.sql_table, attrs[0], attrs[1])
        return sql
      
      def get_for(self, obj):
        r = database.select_all(self.sql_select, (obj.id,))
        return [database[i[0]] for i in r]
      
    database.SQLManyToMany = SQLManyToMany
    
    class TransactionContextManager(object):
      def __enter__(self): database.begin_transaction()
      
      def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type: database.rollback()
        else:        database.end_transaction()
        
    database.classes        = {}
    database.in_transaction = False
    database.dirties        = set()
    database.transaction    = TransactionContextManager()
    database.clear_cache()
    if filename: database.connect(filename)
    
    
  def connect(self, filename):
    self.filename  = filename
    self.connexion = sqlite3.connect(filename, detect_types = sqlite3.PARSE_DECLTYPES)
    self.cursor    = self.connexion.cursor()
    
    if not self.check_existing_table("Object"):
      self.executescript("""
create table Object(
  id integer primary key,
  classname text
);
""")
      
      
  def begin_transaction(self):
    if self.in_transaction: raise ValueError("Already in a transaction!")
    self.in_transaction = True
    
  def rollback(self):
    if not self.in_transaction: raise ValueError("Not in a transaction!")
    self.in_transaction = False
    for dirty in self.dirties: dirty.sql_invalidate()
    self.dirties.clear()
    self.connexion.rollback()
    
  def end_transaction(self):
    if not self.in_transaction: raise ValueError("Not in a transaction!")
    self.in_transaction = False
    for dirty in self.dirties: dirty.sql_update()
    self.dirties.clear()
    self.connexion.commit()
    
  def commit(self):
    if not self.in_transaction: self.connexion.commit()
      
  def close(self):
    self.connexion.close()
    self.connexion = None
    self.cursor    = None
    
  def check_existing_table(self, sql_table):
    r = self.select_one("""select sql from sqlite_master where type = "table" and name = ?""", (sql_table,))
    if not r: return None
    sql = r[0]
    sql = sql.split("(", 1)[1].split(")", 1)[0]
    lines = sql.split(",")[1:] # [0] is id
    return [line.split(None, 1)[0].strip() for line in lines]
  
  def check_existing_index(self, sql_index):
    r = self.select_one("""select name from sqlite_master where type = "index" and name = ?""", (sql_index,))
    if r: return True
    return None
  
  def select_one(self, sql, params = ()):
    self.cursor.execute(sql, params)
    return self.cursor.fetchone()
  
  def select_object_one(self, sql, params = ()):
    self.cursor.execute(sql, params)
    r = self.cursor.fetchone()
    if not r: return None
    return self[r[0]]
  
  def select_all(self, sql, params = ()):
    self.cursor.execute(sql, params)
    return self.cursor.fetchall()
  
  def select_object_all(self, sql, params = ()):
    self.cursor.execute(sql, params)
    return [ self[r[0]] for r in self.cursor.fetchall() ]
  
  def execute(self, sql, params = ()):
    self.cursor.execute(sql, params)
    
  def executescript(self, sql):
    self.cursor.executescript(sql)
    
  def get(self, id):
    try: return self[id]
    except ValueError: return None
    except KeyError:   return None
    
  def __getitem__(self, id):
    if id == 0: return None
    obj = self.cache.get(id)
    if obj: return obj
    
    classname = self.select_one("select classname from Object where id = ?", (id,))
    if not classname: raise ValueError("No object with id=%s!" % id)
    
    obj = _BaseObject()
    obj.id = id
    obj.__class__ = self.classes[classname[0]]
    obj.sql_load(id)
    
    self.cache[id] = self.strong_cache[self.strong_cache_index] = obj
    self.strong_cache_index += 1
    if self.strong_cache_index == 256: self.strong_cache_index = 0
    return obj
  
  def clear_cache(self):
    self.cache = weakref.WeakValueDictionary()
    self.strong_cache = [None] * 256
    self.strong_cache_index = 0
    

