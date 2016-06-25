from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///apus.db')


def create_table():
    Base.metadata.create_all(engine)


# WRITE
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def save_in_db(obj):
    session.add(obj)
    session.commit()

# READ
def query(model):
    return session.query(model)
