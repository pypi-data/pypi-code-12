

from flask_magic.exceptions import HTTPException

class ContactPageMissingEmailToError(HTTPException):
    code = 500
    description = "ContactPage missing email_to value"
