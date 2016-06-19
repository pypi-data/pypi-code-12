from flask import Response, request, redirect
from flask.views import View
from flask import render_template, url_for

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
    used_model = False
    log = logging.getLogger('iweb')
    
    def __init__(self): 
        if self.used_model:
            self.model = Model()
            self.db = self.model.db
    
    def get_post(self, params):
        ret = {}
        for p in params:
            ret[p] = request.form[p]
        return ret

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
        
        self.log.info('*** end request')
        return Response(json_result, mimetype='application/json')


class ViewController(BaseView):
    page_name = None
    page_controller = False

    def process(self):
        raise NotImplementedError()        

    def dispatch_request(self):
        try:
            result = self.process()
        except Exception as e:
            self.log.info(str(e))
        
        if self.page_controller:
            return redirect(self.page_name)
        else:
            return render_template(self.page_name, **result)


class CusAndConController(BaseView):
    
    def process(self):
        raise NotImplementedError()
    
    def return_view(self, page_name, result):
        return render_template(page_name, **result)
    
    def return_controller(self, page_name):
        return redirect(url_for(page_name))
    
    def return_json(self, map_result):
        return Response(json.dumps(map_result), mimetype='application/json')
        
    def dispatch_request(self):
        try:
            return self.process()
        except Exception as e:
            self.log.info(str(e))
    
class RenderTemplateView(View):
    def __init__(self, template_name):
        self.template_name = template_name
    def dispatch_request(self):
        return render_template(self.template_name)    