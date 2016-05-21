from sqlalchemy.exc import SQLAlchemyError, OperationalError
from werkzeug.exceptions import HTTPException

# Generic Errors
class ApplicationError(Exception): pass
class ModelError(ApplicationError): pass
class UserError(ApplicationError): pass
class ViewError(ApplicationError): pass

#-------------------------------------------------------------------------------
# Abort Specific Error

class MailmanConfigurationError(HTTPException):
    code = 500
    description = "MAIL is not configured properly"

class MailmanUnknownProviderError(HTTPException):
    code = 500
    description = "MAIL is configured with an unknown provider"


class SQLAlchemyError(OperationalError, HTTPException):
    code = 500
    description = "DB Error"

