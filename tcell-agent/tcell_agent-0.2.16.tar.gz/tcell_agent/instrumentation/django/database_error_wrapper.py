from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import django_meta
from tcell_agent.instrumentation.django.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.instrumentation.django.utils import django15or16

import logging
import tcell_agent.tcell_logger

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

def instrument_database_error_wrapper():
    if django15or16 == False:
        # Todo: Add Django 1.5/1.6 support
        try:
            from django.db.utils import DatabaseErrorWrapper
            def _tcell_exit(_tcell_original_exit, self, exc_type, exc_value, traceback):
                if exc_type is not None:
                    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
                    if appsensor_policy is not None:
                        request = GlobalRequestMiddleware.get_current_request()
                        meta = django_meta(request)
                        appsensor_policy.sql_exception_detected(self.wrapper.Database, meta, exc_type, exc_value, traceback)

                return _tcell_original_exit(self, exc_type, exc_value, traceback)
            InstrumentationManager.instrument(DatabaseErrorWrapper, "__exit__", _tcell_exit)
        except Exception as e:
            LOGGER.exception("Could not instrument database error wrapper", e)
