from flask import Response
from flask.views import View
from flask import render_template

import json

class BaseView(View):
    controller_debug = False

    def get_parameters(self, params):
        ret = []
        for p in params:
            ret.append(request.args.get(p))
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
    map_result = {}

    def process(self):
        raise NotImplementedError()

    def dispatch_request(self):
        try:
            self.map_result['status'] = 1
            self.map_result['description'] = 'OK Request'
            self.map_result['data'] = self.process()
        except Exception as e:
            print(e)
            self.map_result['status'] = -1
            self.map_result['description'] = str(e)
            self.map_result['data'] = []
        return Response(json.dumps(self.map_result), mimetype='application/json')


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