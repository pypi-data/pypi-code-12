GET_TABLE_SCHEMA = """
SELECT column_name, data_type
FROM   information_schema.columns
WHERE  table_name = %s;
"""


CREATE_TEST_TABLE = """
CREATE TABLE foo_table (
    id  SERIAL PRIMARY KEY,
    foo TEXT,
    bar TEXT
);
"""

DROP_TEST_TABLE = """
DROP TABLE IF EXISTS foo_table CASCADE;
"""


CREATE_KRIDER_TABLE = """
CREATE TABLE kamen_rider (
    id        SERIAL PRIMARY KEY,
    title     TEXT,
    alter_ego TEXT
);
"""
