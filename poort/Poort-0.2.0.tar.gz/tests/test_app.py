# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from avenue import Avenue
from pandora import Laborer
from poort import Gate
from poort import JsonResponse
from poort import Request
from poort import template_or_json_response
from poort.utils import copy_request_environ
import datetime as dt
import poort
import yaml


class TestApp(object):
    def setup_application(self):
        router = Avenue()
        laborer = Laborer()

        class AppGate(Gate):
            def setup(self, environ):
                super(AppGate, self).setup()
                self.attach('request', Request(environ))

            @property
            def request(self):
                """

                :rtype: Request
                """
                return self.retrieve('request')

        app = AppGate()

        @laborer.provider('request')
        def provide_request(kwargs):
            return app.request

        @router.attach(path='/')
        def get_index(request):
            data = {
                'message': 'Hello world!',
                'request': request.as_dict(),
            }

            return template_or_json_response(request, 'index.html', data)

        @router.attach(path='/throws')
        def get_throws(request):
            raise ValueError('Throws errors...')

        @router.attach(path='/static')
        def get_static(request):
            return poort.FileResponse('./index.html')

        @router.attach(path='/download')
        def get_download(request):
            return poort.FileResponse('./index.html',
                                      as_attachment='download-as-index.html')

        @router.attach(path='/set-cookie')
        def get_set_cookie(request):
            value = str(request.params.get('value', 'not-set'))

            response = JsonResponse({
                'message': 'Cookie was set to {:s}.'.format(value)
            })
            response.set_cookie('poort-cookie', value)
            return response

        @router.attach(path='/set-multiple-cookies')
        def get_set_multiple_cookies(request):
            response = JsonResponse({
                'message': 'Setting 10 cookies!'
            })

            for i in range(10):
                response.set_cookie('poort-cookie-{:d}'.format(i), str(i))

            return response

        @router.attach(path='/view-cookie')
        def get_view_cookie(request):
            value = str(request.get_cookie('poort-cookie'))
            response = JsonResponse({
                'message': 'Cookie is currently {:s}.'.format(value)
            })
            return response

        @router.attach(path='/remove-cookie')
        def get_remove_cookie(request):
            response = JsonResponse({
                'message': 'Cookie is removed.'
            })
            response.del_cookie('poort-cookie')
            return response

        def application(environ, start_response):
            copy = copy_request_environ(environ)

            with app(environ):
                request = app.request

                if request.params.get('store') == 'yes':
                    now = dt.datetime.now()
                    filename = './{:s}.yaml'.format(
                        now.strftime('%Y%m%d-%H%M%S'))

                    with open(filename, 'w') as stream:
                        yaml.safe_dump(copy, stream,
                                       allow_unicode=True,
                                       default_flow_style=False,
                                       indent=2)

                path, match = router.match(**request.as_dict())

                if path:
                    try:
                        partial = laborer.provide(path.func)
                        response = partial(**match.kwargs)
                    except Exception as exc:
                        response = JsonResponse({
                            'message': str(exc),
                        }, status_code=500)
                else:
                    response = JsonResponse({
                        'message': 'Page does not exist.'
                    }, status_code=404)

                return response(request, start_response)

        return application

    def test_basics(self):
        application = self.setup_application()
        assert application


application = TestApp().setup_application()

# -- run this test
# gunicorn test_app:application --reload --threads 4
