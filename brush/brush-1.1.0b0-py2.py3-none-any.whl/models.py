from datetime import datetime
import logging
from tornado.options import options
from sqlalchemy import (
    MetaData, Table, Column, Numeric, Integer, Boolean, DateTime, select)

logger = logging.getLogger('brush')
_indexable = ['.status', 'plo.ok']

# Global access to the table schema
brush = None


def initialize(comb, engine):
    """Initialize and create a new table if it does not already exist.

    Parameters
    ----------
    comb : :class:`brush.comb.FrequencyComb`
    engine
        SQLAlchemy engine

    """
    global brush
    metadata = MetaData()

    sql_dtypes = {
        'double': Numeric(asdecimal=False),
        'int': Integer,
        'bool': Boolean
    }

    col_names = sorted(comb.metadata.keys())
    columns = [Column(col.replace('.', '_'),
               sql_dtypes[comb.metadata[col]['type']],
               index=(any(k in col for k in _indexable) or col == 'system.locked'),
               nullable=True)
               for col in col_names if 'timestamp' not in col]

    # Ensure that SQLAlchemy returns a Python float for serialization
    for col in columns:
        if isinstance(col.type, Numeric):
            col.type.asdecimal = False

    data = Table(options.sql_table, metadata,
                 Column('id', Integer, primary_key=True),
                 Column('timestamp', DateTime, index=True, unique=True),
                 *columns)

    metadata.create_all(engine)
    brush = data
    return data


def select_timeseries(table, start, stop=None, keys=None):
    """Select timeseries data from the database.

    Parameters
    ----------
    table : SQLAlchemy.Table
        Table to query
    start : datetime.datetime
        UTC timestamp indicating the start time
    stop : datetime.datetime
        UTC timestamp indicating the end time
    keys : list
        List of keys to get. If ``None``, return all.

    Returns
    -------
    sel
        The SQLAlchemy selectable

    """
    if stop is None:
        stop = datetime.utcnow()

    if keys is None:
        columns = [table]
    else:
        columns = [Column(key) for key in keys]

    sel = select(columns)\
        .where(table.c.timestamp >= start)\
        .where(table.c.timestamp <= stop)
    return sel
