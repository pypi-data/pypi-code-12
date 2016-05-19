from Testing.makerequest import makerequest
from plone import api
from zope.component.hooks import setHooks
from zope.component.hooks import setSite
import Zope2
import logging
import sys
import transaction

log = logging.getLogger()


class ConsoleScript(object):
    def __call__(self, config_file, run_as, server_url=None, context_path=None,
                 portal_id=None, **environ):
        Zope2.Startup.run.configure(config_file)
        environ['SERVER_URL'] = server_url
        self.app = makerequest(Zope2.app(), environ=environ)
        setHooks()
        if portal_id is not None:
            self.portal = self.app[portal_id]
        else:
            portals = self.app.objectValues('Plone Site')
            if len(portals) > 1:
                log.warn('More than one portal - using first one')
            self.portal = portals[0]
        setSite(self.portal)
        self.app.REQUEST.other['PARENTS'] = [self.portal, self.app]
        self.app.REQUEST.other['VirtualRootPhysicalPath'] = (
            '', self.portal.id)

        log.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)

        with api.env.adopt_user(username=run_as):
            if context_path is not None:
                self.context = self.portal.restrictedTraverse(context_path)
            else:
                self.context = self.portal
            self.run()
        transaction.commit()

    def run(self):
        raise NotImplementedError
