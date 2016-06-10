from py4jdbc.exceptions import dbapi2


exc_classes = {}


class _SqlstateMeta(dbapi2.CodeAggregatorMeta):
    exc_classes = exc_classes


class Warning(dbapi2.Warning, metaclass=_SqlstateMeta):
    code = '01'

class NoData(dbapi2.Warning, metaclass=_SqlstateMeta):
    code = '02'

class SqlStatementNotYetComplete(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '03'

class ConnectionError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '08'

class TriggeredActionError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '09'

class FeatureNotSupported(dbapi2.NotSupportedError, metaclass=_SqlstateMeta):
    code = '0A'

class InvalidTransactionInitiation(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '0B'

class LocatorError(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '0F'

class InvalidGrantor(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '0L'

class InvalidRoleSpecification(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '0P'

class DiagnosticsError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '0Z'

class CaseNotFound(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '20'

class CardinalityViolation(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '21'

class DataError(dbapi2.DataError, metaclass=_SqlstateMeta):
    code = '22'

class IntegrityConstraintViolation(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '23'

class InvalidCursorState(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '24'

class InvalidTransactionState(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '25'

class InvalidSQLStatementName(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '26'

class TriggeredDataChangeViolation(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '27'

class InvalidAuthorizationSpecification(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '28'

class DependentPrivilegeDescriptorsStillExist(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '2B'

class InvalidTransactionTermination(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '2D'

class SqlRoutineError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '2F'

class InvalidCursorName(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '34'

class ExternalRoutineError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '38'

class ExternalRoutineInvocationError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '39'

class SavepointError(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '3B'

class InvalidCatalogName(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '3D'

class InvalidSchemaName(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '3F'

class TransactionRollback(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '40'

class SyntaxOrAccessRuleViolationError(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '42'

class WithCheckOptionViolation(dbapi2.ProgrammingError, metaclass=_SqlstateMeta):
    code = '44'

class InsufficientResources(dbapi2.OperationalError, metaclass=_SqlstateMeta):
    code = '53'

class ProgramLimitExceeded(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '54'

class ObjectNotInPrerequisiteState(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '55'

class OperatorIntervention(dbapi2.DatabaseError, metaclass=_SqlstateMeta):
    code = '57'

class SystemError(dbapi2.OperationalError, metaclass=_SqlstateMeta):
    code = '58'