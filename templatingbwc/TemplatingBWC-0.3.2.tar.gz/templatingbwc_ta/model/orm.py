from compstack.sqlalchemy.lib.declarative import declarative_base, LookupMixin

Base = declarative_base()

class Make(Base, LookupMixin):
    __tablename__ = 'auto_makes'
