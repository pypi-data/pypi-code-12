"""
plumbium.recorders.sqldatabase
******************************
"""

try:
    from sqlalchemy import create_engine, text
except:
    pass


class SQLDatabase(object):
    """Records results to a database supported by SQLAlchemy

    :param uri: database server URI e.g. ``mysql://username:password@localhost/dbname``
    :type uri: str
    :param table: table name
    :type collection: str
    :param values: a mapping from database table columns to values
    :type values: dict

    .. seealso:: `SQLAlchemy documentation
        <http://docs.sqlalchemy.org/en/latest/core/connections.html>`_
    """

    def __init__(self, uri, table, values):
        self.uri = uri
        self.table = table
        self.values = values

    def write(self, results):
        """Write the results to the database table specified at initialisation.

        :param results: A dictionary of results to record
        :type results: dict
        """

        engine = create_engine(self.uri)
        field_names = ','.join(self.values.keys())
        values_placeholder = ','.join([':{0}'.format(k) for k in self.values.keys()])
        query_string = """
            INSERT INTO {table}
            ({field_names})
            VALUES ({values_placeholder})
        """
        query = text(query_string.format(
            table=self.table,
            field_names=field_names,
            values_placeholder=values_placeholder
        ))
        row = {}
        for field in self.values:
            row[field] = self.values[field](results)
        engine.execute(query, **row)
