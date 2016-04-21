

from flask_magic.exceptions import HTTPException


class UserLoginDisabledError(HTTPException):
    code = 501
    description = "LOGIN is disabled. Contact admin if this is an error"


class UserSignupDisabledError(HTTPException):
    code = 501
    description = "SIGNUP is disabled. Contact admin if this is an error"


class UserOAuthDisabledError(HTTPException):
    code = 501
    description = "OAuth LOGIN is disabled. Contact admin if this is an error"