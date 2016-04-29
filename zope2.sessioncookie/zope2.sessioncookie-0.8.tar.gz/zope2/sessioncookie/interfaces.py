from zope.interface import Attribute
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Int
from zope.schema import TextLine


class ISignedSessionCookieConfig(Interface):
    """Schema for <sessioncookie> directive.
    """
    secret = TextLine(
        title=u"Secret",
        description=u"Secret used to sign the cookie value",
        required=True,
    )

    salt = TextLine(
        title=u"Salt",
        description=u"Salt used to sign the cookie value",
        required=False,
    )

    cookie_name = TextLine(
        title=u"Cookie Name",
        description=u"Name of the session cookie",
        required=False,
    )

    max_age = Int(
        title=u"Max Age",
        description=u"Max age (in seconds) of the session cookie",
        required=False,
    )

    path = TextLine(
        title=u"Cookie Path",
        description=u"Path of the session cookie",
        required=False,
    )

    domain = TextLine(
        title=u"Cookie Domain",
        description=u"Domain of the session cookie",
        required=False,
    )

    secure = Bool(
        title=u"Secure",
        description=u"Return the session cookie only over HTTPS?",
        required=False,
    )

    http_only = Bool(
        title=u"HTTP Only",
        description=u"Mark the session cookie invisible to Javascript?",
        required=False,
    )

    hash_algorithm = TextLine(
        title=u"Hash Algorithm",
        description=u"Name of algorithm used to sign cookie state",
        default=u"sha512",
        required=False,
    )

    timeout = Int(
        title=u"Timeout",
        description=u"Timeout (in seconds) for the session cookie value",
        required=False,
    )

    reissue_time = Int(
        title=u"Reissue Time",
        description=u"Time (in seconds) for updating cookie value on access",
        required=False,
    )

    encrypt = Bool(
        title=u"Encrypt Cookie",
        description=u"Encrypt cookie text (requires ``pyCrypto``)?",
        required=False,
    )


class ISignedSessionCookieCreated(Interface):
    """ Event interface for newly-created session.

    I.e., no session cookie was present in the browser beforehand.
    """
    session = Attribute("Newly-created session")
