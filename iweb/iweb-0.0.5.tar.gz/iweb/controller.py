from flask import Response, request
from flask.views import View
from flask import render_template

from iweb.model import Model
from iweb.sys import AppConfig

import json,logging

appConfig = AppConfig()
 
logger = logging.getLogger("iweb")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(module)s : %(lineno)d : %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
ch.setFormatter(formatter)
logger.addHandler(ch)
    
class BaseView(View):
    controller_debug = False
    log = logging.getLogger('iweb')
    
    def __init__(self):     
        self.model = Model()
        self.db = self.model.db

    def get_parameters(self, params):
        ret = {}
        for p in params:
            ret[p] = request.args.get(p)
        return ret

class PersistenceAndResult(BaseView):
    def dispatch_request(self):
        try:
            map_result = self.process()
            return Response(json.dumps(map_result), mimetype='application/json')
        except Exception as e:
            print(e)
            map_result['status'] = -1
            map_result['description'] = str(e)
            return Response(json.dumps(map_result), mimetype='application/json')


class PersistenceOnly(BaseView):
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
        data = None
        self.log.info('*** start request')
        try:
            self.map_result['status'] = 1
            self.map_result['description'] = 'OK Request'
            data = self.process()
            if data != None:
                self.map_result['data'] = data
        except Exception as e:
            self.log.info(e)
            self.map_result['status'] = -1
            self.map_result['description'] = 'Request error'
            
        from bson import json_util
        json_result = json.dumps(self.map_result, default=json_util.default)

        data = None
        self.map_result = {}
        self.model.client.close()
        
        self.log.info('*** end request')
        return Response(json_result, mimetype='application/json')


class ViewController(BaseView):
    page_name = None

    def process(self):
        raise NotImplementedError()

    def dispatch_request(self):
        try:
            result = self.process()
        except Exception as e:
            print(e)
        return render_template(self.page_name, **result)