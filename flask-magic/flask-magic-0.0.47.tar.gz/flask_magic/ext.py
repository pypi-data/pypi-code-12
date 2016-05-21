"""
Extensions
"""

import re
import warnings
import logging
import inspect
import functools
from flask import abort, request, current_app
from .core import Magic, init_app
import utils
import humanize
from .extras import markdown_ext
import flask_cloudy
import flask_recaptcha
import flask_seasurf
import flask_kvsession
import flask_cache
import flask_login
import ses_mailer
import flask_mail
import flask_s3

# Load base packages
from flask_magic.plugins import base

__all__ = ["mail",
           "cache",
           "storage",
           "recaptcha",
           "csrf"]
# ------------------------------------------------------------------------------

# user_*

def user_authenticated():
    """ A shortcut to check if a user is authenticated """
    return flask_login.current_user.is_authenticated


def user_not_authenticated():
    """ A shortcut to check if user not authenticated."""
    return not flask_login.current_user.is_authenticated

# ------------------------------------------------------------------------------


def _setup(app):

    check_config_keys = [
        "SECRET_KEY",
        "APPLICATION_ADMIN_EMAIL",
        "APPLICATION_CONTACT_EMAIL",
        "MAILER_URI",
        "MAIL_SENDER",
        "RECAPTCHA_SITE_KEY",
        "RECAPTCHA_SECRET_KEY"
    ]
    for k in check_config_keys:
        if k not in app.config \
                or not app.config.get(k) \
                or app.config.get(k).strip() == "":
            msg = "Config [ %s ] value is not set or empty" % k
            logging.warning(msg)

    app_keys = ["APPLICATION_NAME",
                "APPLICATION_VERSION",
                "APPLICATION_URL",
                "APPLICATION_GOOGLE_ANALYTICS_ID"]
    global_kwargs = {k: app.config.get(k) for k in app_keys}
    Magic.g(**global_kwargs)

    # Setup filters
    @app.template_filter('datetime')
    def format_datetime(dt, format="%m/%d/%Y"):
        return "" if not dt else dt.strftime(format)

    @app.template_filter('strip_decimal')
    def strip_decimal(amount):
        return amount.split(".")[0]

    @app.template_filter('bool_to_yes')
    def bool_to_yes(b):
        return "Yes" if b else "No"

    @app.template_filter('bool_to_int')
    def bool_to_int(b):
        return 1 if b else 0

    @app.template_filter('nl2br')
    def nl2br(s):
        """
        {{ s|nl2br }}

        Convert newlines into <p> and <br />s.
        """
        if not isinstance(s, basestring):
            s = str(s)
        s = re.sub(r'\r\n|\r|\n', '\n', s)
        paragraphs = re.split('\n{2,}', s)
        paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />') for p in paragraphs]
        return '\n\n'.join(paragraphs)

    # More filters
    app.jinja_env.filters.update({
        # slug
        "slug": utils.slugify,
        # Transform an int to comma
        "int_with_comma": humanize.intcomma,
        # Show the date ago: Today, yesterday, July 27 (without year in same year), July 15 2014
        "date_since": humanize.naturaldate,
        # To show the time ago: 3 min ago, 2 days ago, 1 year 7 days ago
        "time_since": humanize.naturaltime,
        # Return a mardown to HTML
        "markdown": markdown_ext.html,
        # Create a Table of Content of the Markdown
        "markdown_toc": markdown_ext.toc
    })

# ------------------------------------------------------------------------------

# Session
#
# It uses KV session to allow multiple backend for the session
def _session(app):
    store = None
    uri = app.config.get("SESSION_URI")
    if uri:
        parse_uri = utils.urlparse(uri)
        scheme = parse_uri.scheme
        username = parse_uri.username
        password = parse_uri.password
        hostname = parse_uri.hostname
        port = parse_uri.port
        bucket = parse_uri.path.strip("/")

        if "redis" in scheme:
            import redis
            from simplekv.memory.redisstore import RedisStore
            conn = redis.StrictRedis.from_url(url=uri)
            store = RedisStore(conn)
        elif "s3" in scheme or "google_storage" in scheme:
            from simplekv.net.botostore import BotoStore
            import boto
            if "s3" in scheme:
                _con_fn = boto.connect_s3
            else:
                _con_fn = boto.connect_gs
            conn = _con_fn(username, password)
            _bucket = conn.create_bucket(bucket)
            store = BotoStore(_bucket)
        elif "memcache" in scheme:
            import memcache
            from simplekv.memory.memcachestore import MemcacheStore
            host_port = "%s:%s" % (hostname, port)
            conn = memcache.Client(servers=[host_port])
            store = MemcacheStore(conn)
        elif "sql" in scheme:
            from simplekv.db.sql import SQLAlchemyStore
            from sqlalchemy import create_engine, MetaData
            engine = create_engine(uri)
            metadata = MetaData(bind=engine)
            store = SQLAlchemyStore(engine, metadata, 'kvstore')
            metadata.create_all()
        else:
            raise ValueError("Invalid Session Store")
    if store:
        flask_kvsession.KVSessionExtension(store, app)



