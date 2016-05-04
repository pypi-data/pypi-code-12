"""
Magic

Base Configuration

"""

import os

CWD = os.path.dirname(__file__)


class BaseConfig(object):
    """
    Base Configuration.
    """

# ------------------------------------------------------------------------------
# APPLICATION MISC CONFIG

    #: Required to setup. This email will have SUPER USER role
    APPLICATION_ADMIN_EMAIL = None

    #: Site's name or Name of the application
    APPLICATION_NAME = "Magic"

    #: The application url
    APPLICATION_URL = ""

    #: Version of application
    APPLICATION_VERSION = "0.0.1"

    #: Email address to be contacted, or to receive email at
    APPLICATION_EMAIL = None

    #: The address to receive email when using the contact page
    APPLICATION_CONTACT_EMAIL = None

    #: GOOGLE ANALYTICS ID
    APPLICATION_GOOGLE_ANALYTICS_ID = ""

    #: PAGINATION_PER_PAGE : Total entries to display per page
    APPLICATION_PAGINATION_PER_PAGE = 20

    #: Turn ON/OFF maintenance page
    APPLICATION_MAINTENANCE_ON = False

    #: The application data directory
    APPLICATION_DATA_DIR = os.path.join(CWD, "_data")

    # MAX_CONTENT_LENGTH
    # If set to a value in bytes, Flask will reject incoming requests with a
    # content length greater than this by returning a 413 status code
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

# ------------------------------------------------------------------------------
# CREDENTIALS

    #: AWS Credentials
    # AWS is used by lots of extensions
    # For: S3, SES Mailer, flask S3.

    # The AWS Access KEY
    AWS_ACCESS_KEY_ID = ""

    # Secret Key
    AWS_SECRET_ACCESS_KEY = ""

    # The bucket name for S3
    AWS_S3_BUCKET_NAME = ""

    # The default region name
    AWS_REGION_NAME = "us-east-1"

# ------------------------------------------------------------------------------
# DATABASES

    #: SQL_URI
    #: format: engine://USERNAME:PASSWORD@HOST:PORT/DB_NAME
    SQL_URI = "sqlite:////%s/db.db" % APPLICATION_DATA_DIR

    #: REDIS_URI
    #: format: USERNAME:PASSWORD@HOST:PORT
    REDIS_URI = None

# ------------------------------------------------------------------------------
# ASSETS DELIVERY

    # ASSETS DELIVERY allows to serve static files from S3, Cloudfront or other CDN

    # The delivery method:
    #   - None: will use the local static files
    #   - S3: Will use AWS S3. By default it will use the bucket name set in AWS_S3_BUCKET_NAME
    #       When S3, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required to upload files
    #   - CDN: To use a CDN. ASSETS_DELIVERY_DOMAIN need to have the CDN domain
    ASSETS_DELIVERY_METHOD = None

    # Set the base domain of the CDN
    ASSETS_DELIVERY_DOMAIN = None


# ------------------------------------------------------------------------------
# SESSION

    #: SESSION
    #: Flask-KVSession is used to save the user's session
    #: Set the SESSION_URI by using these examples below to set KVSession
    #: To use local session, just set SESSION_URI to None
    #:
    #: Redis: redis://username:password@host:6379/db
    #: S3: s3://username:password@s3.aws.amazon.com/bucket
    #: Google Storage: google_storage://username:password@cloud.google.com/bucket
    #: SQL: postgresql://username:password@host:3306/db
    #:      mysql+pysql://username:password@host:3306/db
    #:      sqlite://
    #: Memcached: memcache://host:port
    #:
    SESSION_URI = None

# ------------------------------------------------------------------------------
# STORAGE

    #: STORAGE
    #: Flask-Cloudy is used to save upload on S3, Google Storage,
    #: Cloudfiles, Azure Blobs, and Local storage
    #: When using local storage, they can be accessed via http://yoursite/files
    #:

    #: STORAGE_PROVIDER:
    # The provider to use. By default it's 'LOCAL'.
    # You can use:
    # LOCAL, S3, GOOGLE_STORAGE, AZURE_BLOBS, CLOUDFILES
    STORAGE_PROVIDER = "LOCAL"

    #: STORAGE_KEY
    # The storage key. Leave it blank if PROVIDER is LOCAL
    STORAGE_KEY = AWS_ACCESS_KEY_ID

    #: STORAGE_SECRET
    #: The storage secret key. Leave it blank if PROVIDER is LOCAL
    STORAGE_SECRET = AWS_SECRET_ACCESS_KEY

    #: STORAGE_REGION_NAME
    #: The region for the storage. Leave it blank if PROVIDER is LOCAL
    STORAGE_REGION_NAME = AWS_REGION_NAME

    #: STORAGE_CONTAINER
    #: The Bucket name (for S3, Google storage, Azure, cloudfile)
    #: or the directory name (LOCAL) to access
    STORAGE_CONTAINER = os.path.join(APPLICATION_DATA_DIR, "uploads")

    #: STORAGE_SERVER
    #: Bool, to serve local file
    STORAGE_SERVER = True

    #: STORAGE_SERVER_URL
    #: The url suffix for local storage
    STORAGE_SERVER_URL = "files"

