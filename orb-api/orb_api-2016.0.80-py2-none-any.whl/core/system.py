""" Defines an overall management class for all databases and schemas. """

import logging

from projex.lazymodule import lazy_import
from ..settings import Settings

log = logging.getLogger(__name__)
orb = lazy_import('orb')
pytz = lazy_import('pytz')

from .security import Security


class System(object):
    def __init__(self):
        self.__current_db = None
        self.__databases = {}
        self.__schemas = {}
        self.__settings = Settings()
        self.__syntax = None
        self.__security = Security(self.__settings.security_key)

    def activate(self, db):
        """
        Sets the currently active database instance.

        :param db:  <orb.Database> || None
        """
        self.__current_db = db

    def database(self, code=''):
        """
        Returns the database for this manager based on the inputted name. \
        If no name is supplied, then the currently active database is \
        returned.
        
        :usage      |>>> import orb
                    |>>> orb.system.database() # returns active database
                    |>>> orb.system.database('User') # returns the User db
                    |>>> orb.system.database('User', 'Debug') # from Debug
        
        :param      name | <str> || None

        :return     <orb.database.Database> || None
        """
        return self.__databases.get(code) or self.__current_db

    def databases(self):
        """
        Returns the databases for this system.
        
        :return     {<str> name: <orb.Database>, ..}
        """
        return self.__databases

    def init(self, scope):
        """
        Loads the models from the orb system into the inputted scope.
        
        :param      scope        | <dict>
                    autoGenerate | <bool>
                    schemas      | [<orb.TableSchema>, ..] || None
                    database     | <str> || None
        """
        schemas = self.schemas().values()
        for schema in schemas:
            scope[schema.name()] = schema.model()

    def register(self, obj):
        """
        Registers a particular database.
        
        :param      obj     | <orb.Database> || <orb.Schema>
        """
        if isinstance(obj, orb.Database):
            self.__databases[obj.code()] = obj
        elif isinstance(obj, orb.Schema):
            self.__schemas[obj.name()] = obj

    def model(self, code, autoGenerate=True):
        return self.models(autoGenerate=autoGenerate).get(code)

    def models(self, base=None, database='', autoGenerate=True):
        output = {}
        for schema in self.__schemas.values():
            model = schema.model(autoGenerate=autoGenerate)
            if (model and
                (base is None or issubclass(model, base)) and
                (not database or not model.schema().database() or database == model.schema().database())):
                output[schema.name()] = model
        return output

    def schema(self, code):
        """
        Looks up the registered schemas for the inputted schema name.
        
        :param      name     | <str>
                    database | <str> || None
        
        :return     <orb.tableschema.TableSchema> || None
        """
        return self.__schemas.get(code)

    def schemas(self):
        """
        Returns a list of all the schemas for this instance.
        
        :return     {<str> code: <orb.Schema>, ..}
        """
        return self.__schemas

    def settings(self):
        """
        Returns the settings instance associated with this manager.
        
        :return     <orb.Settings>
        """
        return self.__settings

    def security(self):
        return self.__security

    def setSecurity(self, security):
        self.__security = security

    def setSyntax(self, syntax):
        if not isinstance(syntax, orb.Syntax):
            syntax = orb.Syntax.byName(syntax)
            if syntax:
                self.__syntax = syntax()
        else:
            self.__syntax = syntax

    def syntax(self):
        """
        Returns the syntax that is being used for this system.

        :return:    <orb.Syntax>
        """
        if self.__syntax is None:
            self.__syntax = orb.Syntax.byName(self.__settings.syntax)()
        return self.__syntax