# ------------------------------------------------------------------------------
# Mailer
class _Mailer(object):
    """
    config key: MAIL_*
    A simple wrapper to switch between SES-Mailer and Flask-Mail based on config
    """
    mail = None
    provider = None
    config = None
    _template = None

    @property
    def validated(self):
        return bool(self.mail)

    def init_app(self, app):
        self.config = app.config
        scheme = None

        mailer_uri = self.config.get("MAIL_URI")
        if mailer_uri:
            mailer_uri = utils.urlparse(mailer_uri)
            scheme = mailer_uri.scheme
            hostname = mailer_uri.hostname

            # Using ses-mailer
            if "ses" in scheme.lower():
                self.provider = "SES"

                access_key = mailer_uri.username or app.config.get("AWS_ACCESS_KEY_ID")
                secret_key = mailer_uri.password or app.config.get("AWS_SECRET_ACCESS_KEY")
                region = hostname or self.config.get("AWS_REGION", "us-east-1")
                
                self.mail = ses_mailer.Mail(aws_access_key_id=access_key,
                                            aws_secret_access_key=secret_key,
                                            region=region,
                                            sender=self.config.get("MAIL_SENDER"),
                                            reply_to=self.config.get("MAIL_REPLY_TO"),
                                            template=self.config.get("MAIL_TEMPLATE"),
                                            template_context=self.config.get("MAIL_TEMPLATE_CONTEXT"))

            # SMTP will use flask-mail
            elif "smtp" in scheme.lower():
                self.provider = "SMTP"

                class _App(object):
                    config = {
                        "MAIL_SERVER": mailer_uri.hostname,
                        "MAIL_USERNAME": mailer_uri.username,
                        "MAIL_PASSWORD": mailer_uri.password,
                        "MAIL_PORT": mailer_uri.port,
                        "MAIL_USE_TLS": True if "tls" in mailer_uri.scheme else False,
                        "MAIL_USE_SSL": True if "ssl" in mailer_uri.scheme else False,
                        "MAIL_DEFAULT_SENDER": app.config.get("MAIL_SENDER"),
                        "TESTING": app.config.get("TESTING"),
                        "DEBUG": app.config.get("DEBUG")
                    }
                    debug = app.config.get("DEBUG")
                    testing = app.config.get("TESTING")

                _app = _App()
                self.mail = flask_mail.Mail(app=_app)

                _ses_mailer = ses_mailer.Mail(template=self.config.get("MAIL_TEMPLATE"),
                                              template_context=self.config.get("MAIL_TEMPLATE_CONTEXT"))
                self._template = _ses_mailer.parse_template
            else:
                logging.warning("Mailer Error. Invalid scheme '%s'>" % scheme)

    def send(self, to, subject=None, body=None, reply_to=None, template=None, **kwargs):
        """
        To send email
        :param to: the recipients, list or string
        :param subject: the subject
        :param body: the body
        :param reply_to: reply_to
        :param template: template, will use the templates instead
        :param kwargs: context args
        :return: bool - True if everything is ok
        """
        sender = self.config.get("MAIL_SENDER")
        recipients = [to] if not isinstance(to, list) else to
        kwargs.update({
            "subject": subject,
            "body": body,
            "reply_to": reply_to
        })

        if not self.validated:
            abort("MailmanConfigurationError")

        if self.provider == "SES":
            kwargs["to"] = recipients
            if template:
                self.mail.send_template(template=template, **kwargs)
            else:
               self.mail.send(**kwargs)

        elif self.provider == "SMTP":
            if template:
                data = self._template(template=template, **kwargs)
                kwargs["subject"] = data["subject"]
                kwargs["body"] = data["body"]
            kwargs["recipients"] = recipients
            kwargs["sender"] = sender

            # Remove invalid Messages keys
            _safe_keys = ["recipients", "subject", "body", "html", "alts",
                          "cc", "bcc", "attachments", "reply_to", "sender",
                           "date", "charset", "extra_headers", "mail_options",
                           "rcpt_options"]
            for k in kwargs.copy():
                if k not in _safe_keys:
                    del kwargs[k]

            message = flask_mail.Message(**kwargs)
            self.mail.send(message)

        else:
            abort("MailmanUnknownProviderError")


# ------------------------------------------------------------------------------

# Assets Delivery
class _AssetsDelivery(flask_s3.FlaskS3):
    def init_app(self, app):
        delivery_method = app.config.get("ASSETS_DELIVERY_METHOD")
        if delivery_method and delivery_method.upper() in ["S3", "CDN"]:
            #with app.app_context():
            is_secure = False #request.is_secure

            if delivery_method.upper() == "CDN":
                domain = app.config.get("ASSETS_DELIVERY_DOMAIN")
                if "://" in domain:
                    domain_parsed = utils.urlparse(domain)
                    is_secure = domain_parsed.scheme == "https"
                    domain = domain_parsed.netloc
                app.config.setdefault("S3_CDN_DOMAIN", domain)

            app.config["FLASK_ASSETS_USE_S3"] = True
            app.config["USE_S3"] = True
            app.config.setdefault("S3_USE_HTTPS", is_secure)
            app.config["S3_URL_STYLE"] = "path"
            app.config.setdefault("S3_ONLY_MODIFIED", True)
            app.config.setdefault("S3_GZIP", True)
            app.config.setdefault("S3_BUCKET_NAME", app.config.get("AWS_S3_BUCKET_NAME"))

            super(self.__class__, self).init_app(app)

# ------------------------------------------------------------------------------

init_app(_setup)

init_app(_session)

# Mail
mail = _Mailer()
init_app(mail.init_app)

# Cache
cache = flask_cache.Cache()
init_app(cache.init_app)

# Storage
storage = flask_cloudy.Storage()
init_app(storage.init_app)

# Recaptcha
recaptcha = flask_recaptcha.ReCaptcha()
init_app(recaptcha.init_app)

# CSRF
csrf = flask_seasurf.SeaSurf()
init_app(csrf.init_app)

# Assets delivery
assets_delivery = _AssetsDelivery()
init_app(assets_delivery.init_app)

# ------------------------------------------------------------------------------





