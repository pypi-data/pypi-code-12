from flask import Response, request
from flask.views import View
from flask import render_template

from iweb.model import Model
from iweb.sys import AppConfig

import json

appConfig = AppConfig()

class BaseView(View):
    controller_debug = False

    def __init__(self):
        self.model = Model()
        self.db = self.model.db

    def get_parameters(self, params):
        ret = {}
        for p in params:
            ret[p] = request.args.get(p)
        return ret

class PersistenceAndResult(View):
    def dispatch_request(self):
        try:
            map_result = self.process()
            return Response(json.dumps(map_result), mimetype='application/json')
        except Exception as e:
            print(e)
            map_result['status'] = -1
            map_result['description'] = str(e)
            return Response(json.dumps(map_result), mimetype='application/json')


class PersistenceOnly(View):
    def dispatch_request(self):
        map_result = {}
        try:
            self.process()
            map_result['status'] = 0
            map_result['description'] = 'Request success'
            return Response(json.dumps(map_result), mimetype='application/json')
        except Exception as e:
            print(e)
            map_result['status'] = -1
            map_result['description'] = str(e)
            return Response(json.dumps(map_result), mimetype='application/json')


class APIController(BaseView):


    def process(self):
        raise NotImplementedError()

    def dispatch_request(self):
        data = None
        map_result = {}
        try:
            map_result['status'] = 1
            map_result['description'] = 'OK Request'
            data = self.process()
            if data != None:
                map_result['data'] = data
        except Exception as e:
            print(e)
            self.map_result['status'] = -1
            self.map_result['description'] = 'Request error'
        from bson import json_util
        json_result = json.dumps(map_result, default=json_util.default)

        data = None
        map_result = {}
        self.model.client.close()

        return Response(json_result, mimetype='application/json')


class ViewController(View):
    page_name = None

    def process(self):
        raise NotImplementedError()

    def dispatch_request(self):
        try:
            result = self.process()
        except Exception as e:
            print(e)
        return render_template(self.page_name, **result)