# ------------------------------------------------------------------------------
# MAIL

    # AWS SES
    # To use AWS SES to send email
    #:
    #: - To use the default AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #: set MAIL_URI = "ses://"
    #: * To use a different credential:
    #: set MAIL_URI = "ses://{access_key}:{secret_key}@{region}"
    #:
    #: *** uncomment if you are using SMTP instead
    # MAIL_URI = "ses://"

    # SMTP
    #: If you are using SMTP, it will use Flask-Mail
    #: The uri for the smtp connection. It will use Flask-Mail
    #: format: smtp://USERNAME:PASSWORD@HOST:PORT
    #: with sll -> smtp+ssl://USERNAME:PASSWORD@HOST:PORT
    #: with ssl and tls -> smtp+ssl+tls://USERNAME:PASSWORD@HOST:PORT
    #:
    #: *** comment out if you are using SES instead
    # MAIL_URI = "smtp+ssl://{username}:{password}@{host}:{port}"\
    #    .format(username="", password="", host="smtp.gmail.com", port=465)

    #: MAIL_SENDER - The sender of the email by default
    #: For SES, this email must be authorized
    MAIL_SENDER = APPLICATION_ADMIN_EMAIL

    #: MAIL_REPLY_TO
    #: The email to reply to by default
    MAIL_REPLY_TO = APPLICATION_ADMIN_EMAIL

    #: MAIL_TEMPLATE
    #: a directory that contains the email template or a dict
    MAIL_TEMPLATE = os.path.join(APPLICATION_DATA_DIR, "mail-templates")

    #: MAIL_TEMPLATE_CONTEXT
    #: a dict of all context to pass to the email by default
    MAIL_TEMPLATE_CONTEXT = {
        "site_name": APPLICATION_NAME,
        "site_url": APPLICATION_URL
    }

# ------------------------------------------------------------------------------
#: CACHE

    #: Flask-Cache is used to caching

    #: CACHE_TYPE
    #: The type of cache to use
    #: null, simple, redis, filesystem,
    CACHE_TYPE = "simple"

    #: CACHE_REDIS_URL
    #: If CHACHE_TYPE is 'redis', set the redis uri
    #: redis://username:password@host:port/db
    CACHE_REDIS_URL = ""

    #: CACHE_DIR
    #: Directory to store cache if CACHE_TYPE is filesystem, it will
    CACHE_DIR = ""

# ------------------------------------------------------------------------------
#: RECAPTCHA

    #: Flask-Recaptcha
    #: Register your application at https://www.google.com/recaptcha/admin

    #: RECAPTCHA_ENABLED
    RECAPTCHA_ENABLED = True

    #: RECAPTCHA_SITE_KEY
    RECAPTCHA_SITE_KEY = ""

    #: RECAPTCHA_SECRET_KEY
    RECAPTCHA_SECRET_KEY = ""


# ------------------------------------------------------------------------------
#: LOGGING

    # Setup the logging configuration to report errors

    # The logging class to use.
    # The simplest use to setup logging
    LOGGING_CLASS = "logging.StreamHandler"

    # Advanced logging
    # keep the 'loggers' name empty, as it is requested by Magic
    # You can add multiple handlers
    # Make sure "version" is set to 1
    """
    # ADVANCED LOGGING
    LOGGING_CONFIG = {
        "version": 1,
        "handlers": {
            "default": {
                "class": "logging.StreamHandler"
            }
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'WARN',
            }
        }
    }
    """

# ------------------------------------------------------------------------------
# USER PLUGIN
    
    # Bool - To Enable/disable signup
    USER_AUTH_ALLOW_SIGNUP = False
    
    # Bool - To Enable/Disable login
    USER_AUTH_ALLOW_LOGIN = True
    
    # Password reset method: TOKEN or PASSWORD
    USER_AUTH_PASSWORD_RESET_METHOD = "TOKEN"
    
    # The time in minutes for the token reset to expire
    USER_AUTH_RESET_TOKEN_TTL = 60
    


    """
    # List of valid providers
    # Requires: 'consumer_key' and 'consumer_secret'
    USER_OAUTH_CREDENTIALS = {
        "Facebook": {
            "consumer_key": "",
            "consumer_secret": ""
        },
        "Google": {
            "consumer_key": "",
            "consumer_secret": ""
        },

        "Twitter": {
            "consumer_key": "",
            "consumer_secret": ""
        }
    }
    """

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# --- ENVIRONMENT BASED CONFIG -------------------------------------------------


class Development(BaseConfig):
    """
    Config for development environment
    """
    SERVER_NAME = None
    DEBUG = True
    SECRET_KEY = "PLEASE CHANGE ME"


class Production(BaseConfig):
    """
    Config for Production environment
    """
    APPLICATION_PROJECT_NAME = ""
    SERVER_NAME = None
    DEBUG = False
    SECRET_KEY = None