
"""
Look for easy usage example in tag.py moule

thanks to python language flexibility, I can create such modules and classes,
without creating singletones in modules
"""

import sqlalchemy.ext.declarative
import sqlalchemy.orm


class BasicDB:

    def __init__(
            self,
            config_string=None,
            bind=None,
            decl_base=None,
            metadata=None,
            init_table_data=None
            ):

        if bind is None and config_string is None:
            raise ValueError(
                "if `bind' or `config_string' must be defined"
                )

        if bind is not None and config_string is not None:
            raise ValueError(
                "if `bind' is defined, then `config_string' must be None"
                )

        if config_string is not None and bind is None:
            bind = sqlalchemy.create_engine(config_string)

        if decl_base is None:
            self.decl_base = sqlalchemy.ext.declarative.declarative_base(
                metadata=metadata,
                bind=bind
                )
        else:
            self.decl_base = decl_base

        self.init_table_mappings(init_table_data)

        return

    def create_all(self):
        return self.decl_base.metadata.create_all()

    def bind(self, engine):
        self.decl_base.metadata.bind = engine
        return
