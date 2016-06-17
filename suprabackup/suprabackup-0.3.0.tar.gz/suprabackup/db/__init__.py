"""
This module handles database connections for suprabackup

"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# This is used just for proxying models to db.models.<something>
from .. import models
from ..models.base import Model


Session = sessionmaker()


def get_engine(engine, host, db, user, password=''):
    """
    Get the engine corresponding to the given parameters

    """
    user_string = "{}:{}".format(user, password)
    return create_engine('{}://{}@{}/{}'.format(engine, user_string, host, db))


def connect_engine(engine):
    """
    Get a session from an engine

    """
    return Session(bind=engine)


def connect(engine, host, db, user, password=''):
    """
    Connects to the database using the ORM and returns a db session

    """
    return connect_engine(get_engine(engine, host, db, user, password))


def connect_with_config(config, logger=None):
    """
    Connects to the database specified in configuration file and returns a session
    This will log to the given logger instance

    """
    try:
        session = connect(engine=config['database']['engine'],
                          host=config['database']['host'],
                          db=config['database']['db'],
                          user=config['database']['user'],
                          password=config['database'].get('password', ''),
                         )
        if logger:
            logger.debug("Successfully connected to database {}"
                         .format(config['database']['db']))
        return session
    except KeyError as e:
        if logger:
            logger.error("Cannot connect to database: {0} not defined"
                         .format(e))
    except Exception as e:
        if logger:
            logger.error("Cannot connect to database {0} on {1}: {2}"
                         .format(config['database']['name'],
                                 config['database']['host'],
                                 e))
    return None
