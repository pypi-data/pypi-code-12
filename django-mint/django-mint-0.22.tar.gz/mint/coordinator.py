import json
from mint import utils
from mint import exceptions
from django import http
from django.conf import settings
import traceback
import logging


class HttpResponseUnauthorized(http.HttpResponse):
    status_code = 403


class Coordinator(object):
    controllers = []

    def __init__(self, request, ctx, idx=None, action=None):
        self.request = request
        self.ctx = utils.underscore_to_camel(ctx)
        self.id = idx
        self.action = action
        self.related = action
        self.controller = None
        self.related_controller = None

    def open(self):
        for ctx in self.controllers:
            if ctx.__name__ == self.ctx:
                self.controller = ctx(self.request)
                return
        raise exceptions.InvalidContext('This controller does not exist: %s' % self.ctx)

    def run(self):
        try:
            return self.run_inner()
        except exceptions.HttpError as exc:
            if isinstance(exc, exceptions.HttpBadRequest):
                return self.return_error(exc, response=http.HttpResponseBadRequest)
            elif isinstance(exc, exceptions.HttpForbidden):
                return self.return_error(exc, response=http.HttpResponseForbidden)
            elif isinstance(exc, exceptions.HttpNotAllowed):
                return self.return_error(exc, response=http.HttpResponseNotAllowed)
            elif isinstance(exc, exceptions.HttpNotFound):
                return self.return_error(exc, response=http.HttpResponseNotFound)
            elif isinstance(exc, exceptions.HttpUnauthorized):
                return self.return_error(exc, response=HttpResponseUnauthorized)
            elif isinstance(exc, exceptions.HttpError):
                self.report_exception()
                return self.return_error(exc, response=http.HttpResponseServerError)
        except Exception as exc:
            self.report_exception()
            return self.return_error(exc, response=http.HttpResponseServerError)

    def run_inner(self):
        self.open()
        if self.id and (self.related or self.action):
            if self.find_related():
                return self.exec_related()
            elif self.find_m2m_field():
                return self.exec_m2m()
            elif self.find_action():
                return self.exec_action()
            else:
                raise exceptions.HttpBadRequest("No such action or related model: %s" %
                                                self.related if self.related is not None else self.action)
        elif self.id:
            return self.exec_id()
        elif not self.id and self.action:
            if self.find_action():
                return self.exec_action()
            else:
                raise exceptions.HttpBadRequest("No such action: %s" % self.action)
        else:
            return self.exec_root()

    def find_related(self):
        if len(self.controller.related) > 0:
            for ctx in self.controller.related:
                if ctx.__name__ == utils.underscore_to_camel(self.related):
                    self.related_controller = ctx(self.request)
                    return True
            return False
        return False

    def find_m2m_field(self):
        self.controller.open_model(self.id)
        if hasattr(self.controller.model, self.related):
            return True
        return False

    def find_action(self):
        return self.controller.has_action(self.action)

    def exec_related(self):
        self.controller.open_model(self.id)
        self.related_controller.open_model()
        filter = {
            utils.camel_to_underscore(self.controller.__class__.__name__): self.controller.model
        }
        self.related_controller.model.filter(**filter)
        return self.return_success(self.related_controller.exec_root())

    def exec_m2m(self):
        return self.return_success(self.controller.exec_m2m(self.id, self.related))

    def exec_action(self):
        return self.return_success(self.controller.exec_action(self.action, self.id))

    def exec_id(self):
        return self.return_success(self.controller.exec_id(self.id))

    def exec_root(self):
        self.controller.open_model()
        return self.return_success(self.controller.exec_root())

    def return_success(self, out, response=http.HttpResponse):
        if isinstance(out, dict):
            out['result'] = True
        return self.format(out, response=response)

    def return_error(self, exc=None, error=None, message=None, response=http.HttpResponse):
        if exc:
            return self.format({
                'result': False,
                'message': str(exc),
                'error': exc.__class__.__name__,
                'traceback': traceback.format_exc() if settings.DEBUG else '',
            }, response=response)
        elif error and message:
            return self.format({
                'result': False,
                'message': message,
                'error': error
            }, response=response)
        else:
            return self.format({
                'result': False,
                'message': 'Error handler not correctly invoked',
                'error': 'Exception'
            }, response=response)

    def format(self, out, response=http.HttpResponse):
        if out is True:
            return self.format({'result': True}, response=response)
        else:
            return response(json.dumps(out), content_type='application/json')

    def report_exception(self):
        logger = logging.getLogger('django.request')
        logger.exception(
            "Internal Server Error during API call: %s" % self.request.path,
            extra={'status_code': 500, 'request': self.request}
        )