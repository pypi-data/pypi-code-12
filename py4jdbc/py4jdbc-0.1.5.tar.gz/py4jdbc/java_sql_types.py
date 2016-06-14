
java_sql_types = [
    ('ARRAY', 2003),
    ('BIGINT', -5),
    ('BINARY', -2),
    ('BIT', -7),
    ('BLOB', 2004),
    ('BOOLEAN', 16),
    ('CHAR', 1),
    ('CLOB', 2005),
    ('DATALINK', 70),
    ('DATE', 91),
    ('DECIMAL', 3),
    ('DISTINCT', 2001),
    ('DOUBLE', 8),
    ('FLOAT', 6),
    ('INTEGER', 4),
    ('JAVA_OBJECT', 2000),
    ('LONGNVARCHAR', -16),
    ('LONGVARBINARY', -4),
    ('LONGVARCHAR', -1),
    ('NCHAR', -15),
    ('NCLOB', 2011),
    ('NULL', 0),
    ('NUMERIC', 2),
    ('NVARCHAR', -9),
    ('OTHER', 1111),
    ('REAL', 7),
    ('REF', 2006),
    ('ROWID', -8),
    ('SMALLINT', 5),
    ('SQLXML', 2009),
    ('STRUCT', 2002),
    ('TIME', 92),
    ('TIMESTAMP', 93),
    ('TINYINT', -6),
    ('VARBINARY', -3),
    ('VARCHAR', 12),
]

from enum import Enum


class Connection(Enum):
    '''Constants for module java.sql.Connection.
    '''
    module = "java.sql.Connection"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Connection.html#TRANSACTION_NONE
    # modifiers: public static final int
    TRANSACTION_NONE = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Connection.html#TRANSACTION_READ_COMMITTED
    # modifiers: public static final int
    TRANSACTION_READ_COMMITTED = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Connection.html#TRANSACTION_READ_UNCOMMITTED
    # modifiers: public static final int
    TRANSACTION_READ_UNCOMMITTED = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Connection.html#TRANSACTION_REPEATABLE_READ
    # modifiers: public static final int
    TRANSACTION_REPEATABLE_READ = 4

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Connection.html#TRANSACTION_SERIALIZABLE
    # modifiers: public static final int
    TRANSACTION_SERIALIZABLE = 8


class Databasemetadata(Enum):
    '''Constants for module java.sql.DatabaseMetaData.
    '''
    module = "java.sql.DatabaseMetaData"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#attributeNoNulls
    # modifiers: public static final short
    attributeNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#attributeNullable
    # modifiers: public static final short
    attributeNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#attributeNullableUnknown
    # modifiers: public static final short
    attributeNullableUnknown = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowNotPseudo
    # modifiers: public static final int
    bestRowNotPseudo = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowPseudo
    # modifiers: public static final int
    bestRowPseudo = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowSession
    # modifiers: public static final int
    bestRowSession = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowTemporary
    # modifiers: public static final int
    bestRowTemporary = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowTransaction
    # modifiers: public static final int
    bestRowTransaction = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#bestRowUnknown
    # modifiers: public static final int
    bestRowUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#columnNoNulls
    # modifiers: public static final int
    columnNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#columnNullable
    # modifiers: public static final int
    columnNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#columnNullableUnknown
    # modifiers: public static final int
    columnNullableUnknown = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionColumnIn
    # modifiers: public static final int
    functionColumnIn = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionColumnInOut
    # modifiers: public static final int
    functionColumnInOut = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionColumnOut
    # modifiers: public static final int
    functionColumnOut = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionColumnResult
    # modifiers: public static final int
    functionColumnResult = 5

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionColumnUnknown
    # modifiers: public static final int
    functionColumnUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionNoNulls
    # modifiers: public static final int
    functionNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionNoTable
    # modifiers: public static final int
    functionNoTable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionNullable
    # modifiers: public static final int
    functionNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionNullableUnknown
    # modifiers: public static final int
    functionNullableUnknown = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionResultUnknown
    # modifiers: public static final int
    functionResultUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionReturn
    # modifiers: public static final int
    functionReturn = 4

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#functionReturnsTable
    # modifiers: public static final int
    functionReturnsTable = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyCascade
    # modifiers: public static final int
    importedKeyCascade = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyInitiallyDeferred
    # modifiers: public static final int
    importedKeyInitiallyDeferred = 5

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyInitiallyImmediate
    # modifiers: public static final int
    importedKeyInitiallyImmediate = 6

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyNoAction
    # modifiers: public static final int
    importedKeyNoAction = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyNotDeferrable
    # modifiers: public static final int
    importedKeyNotDeferrable = 7

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeyRestrict
    # modifiers: public static final int
    importedKeyRestrict = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeySetDefault
    # modifiers: public static final int
    importedKeySetDefault = 4

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#importedKeySetNull
    # modifiers: public static final int
    importedKeySetNull = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnIn
    # modifiers: public static final int
    procedureColumnIn = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnInOut
    # modifiers: public static final int
    procedureColumnInOut = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnOut
    # modifiers: public static final int
    procedureColumnOut = 4

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnResult
    # modifiers: public static final int
    procedureColumnResult = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnReturn
    # modifiers: public static final int
    procedureColumnReturn = 5

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureColumnUnknown
    # modifiers: public static final int
    procedureColumnUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureNoNulls
    # modifiers: public static final int
    procedureNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureNoResult
    # modifiers: public static final int
    procedureNoResult = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureNullable
    # modifiers: public static final int
    procedureNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureNullableUnknown
    # modifiers: public static final int
    procedureNullableUnknown = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureResultUnknown
    # modifiers: public static final int
    procedureResultUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#procedureReturnsResult
    # modifiers: public static final int
    procedureReturnsResult = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#sqlStateSQL
    # modifiers: public static final int
    sqlStateSQL = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#sqlStateSQL99
    # modifiers: public static final int
    sqlStateSQL99 = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#sqlStateXOpen
    # modifiers: public static final int
    sqlStateXOpen = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#tableIndexClustered
    # modifiers: public static final short
    tableIndexClustered = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#tableIndexHashed
    # modifiers: public static final short
    tableIndexHashed = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#tableIndexOther
    # modifiers: public static final short
    tableIndexOther = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#tableIndexStatistic
    # modifiers: public static final short
    tableIndexStatistic = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typeNoNulls
    # modifiers: public static final int
    typeNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typeNullable
    # modifiers: public static final int
    typeNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typeNullableUnknown
    # modifiers: public static final int
    typeNullableUnknown = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typePredBasic
    # modifiers: public static final int
    typePredBasic = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typePredChar
    # modifiers: public static final int
    typePredChar = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typePredNone
    # modifiers: public static final int
    typePredNone = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#typeSearchable
    # modifiers: public static final int
    typeSearchable = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#versionColumnNotPseudo
    # modifiers: public static final int
    versionColumnNotPseudo = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#versionColumnPseudo
    # modifiers: public static final int
    versionColumnPseudo = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html#versionColumnUnknown
    # modifiers: public static final int
    versionColumnUnknown = 0


