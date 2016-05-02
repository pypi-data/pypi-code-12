SHEBANG_ACTION = \
"""
Make the first non-empty line of your mapper '#!/usr/bin/python' (without the single quotes)
"""

SHEBANG_DETAILS = \
"""
The first non-empty line of every mapper should be  '#!/usr/bin/python'. This line is \
called the shebang line and instructs the local environment on a data node to use Python \
as the execution language. Without this line, Hadoop is unable to execute the mapper.\

Please review example mappers on how to write a shebang line.
"""

COLUMN_TYPE_ACTION = \
"""
Ensure that all columns in schema are of allowed types
"""

COLUMN_TYPE_DETAILS = \
"""
For maximum ingestion robustness and to ensure minimal data loss, Thrive recommends that \
columns be limited to allowed types.

Allowed types: INT, FLOAT, BIGINT, TIMESTAMP, VARCHAR(<65000), BOOLEAN.
"""

COLUMN_COUNT_ACTION = \
"""
Ensure that all output rows have identical number of columns (fields) as specified in the \
schema
"""

COLUMN_COUNT_DETAILS = \
"""
Relational databases like Vertica are strict about requiring identical number columns \
in all input rows. Further, this number should equal the number of columns specified in \
the 'columns.csv'. Rows that violate this condition will be rejected by Vertica.
"""

COLUMN_VALUE_ACTION = \
"""
Ensure that each column of every output row has a type consistent with the schema
"""

COLUMN_VALUE_DETAILS = \
"""
Relational databases like Vertica are strict about requiring conformance with schema. \
Fields in every row must have the same type as specified in schema. For example if a float \
is sent when an integer is expected will result in the whole row being rejected.
"""




