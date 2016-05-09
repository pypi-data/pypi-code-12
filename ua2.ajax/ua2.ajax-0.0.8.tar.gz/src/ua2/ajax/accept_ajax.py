import types
import sys

try:
    from django.utils import simplejson
except ImportError:
    import json as simplejson
from django.http import HttpResponse
from django.http import Http404
from django.utils.log import getLogger
from django.conf import settings
from django.views.debug import ExceptionReporter
from django.contrib import messages

logger = getLogger('django.request')


def json_response(data):
    return HttpResponse(
        simplejson.dumps(data, ensure_ascii=False),
        mimetype='application/json')


def accept_ajax(view_func):
    def _wrap_view_func(request, *args, **kwargs):
        try:
            response = view_func(request, *args, **kwargs)
        except Http404 as e:
            raise Http404(e)

        except Exception as e:
            if not request.is_ajax():
                raise

            logger.error('Internal Server Error: %s' % request.path,
                         exc_info=sys.exc_info(),
                         extra={
                             'status_code': 500,
                             'request': request
                             }
                         )
            response = {'status_code': 500,
                        'extension': 'ua2.ajax.accept_ajax',
                        'request_path': request.path}
            if settings.DEBUG:
                report = ExceptionReporter(request, *sys.exc_info())
                response['debug_msg'] = report.get_traceback_text()
                response['debug_html'] = report.get_traceback_html()
            return json_response(response)

        # no other way to get all headers, except lookup protected variable
        resp = {'status_code': 200,
                'headers': [],
                'extension': 'ua2.ajax.accept_ajax'}

        message_list = []
        # compatibility with jquery-django-messages-ui
        for message in messages.get_messages(request):
            message_list.append({
                    "level": message.level,
                    "message": message.message,
                    "tags": message.tags,
                    })
        if message_list:
            resp['messages'] = message_list

        non_ajax_handler = None
        if isinstance(response, types.DictType):
            resp['content'] = response
            resp['type'] = 'dict'
            non_ajax_handler = json_response

        elif isinstance(response, types.ListType):
            resp['content'] = response
            resp['type'] = 'list'
            non_ajax_handler = json_response

        else:
            resp['content'] = response.content
            resp['type'] = 'string'
            resp['headers'] = response._headers

        if request.is_ajax():
            new_response = json_response(resp)
        elif non_ajax_handler:
            new_response = non_ajax_handler(resp)
        else:
            new_response = response

        return new_response

    return _wrap_view_func
