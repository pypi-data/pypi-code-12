"""cubicweb-sentry application package

support for Sentry (getsentry.com)
"""
from logilab.common.decorators import monkeypatch
from cubicweb.web.views.basecontrollers import ViewController
import logging
logger = logging.getLogger(__name__)


def registration_callback(vreg):
    config = vreg.config
    sentry_dsn = config['sentry-dsn']
    if not sentry_dsn:
        return

    from raven import Client
    client = Client(sentry_dsn)

    original_handle = ViewController.publish

    @monkeypatch(ViewController, 'publish')
    def publish(self, rset=None):
        """ instrumented publish"""
        try:
            return original_handle(self, rset)
        except:
            req = self._cw
            extra = {'user': req.user.dc_title(),
                     'useragent': req.useragent(),
                     'url': req.url(),
                     'last_visited_page': req.last_visited_page(),
                     'form': req.form}
            ident = client.get_ident(client.captureException(extra=extra))
            msg = "Exception caught; reference is %s" % ident
            logger.critical(msg)
            raise