class Parametermetadata(Enum):
    '''Constants for module java.sql.ParameterMetaData.
    '''
    module = "java.sql.ParameterMetaData"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterModeIn
    # modifiers: public static final int
    parameterModeIn = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterModeInOut
    # modifiers: public static final int
    parameterModeInOut = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterModeOut
    # modifiers: public static final int
    parameterModeOut = 4

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterModeUnknown
    # modifiers: public static final int
    parameterModeUnknown = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterNoNulls
    # modifiers: public static final int
    parameterNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterNullable
    # modifiers: public static final int
    parameterNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ParameterMetaData.html#parameterNullableUnknown
    # modifiers: public static final int
    parameterNullableUnknown = 2


class Resultset(Enum):
    '''Constants for module java.sql.ResultSet.
    '''
    module = "java.sql.ResultSet"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#CLOSE_CURSORS_AT_COMMIT
    # modifiers: public static final int
    CLOSE_CURSORS_AT_COMMIT = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#CONCUR_READ_ONLY
    # modifiers: public static final int
    CONCUR_READ_ONLY = 1007

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#CONCUR_UPDATABLE
    # modifiers: public static final int
    CONCUR_UPDATABLE = 1008

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#FETCH_FORWARD
    # modifiers: public static final int
    FETCH_FORWARD = 1000

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#FETCH_REVERSE
    # modifiers: public static final int
    FETCH_REVERSE = 1001

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#FETCH_UNKNOWN
    # modifiers: public static final int
    FETCH_UNKNOWN = 1002

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#HOLD_CURSORS_OVER_COMMIT
    # modifiers: public static final int
    HOLD_CURSORS_OVER_COMMIT = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#TYPE_FORWARD_ONLY
    # modifiers: public static final int
    TYPE_FORWARD_ONLY = 1003

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#TYPE_SCROLL_INSENSITIVE
    # modifiers: public static final int
    TYPE_SCROLL_INSENSITIVE = 1004

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSet.html#TYPE_SCROLL_SENSITIVE
    # modifiers: public static final int
    TYPE_SCROLL_SENSITIVE = 1005


class Resultsetmetadata(Enum):
    '''Constants for module java.sql.ResultSetMetaData.
    '''
    module = "java.sql.ResultSetMetaData"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#columnNoNulls
    # modifiers: public static final int
    columnNoNulls = 0

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#columnNullable
    # modifiers: public static final int
    columnNullable = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#columnNullableUnknown
    # modifiers: public static final int
    columnNullableUnknown = 2


class Statement(Enum):
    '''Constants for module java.sql.Statement.
    '''
    module = "java.sql.Statement"

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#CLOSE_ALL_RESULTS
    # modifiers: public static final int
    CLOSE_ALL_RESULTS = 3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#CLOSE_CURRENT_RESULT
    # modifiers: public static final int
    CLOSE_CURRENT_RESULT = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#EXECUTE_FAILED
    # modifiers: public static final int
    EXECUTE_FAILED = -3

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#KEEP_CURRENT_RESULT
    # modifiers: public static final int
    KEEP_CURRENT_RESULT = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#NO_GENERATED_KEYS
    # modifiers: public static final int
    NO_GENERATED_KEYS = 2

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#RETURN_GENERATED_KEYS
    # modifiers: public static final int
    RETURN_GENERATED_KEYS = 1

    # https://docs.oracle.com/javase/7/docs/api/java/sql/Statement.html#SUCCESS_NO_INFO
    # modifiers: public static final int
    SUCCESS_NO_INFO = -2
