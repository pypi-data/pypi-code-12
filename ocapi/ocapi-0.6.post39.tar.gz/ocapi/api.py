#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c)Ing. Zdenek Dlauhy, Michal Dlauhy, info@dlauhy.cz

__updated__ = "2016-04-10"

"""
ocapi
=====

This is API connector to www.pripravto.cz service for furniture makers. You should
be able to use it to create your custom designs for furniture, download data
and eventually build your partial interface. Connector is built on HTTP GET and
POST methods and it uses your account on service.

This connector can also be used to build custom api connection to another services.

Instalation
-----------

For instalation you can download package or install by **pip**. Downloaded you
can just unpack or get from from https://pypi.python.org/pypi/ocapi and install it::

    #download archive
    wget https://bitbucket.org/pripravto/ocapi/get/default.tar.gz
    cd /tmp
    virtualenv test
    source test/bin/activate
    tar -xvf default.tar.gz
    #specify correct name
    cd pripravto....

Instalation::

    python setup.py install

or install by pip::

    pip install ocapi


Quickstart
----------

First you should get your account on **https://pripravto.cz** service, when you will have it
Login normally into service. Then you can start by opening Python console
and importing ocapi::

    import ocapi.api as oc
    import math
    args = {'name':'test2','position':[0,0,0],'size':[1000,1000,1000]}
    #set your own credentials will log error with these use credentials
    prod = oc.CabinetMaker(args, username="test",password="test")
    for i in range(36):
        size = [18,math.sin(math.radians(i*10))*50+80,18]
        rot = [0,0,10+i*2]
        prod.add_element(pos=[i*20,0,0],size=size,rot=rot)
    prod.finish()

This is partial example which will show you base usage of this api. This will create
serries of elements which are sized by sin function and rotated by series of
iteration.

To build something more usefull you can make first base cabinet by just writing down
one function::

    args = {'name':'cabinet2','position':[0,0,0],'size':[600,600,1000]}
    prod.parse_args(args)
    #build our base parts
    prod.add_basic()
    #add doors
    prod.add_doors()
    prod.finish()

After data creation you can also check what kind of data you have created on service
itself and also download images and so on.

Username and password are specified at start of object::

    prod = oc.CabinetMaker(args, username="test",password="test", host="test.pripravto.cz")
    #your username and password is from https://pripravto.cz/oc/register/start

For complete registration process you need your functional e-mail address and fill out
data required by registration. **You should keep your user credentials secret.**
For examples what can be built on this api connector take a look on http://pripravto.cz/en/blog
where we put examples.

More documantation for pripravto service or about this plase see web page or
**oc.CabinetMaker** class.

Development
-----------

You can contact us or raise issues on https://bitbucket.org/pripravto/ocapi
Developmnet is also made on Bitbucket, you can clone repository and start
making chaneges. We also plan to use this api connector to be able to connect
with diffrent applications more quickly and easily.

For this project we are using PyVmMonitor on http://www.pyvmmonitor.com


module for access to oc api

base usecase::

    import ocapi.api as oc
    import math
    args = {'name':'test2','position':[0,0,0],'size':[1000,1000,1000]}
    prod = oc.CabinetMaker(args, username="test",password="test")

    for i in range(36):#count through whole rotation
        size = [18,math.sin(math.radians(i*10))*50+80,18]#change size
        rot = [0,0,10+i*2]#rotate part
        prod.add_element(pos=[i*20,0,0],size=size,rot=rot)
    prod.finish()

"""

import json
import sys

class AttrDict(dict):
    """
    attr dict > create base object
    """
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    pass

#this is global settings for BaseControl class
settings ={"username":None, "password":None, "host":"https://pripravto.cz:443", "login":True}


if sys.platform == "brython":
    # this code here is specially crafted mostly for brython api
    # first hook up brython version
    # do not make imports if they are not needed it is slow.
    # this makes brython faster
    # get connection object for ajax browser
    import ocapi.brythonapi
    info = "If you need real version import ocapi.info"
    str.encode = lambda x, y: x
    str.decode = lambda x, y: x
    convert_to_base = lambda x:x
    # special function for callbacks from UI
    gui_callback_function = lambda x:x
    #TODO: fix me
    uuid = AttrDict({"uuid4":lambda x="If you need random import uuid and rewrite this":x})
    window = ocapi.brythonapi.window
    localStorage = window.localStorage
    basestring = str
    connect = ocapi.brythonapi.Connection
    log = ocapi.brythonapi.log
    base64_decode = ocapi.brythonapi.window.atob

    def gui_callback(func=None, save_last=None):
        """
        this function is defined for window callbacks > use it in brython
        if func is not defined use oc.callback_function = your_func_name
        normal Python does not need this
        """
        log.info("Starting callback..")
        output_str = window.join_data_base('#funcdata :input')
        # here is eval, because input should be js object > JSON > python str
        # we do not have literal_eval in brython :(
        output = eval(output_str)
        if save_last is None:
            try:
                save_last = int(window.localStorage['app.editor_make_save_params'])
            except Exception as e:
                log.error("Cannot get settings...{}".format(e))
        if save_last:
            log.info("Saving last parameters")
            window.localStorage['app.editor_last_parameters'] = output_str
        log.info("Selected data '{}'".format(output))
        assert isinstance(output, dict), "Passed data should be dict"
        window.jQuery('#myModal').modal('hide')
        log.info("Closing window...")
        if func is None:
            func = gui_callback_function
        log.info(func)
        try:
            func(**output)
        except Exception as e:
            import traceback
            error = traceback.format_exc()
            log.error(error)
            log.error("{}".format(e))
            window.alert("{}".format(e))
        log.info("Finishing call")

    def gui_get_last_parameters(parameters):
        """get last parameters from gui from local storage"""
        log.info(parameters)
        try:
            last_parameters = window.localStorage['app.editor_last_parameters']
        except Exception as e:
            log.error("Cannot find specified last parameters {}".format(e))
            last_parameters = None
        if last_parameters:
            try:
                last_parameters_js = window.data_to_json(last_parameters)
                # if this can be loaded by JSON assume, that eval is okay
                json.loads(last_parameters_js)
                eval_data = eval(last_parameters)
            except Exception as e:
                log.error("Cannot parse data...")
                eval_data = {}
            if set(eval_data.keys()) == set(parameters.keys()):
                log.info("Using old saved values from local storage")
                parameters = eval_data
            else:
                log.info("Present data are from another function")
        return dict(parameters)

    def modal_window(func, parameters,options=None,trans=None,lang=None,glob=None,save_last=1):
        '''
        :param func: function which gets called inside modal window run
        :param parameters: default parameters
        :param options: set options to be showed for users
        :param trans: translations for layout
        :param lang: specify lang

        function to call modal_window with several options from default parameters
        '''
        global gui_callback_function
        if lang is None:
            lang = window.lang
        if glob is None:
            glob = {}
        if options is None:
            options = {"select_list":{}, "radio_list":{},"lists_list":{}}
        window.localStorage['app.editor_make_save_params'] = save_last
        gui_callback_function = func
        _parameters = gui_get_last_parameters(parameters)
        if trans:
            trans_lang= trans.get(lang,{})
            if trans_lang:
                for key in trans_lang:
                    window.translation[lang][key] = trans_lang.get(key,key)
            else:
                log.error("Cannot get translations..")
        doc =  gui_callback_function.__doc__
        if doc:
            doc =doc.format(updated=glob.get('__updated__',None),version=glob.get('__version__',None))
        log.info(doc)
        window.modal_data2(str(_parameters),False, False, options,gui_callback,doc)

else:
    # here is normal python
    import logging
    import functools
    import os
    import base64
    import uuid
    import collections
    import ocapi.info as info
    import ocapi.urllibtls
    connect = ocapi.urllibtls.connect
    logging.basicConfig(level=0)
    log = logging.getLogger(__name__)

    base64_decode = base64.decodestring

    class WrapItem(object):
        """wrapper which can be used in every way"""
        def __init__(self, item=None):
            self.item = item
        def __getattr__(self, name):
            try:
                item = getattr(self.item, name)
                return item if name is 'item' else WrapItem(item)
            except AttributeError:
                return WrapItem()
        def __call__(self):
            return self.item
    
    #this is wrapper for window object which does not exist in python
    window =  WrapItem()

    def modal_window(func, parameters,options=None,trans=None,lang="cs",glob=None,save_last=1):
        '''
        :param func: function which gets called inside modal window run
        :param parameters: default parameters
        :param options: set options to be showed for users
        :param trans: translations for layout
        :param lang: specify lang
        function to call modal_window with several options from default parameters
        if this is run in normal python, it just calls current function with parameters
        '''
        try:
            func(**parameters)
        except Exception as e:
            log.error("Error: {} when running function {}".format(e, func))
            import traceback
            error = traceback.format_exc()
            log.error(error)
            log.error("{}".format(e))
            raise

    def _cmd_parser(settings):
        """parse cmd lines and update settings"""
        import argparse
        parser = argparse.ArgumentParser(prog="ocapi", description="ocapi OptimCabinet connector")
        parser.add_argument('--username', help='set username', default=None, type=str)
        parser.add_argument('--password', help='set password', default=None, type=str)
        parser.add_argument('--host', help='set hostname for server', default=None, type=str)
        args, unknown = parser.parse_known_args()
        if not settings["username"]:
            settings["username"] = args.username
        if not settings["password"]:
            settings["password"] = args.password
        if not settings["host"]:
            settings["host"] = args.host
        return args, parser

    #call parser for cmd when running in python
    _cmd_parser(settings)

    def convert_to_base(data):
        """
        convert data input to base types
        """
        if isinstance(data, basestring):
            try:
                return str(data.encode('utf-8'))
            except UnicodeDecodeError:
                return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(convert_to_base, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert_to_base, data))
        else:
            return data



#from here all code is shared
upload_template = """-----------------------------{boundary}
Content-Disposition: form-data; name="myfile"; filename="{filename}"
Content-Type: application/octet-stream

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c) pripravto.cz
# import this
{data}

-----------------------------{boundary}
Content-Disposition: form-data; name="order"


-----------------------------{boundary}--
"""

def api_generator(save=True):
    """
    function for api generation which creates code
    for base CabinetMaker class. This function can be used only in full OptimCabinet
    framework. It will not work without several other functions.
    """
    klass = """
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c)Ing. Zdenek Dlauhy, Michal Dlauhy, info@dlauhy.cz

class CabinetMakerBase(object):
"""
    funcs_def = """
    def {func}(self, {parameters}):
        '''{doc}'''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='{func}', **_loc)

"""
    def attach_attrs(attrs):
        """attach parameters inside template"""
        return ",".join("{}={}".format(k, "'{}'".format(v) if isinstance(v, str) else v) for k, v in sorted(attrs.items()))
    # this import needs whole optimcabinet
    import initialization as oc
    import webapp.web_products
    # get base data
    doc = webapp.web_products.product_doc_generator(oc.CabinetMaker)
    funcs = webapp.web_products.product_parameters_generator(oc.CabinetMaker, generate=True, make_all=True)
    all_data = {}
    # merge data together
    for key, value in funcs:
        all_data[key] = {'attrs':value}
    for key, value in doc:
        all_data[key]['doc'] = value
    all_funcs_def = {}
    # make function definition
    for key, value in all_data.items():
        all_funcs_def[key] = funcs_def.format(func=key,
                                              parameters=attach_attrs(value['attrs']),
                                              doc=value['doc'])
    # merge whole document and save it
    klass += "".join(v for k, v in all_funcs_def.items())
    if save:
        filename = os.path.abspath(__file__)
        path, filename = os.path.split(filename)
        writer = open("{}/product.py".format(path), "w")
        writer.write(klass)
        writer.close()
    return klass


# import local api of CabinetMaker
try:
    from ocapi.product import CabinetMakerBase
except ImportError as e:
    log.error(e)
    log.warn("Running api generator")
    api_generator()
    raise


class BaseControl(object):
    """
    base object for web api access
    initialize connection to some webservice
    """
    def __init__(self, username=None, password=None, host=None,
                 port=None, debug=None, connector=connect, filepath="/tmp",
                 tls=True, raise_error=True):
        """
        :param username: username of user accessing service
        :type username: str
        :param password: password of user accessing service
        :type password: str
        :param host: base name of domain
        :type host: str
        :param port: port to connect
        :type port: int
        :param debug: set debug level
        :type debug: int or None
        :param connector: set connector function
        :type connector: func
        :param filepath: path where to save parts
        :type filepath: str
        :param tls: use tls mechanism
        :type tls: bool
        :param raise_error: make errors to be Exceptions
        :type raise_error: bool
        """
        self.cookie = None
        self.connector = connector
        self.debug = debug
        self.raise_error = raise_error
        if sys.platform == "brython":
            #in brython remove all this settings
            self.username = ""
            self.password = ""
            self.host = ""
            self.port = ""
            self.filepath = ""
            self.tls = None
        else:
            #if we are in normal python get settings from settings dict/cmd
            if username is None:
                username = settings["username"]
            self.username = username
            if password is None:
                password = settings["password"]
            self.password = password
            if host is None:
                host = settings["host"]
            #parse host, port etc..
            host, port, tls = self._parse_url(host, port, tls)
            self.host = host
            self.port = port
            self.tls = tls
            self.filepath = filepath
        log.info("Creating connection {}".format(self))

    def __del__(self):
        log.info("Finishing all connections on {}".format(self))

    def _parse_url(self, host, port, tls):
        """this function is used to create base settings for rest of application
        when whole settings is entered like https://pripravto.cz:433"""
        if sys.platform != "brython":
            result = ocapi.urllibtls.urllib.parse.urlparse(host)
            if result.hostname:
                _host = result.hostname
            else:
                _host = host
            if result.port:
                _port = result.port
            else:
                _port = port
            if result.scheme:
                if result.scheme =="https":
                    _tls = True
                elif result.scheme =="http":
                    _tls = False
                else:
                    raise Exception("Cannot handle diffrent type of connection {}".format(result.scheme))
            else:
                _tls = tls
        else:
            _host, _port , _tls = host, port, tls
        return _host, _port , _tls

    def login(self, username=None, password=None, url="/login"):
        '''
        function to make login into app - base login action

        :param username: specify username
        :param password: specify password
        :param url: url where to submit
        '''
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        data = dict(username=username, passwd=password)
        #do not log username and passwd
        response = self.action(url=url, data=data, method="POST", make_log=False)
        if response.status == 302:
            # get cookie or start app
            headers = self.get_headers(response)
            cookie = headers.get("set-cookie", None)
            if cookie:
                self.cookie = cookie.split(";")[0]
            location = headers.get("location", None)
            if location == "/oc/start":
                import time
                # start app
                response = self.action(url=location)
                log.info("Waiting for app to start!")
                time.sleep(5)
        return response

    def action(self, url, data=None, host=None, method="GET", headers=None,
               convert=None, tls=None, port=None, make_log=True, timeout=20):
        '''
        function which makes action ie. download file and send data

        :param url: specify string URL address where to connect
        :param data: send data to app can be string or dict
        :param host: connect to server
        :param method: specify method type GET or POST
        :param headers: send specific headers
        :param convert: apply automated conversion function
        :param tls: use TLS to connect
        :param port: specify
        '''
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        if tls is None:
            tls = self.tls
        if make_log:
            log.debug("Contacting url {}:{}{} with {}".format(host, port, url, data))
        response = self.connector(host=host, url=url, port=port, data=data, method=method,
                                  headers=headers, debug=self.debug, cookie=self.cookie,
                                  tls=tls,timeout=timeout)
        if response.status < 400:
            if convert:
                return convert(response)
            else:
                return response
        else:
            msg = "Error in connecting requested url {}:{}"
            log.error(msg.format(response.reason, response.status))
            return self.check_response(response)

    def save_file(self, response, headers=None,save=True):
        """save file if response should be file"""
        if headers is None:
            headers = self.get_headers(response)
        if headers.get("content-disposition", False):
            filename = headers["content-disposition"].split("filename=")[-1]
        else:
            filename = str(uuid.uuid4())
        if headers.get("content-transfer-encoding", None) == "base64":
            data = base64_decode(response.read())
        else:
            data = response.read()
        filename = "{}/{}".format(self.filepath, filename)
        if sys.platform != "brython":
            if save:
                with open(filename, 'wb') as writer:
                    writer.write(data)
                    writer.close()
                    log.info("File saved to {}".format(filename))
                return filename
            else:
                return data
        return data

    def upload_file(self, data, boundary="upload_from_editor", filename="text.txt",
                    template=None, headers=None):
        """this function to upload data to server with custom settings"""
        if template is None:
            template = upload_template
        data = template.format(boundary=boundary, filename=filename, data=data)
        msg_boundary = "multipart/form-data; boundary=---------------------------{boundary}".format(boundary=boundary)
        if headers is None:
            headers = {"Content-Type":msg_boundary}
        if 'content-type' not in headers:
            headers["Content-Type"] = msg_boundary
        return self.action("/upload", method="POST", data=data, headers=headers)

    def get_headers(self, response):
        """make headers same on Python2 and 3"""
        headers = dict(response.getheaders())
        headers = {key.lower():value for key, value in headers.items()}
        return headers

    def check_response(self, response):
        if response.status >= 400 and self.raise_error:
            raise Exception("Server response {}:{}".format(response.status,response.reason))
        else:
            return response

    def convert(self, response, headers=None, status=200):
        """automated convertor function which when is used in self.action
        changes what will happen with response
        """
        if response.status == status:
            if headers is None:
                headers = self.get_headers(response)
            headers['content-type'] = headers.get('content-type', None)
            log.info("Converting data sources {} {}".format(response, headers['content-type']))
            if headers['content-type'] == 'text/xml' or headers['content-type'] == 'application/xml':
                try:
                    import inout.optimio
                    return inout.optimio.xml2obj(response.read())
                except ImportError as e:
                    log.error(e)
                    return response
            elif headers['content-type'] in ['text/json', 'application/json','application/json; charset=utf-8']:
                if sys.version_info.major == 3:
                    return json.loads(response.read().decode("utf-8"))
                else:
                    return convert_to_base(json.loads(response.read().decode("utf-8")))
            elif headers['content-type'] == 'image/svg+xml' or headers['content-type'] == 'image/jpeg':
                return self.save_file(response, headers)
            elif headers['content-type'] == 'text/plain':
                text = response.read().decode("utf-8")
                log.warn(text)
                return text
            elif headers.get("content-disposition", False):
                return self.save_file(response, headers)
            else:
                log.error("Cannot find correct convert option..")
        return response

class Control(BaseControl):
    """
    this class creates alll basic method which will be needed
    to control web app. It does not create production functions
    and also it should just set and receive data
    """
    #custom functions
    def other_funcs(self):
        """attach other functions"""
        self.action_list = {'make_commit':'/rev/commit',
                            'make_new':'/system/new',
                            'make_save':'/system/savepickle'}
        self._make_funcs(self.action_list)

    def _make_funcs(self, actions):
        """make functions based on actions list with partial"""
        for key, value in actions.items():
            func = functools.partial(self.action, url=value, convert=self.convert)
            setattr(self, key, func)

    def _make_optim_calc(self, template="optimalize", name=None, obj_id=None, make_new=True):
        """
        :param template: template to get
        :type template: str
        :param name: get requested order
        :type name: str
        :param obj_id: get requested id
        :type obj_id: int
        :param make_new: create new calculation or optimalization
        :type make_new: bool
        """
        log.info("Trying to download data for {}".format(template))
        if name is None:
            name = self.get_order_name()
        if make_new:
            response = self.action(url="/{}/".format(template))
        if obj_id is None:
            last_calc = self.action(url="/json/{}/orders".format(template), convert=self.convert)
            # count from 0
            obj_id = last_calc[name] - 1
        url = "/json/{}/orders/{}/{}".format(template, name, obj_id)
        return self.action(url=url, convert=self.convert)

    def get_optim(self, name=None, obj_id=None):
        """get optim details for specified order and number"""
        return self._make_optim_calc(template="optimalize", name=name, obj_id=obj_id, make_new=False)

    def create_optim(self, name=None):
        return self._make_optim_calc(template="optimalize",name=name, make_new=True)

    def get_calc(self, name=None, obj_id=None):
        """get calculation details for specified order and number"""
        return self._make_optim_calc(template="calculation", name=name, obj_id=obj_id, make_new=False)

    def create_calc(self, name=None):
        return self._make_optim_calc(template="calculation",name=name, make_new=True)

    def get_order_name(self):
        """get name of opened order"""
        response = self.action(url="/json/sidebar", convert=self.convert)
        return str(response['order'])

    def get_order(self, name=None):
        """get order data"""
        if name is None:
            name = self.get_order_name()
        return self.action(url="/json/orders/{}".format(name), convert=self.convert)

    def create_order(self,name,customer, delete_all=True):
        if delete_all:
            ret = self.action("/system/new")
        data = {"name":name, "info":"info", "customer":customer}
        return self.action("/orders/create",data=data,method="POST")

    def get_orders_list(self):
        """get orders list"""
        orders_list = self.action(url="/json/sidebar", convert=self.convert)['orders']
        return [order for order in orders_list]

    def get_item_db(self, name=None):
        """get requested material"""
        mat = self.action(url="/json/db/{}".format(name), convert=self.convert)
        return AttrDict(mat)
    #products
    def get_product_name(self, name=None):
        """get current active product name"""
        if name is None:
            name = getattr(self, "name", "untitled")
        return name

    def get_product(self, name=None):
        """get actual product data from current order"""
        name = self.get_product_name(name)
        res = self.action(url="/json/products/{}/all".format(name), convert=self.convert)
        product = AttrDict(res)
        self._make_product(product)
        return product

    def get_products(self,remove_types=("item","wall")):
        """get all products at once from current order"""
        res = self.action(url="/json/products_all", convert=self.convert)
        products = AttrDict(res)
        self._make_products(products,remove_types)
        return products

    def _make_products(self, space, remove_types):
        """change json products to series of products and elements"""
        prods = []
        for i, product in enumerate(space.products):
            product = AttrDict(product)
            if product.fce not in remove_types:
                self._make_product(product)
                prods.append(product)
        space.products = prods

    def _make_product(self, product):
        """create a product from data basicly add elements"""
        for name, element in sorted(product.elements.items()):
            product.elements[name] = AttrDict(element)

    def get_products_list(self):
        """get products list"""
        products_list = self.action(url="/json/sidebar", convert=self.convert)['products']
        return [prod[0] for prod in products_list]

    def get_element(self, element, product=None):
        """get element object from json"""
        product = self.get_product_name(product)
        element = self.action(url="/json/products/{}/{}".format(product, element), convert=self.convert)
        return AttrDict(element)

    def get_element_from_product(self, product, element):
        """get element object from product"""
        if isinstance(element, int):
            element = product['data'][str(element)]
        return AttrDict(product['elements'][element])

    def get_image(self, name=None, order=None, paths=None, typ="product", url=None,
                  convert=True):
        """
        :param name: specify product name
        :type name: str
        :param order: specify order name
        :type order: str
        :param paths: send paths to select
        :type paths: dict
        :param typ: choose type
        :type typ: str
        :param url: url to get image
        :type url: str
        :param convert: save file or no
        :type convert: bool
        
        get image based on settings"""
        log.info("Trying to download image")
        if paths is None:
            paths = {'element':'products/elements',
                     'product':'products',
                     'product_viz':'products/viz',
                     'optim':'optim',
                     'viz':'products/viz',
                     'img':'import'}
        name = self.get_product_name(name)
        if order is None:
            order = self.get_order_name()
        if typ == "product":
            name = "{}_{}.svg".format(order, name)
        elif typ == "optim":
            pass
        elif typ == "product_viz":
            name = "{}_{}.jpeg".format(order, name)
        elif typ == "viz":
            name = "{}.jpeg".format(order)
        else:
            raise Exception("Wrong type of requested image")
        if url is None:
            url = "/userdata/{}/{}".format(paths[typ], name)
        if convert:
            image = self.action(url=url, convert=self.convert)
        else:
            image = self.action(url=url)
        return image

    def load_products(self, name):
        """load products with specified name"""
        return self.action(url="/system/loadpickle{}".format(name))

    def save_products(self):
        """function to save current products"""
        response = self.action(url="/system/ordersave")
        response = self.action(url="/system/savepickle")
        response = self.action(url="/rev/commit")

    def set_profile(self,profile,parameters_name=None, data=None):
        """set profile from data or from local storage on set parameter name"""
        log.info("Setting new base settings {}".format(profile))
        if parameters_name is None:
            parameters_name = profile.split(".")[1]
        if data is None:
            try:
                data = window.localStorage[profile]
            except KeyError as e:
                log.error("Cannot find specified settings {}:{}".format(profile,e))
                data = None
        if data:
            if not isinstance(data,str):
                data = str(data)
            log.info([profile,data])
            return self.action(url="/usersettings", method="POST", data={parameters_name:data})
        else:
            log.error("Cannot set new parameters {}".format(data))
            return None

    def search_func(self,functions, key, app_web_name=None):
        """function to find correct settings"""
        log.info("Searching for function {}".format(key))
        found = []
        for func_name,parameters  in functions:
            if func_name == key:
                user_name = parameters.get('app_web_name',"")
                if app_web_name == user_name:
                    return [func_name, parameters]
                else:
                    found = [func_name, parameters]
        log.warn("Function parameters returned are not exact as requested {}".format(app_web_name))
        #if we cannot return target, return closest match
        return found

    def get_usersettings(self, name):
        """get base settings from server"""
        log.info("Getting base user settings")
        data = self.action("/usersettings")
        if sys.platform  != "brython":
            #TODO: add option for normal python
            raise Exception("This is not implemented outside brython")
        doc = window.document.createElement("html")
        doc.innerHTML = data.read()
        obj = doc.getElementsByClassName("parameter")
        ret = None
        for element in obj:
            if element.name == name:
                ret = eval(element.innerHTML)
        return ret

    def custom_action(self, method="name", **kwargs):
        """custom action to save data"""
        self.data.append((method, kwargs))

    def add_empty(self, func_key='add_empty', **kwargs):
        '''
        special function here we assume that function is empty
        and should be handled by server so we remove not needed data and
        also func_key which would collide with server version
        '''
        loc = dict(locals())
        loc.pop('self')
        loc.update(loc['kwargs'])
        loc.pop('kwargs')
        loc.pop('func_key')
        self.custom_action(method=func_key, **loc)


class CabinetMaker(Control, CabinetMakerBase):
    """
    This Class gets product functions from cabinet maker class which
    can be dynamically generated by api_generator function.

    This Class is created to construct products as original cabinet maker

    example::

        import ocapi.api as oc
        import math
        args = {'name':'test2','position':[0,0,0],'size':[1000,1000,1000]}
        prod = oc.CabinetMaker(args, username="test",password="test")
        for i in range(36):#count through whole rotation
            size = [18,math.sin(math.radians(i*10))*50+80,18]#change size
            rot = [0,0,10+i*2]#rotate part
            prod.add_element(pos=[i*20,0,0],size=size,rot=rot)
        prod.finish()

    """
    def __init__(self, args=None, username=None, password=None, host=None,
                 port=443, debug=None, connector=connect, filepath="/tmp",
                 login=None, tls=True, raise_error=True):
        BaseControl.__init__(self, username=username, password=password, host=host, port=port,
                             debug=debug, connector=connector, filepath=filepath, tls=tls,
                             raise_error=raise_error)
        self.data = []
        self.name = "untitled"
        if args:
            self.parse_args(args)
        if login is None:
            login = settings.get("login",None)
        if login and sys.platform != "brython":
            self.login(username, password)

    def parse_args(self, params):
        """transform parameters into type used on web service"""
        params = dict(params)
        assert isinstance(params, dict)
        params['posX'] = params['position'][0]
        params['posY'] = params['position'][1]
        params['posZ'] = params['position'][2]
        params['width'] = params['size'][0]
        params['depth'] = params['size'][1]
        params['height'] = params['size'][2]
        rot = list(params.get('rotation',[0,0,0]))
        params['rot'] = [rot[0],rot[1],rot[2]]
        self.name = params.get('name', "untitled")
        self.data = self.data + list(params.items())
        self.data.append(('productParam', params))

    product_parse_args = parse_args

    def recreate_product_data(self, product, arg=None, data_functions=None):
        """create again data source for new send to service"""
        self.data = []
        if not arg:
            arg = product.arg
        if not data_functions:
            data_functions = product.data_functions
        self.parse_args(arg)
        self.data += [(name, func_data) for name, func_data in data_functions]
        log.info("Prepared data for next product creation.")

    product_recreate = recreate_product_data

    def finish(self, get_error=True):
        """send all data to server and return product back to user"""
        log.info("To create new product use func parse_args")
        name = self.name
        response = self.action(url="/products/create", data=self.data, method='POST')
        if get_error:
            error = self.action(url="/json/lasterror", convert=self.convert)
        else:
            error = None
        if error:
            if hasattr(error, "status"):
                raise Exception("Error cannot get real request. Maybe user is not logged raise_error is False?")
            msg = "Error in {} with parameter {}"
            raise Exception(msg.format([error['func_name']], [error['actual_error']]))
        else:
            log.info("Product created. Removing old data and returning new product")
            self.data = []
            response = self.get_product(name)
            return response

    product_finish = finish

    def make_funcs(self, actions, docs):
        """create all functions so it should be possible to use it as cabinet maker"""
        for key, value in actions:
            func = functools.partial(self.custom_action, method=key, **value)
            setattr(self, key, func)
        for key, value in docs:
            func = getattr(self, key)
            func.__doc__ = value


if __name__ == "__main__" :
    # api_generator()
    # import ocapi.api as oc
    import math
    
    def test_local():
        args = {'name':'test2', 'position':[0, 0, 0], 'size':[1000, 1000, 1000]}
        prod = CabinetMaker(args, host="localhost", port=2000, tls=False, login=False)
        for i in range(36):  # count through whole rotation
            size = [18, math.sin(math.radians(i * 10)) * 50 + 80, 18]  # change size
            rot = [0, 0, 10 + i * 2]  # rotate part
            prod.add_element(pos=[i * 20, 0, 0], size=size, rot=rot)
        print(prod.finish())
        print(prod.get_image())


    def test_local_get_calc():
        prod = CabinetMaker(None, host="localhost", port=2000, tls=False, login=False)
        prod.action("/system/new")
        prod.action("/orders/create?name=dva&info=Data&customer=Alfonz")
        args = {'name':'test2', 'position':[0, 0, 0], 'size':[1000, 1000, 1000]}
        prod.parse_args(args)
        for i in range(36):  # count through whole rotation
            size = [18, math.sin(math.radians(i * 10)) * 50 + 80, 18]  # change size
            rot = [0, 0, 10 + i * 2]  # rotate part
            prod.add_element(pos=[i * 20, 0, 0], size=size, rot=rot)
        data = list(prod.data)
        print(prod.finish())
        print(prod.get_calc(make_new=True))
        print(prod.get_image())

    def test_get_products():
        con = CabinetMaker(None, host="localhost", port=2000, tls=False, login=False)
        con.name = "dunt_51"
        prod = con.get_product()
        size = prod.size
        element = prod.elements['dunt_51_0_BOK']
        calc = element.calculation
        con.recreate_product_data(prod)
        con.custom_action(method="add_shape_cut", origin=None, tool_side='center', pos=None, number=4, joint='add_shape_cut_round', shape=True, radius=100, x_dist=100, tool_side_close='center', rot=None, size=None, tool_diameter=10, index=None, y_dist=100, process_type='acamProcessROUGH_FINISH', tool_number=1, final_depth=0, planes=None, save=True)
        prod = con.finish()
        con.recreate_product_data(prod)
        element = prod.elements['dunt_51_6_POL']
        dat = [{'type':'line', 'pos':[0, 20, 0], 'pos1':[element.sizeLength - 20, 20, 0]}, {'type':'line', 'pos':[element.sizeLength - 20, 20, 0], 'pos1':[element.sizeLength - 20, element.sizeWidth - 20, 0]}]
        con.custom_action(method="add_shape_cut", joint=dat, index='dunt_51_6_POL', shape=False, save=True)
        prod = con.finish()


    def test_change_product():
        args = {'edgeSIDE': ['Z', 0, 0, 0], 'thickConstr': 18, 'frontOut': False, 'socle': 0, 'matSteel': 'F509', 'matBack': '101', 'size': [600, 510, 900], 'style': 'FLAT', 'thickDrawer': 18, 'thickBack': 5, 'edgeDRAWER': ['X', 0, 0, 0], 'frame_width': 70, 'edgeTOP': ['Z', 0, 0, 0], 'matConstr': 'H3702', 'edges': True, 'elementInfo': {'fittings': {'KOL': 5}, 'production': {'EDGEBANDER': 2, 'HAND': 3, 'SAW': 1, 'COATING': False, 'CNC': 1}, 'group': 'dunt_17', 'visibility': 'NORMAL', 'block': True}, 'rotation': [0, 0, 0], 'matFront': 'H3702', 'product_type': 'product', 'name': 'dunt_17', 'position': [0, 0, 0], 'edgeDOOR': ['Z', 'Z', 'Z', 'Z']}
        con = CabinetMaker(args, host="localhost", port=2000, tls=False, login=False)
        con.add_basic(info=None, top_bars=None, variant='H', area_id=None, socle=None, back=5, diff=None, save=True)
        con.add_shelve(info=None, area_id=None, mat=None, number=None, diff=None, rotation=None, save=True, size=None)
        con.finish()
        prod = con.get_product()
        print(prod)
        con.recreate_product_data(prod)
        for i in [0, 1, 2, 3, 4]:
            el_name = prod.data[str(i)]
            element = prod.elements[el_name]
            thick = element.sizeThickness
            con.add_mod_element(index=i, sizeThickness=thick + 20)
        prod = con.finish()


    def test_change_product_2():
        args = {'edgeSIDE': ['Z', 0, 0, 0], 'thickConstr': 18, 'frontOut': False, 'socle': 0, 'matSteel': 'F509', 'matBack': '101', 'size': [600, 510, 900], 'style': 'FLAT', 'thickDrawer': 18, 'thickBack': 5, 'edgeDRAWER': ['X', 0, 0, 0], 'frame_width': 70, 'edgeTOP': ['Z', 0, 0, 0], 'matConstr': 'H3702', 'edges': True, 'elementInfo': {'fittings': {'KOL': 5}, 'production': {'EDGEBANDER': 2, 'HAND': 3, 'SAW': 1, 'COATING': False, 'CNC': 1}, 'group': 'dunt_17', 'visibility': 'NORMAL', 'block': True}, 'rotation': [0, 0, 0], 'matFront': 'H3702', 'product_type': 'product', 'name': 'dunt_17', 'position': [0, 0, 0], 'edgeDOOR': ['Z', 'Z', 'Z', 'Z']}
        con = CabinetMaker(args, host="localhost", port=2000, tls=False, login=False)
        for i in range(0, 40):
            con.add_element(number=1, pos=[0, 0, 0])
        con.finish()
        prod = con.get_product()
        print(prod)
        con.recreate_product_data(prod)
        for i in range(0, 40):
            el_name = prod.data[str(i)]
            element = prod.elements[el_name]
            thick = element.sizeThickness
            con.add_mod_element(index=i, elementRotation=[10 * i, 0, 0])
        prod = con.finish()

    def test_normal():
        args = {'name':'test2', 'position':[0, 0, 0], 'size':[1000, 1000, 1000]}
        prod = CabinetMaker(args, username="useroc1", password="oc1user1piff")
        for i in range(36):  # count through whole rotation
            size = [18, math.sin(math.radians(i * 10)) * 50 + 80, 18]  # change size
            rot = [0, 0, 10 + i * 2]  # rotate part
            prod.add_element(pos=[i * 20, 0, 0], size=size, rot=rot)
        print(prod.finish())
        print(prod.get_image())


    def test_bigger():
        args = {'edgeSIDE': ['Z', 0, 0, 0], 'thickConstr': 18, 'frontOut': False, 'socle': 0, 'matSteel': 'F509', 'matBack': '101', 'size': [600, 510, 900], 'style': 'FLAT', 'thickDrawer': 18, 'thickBack': 5, 'edgeDRAWER': ['X', 0, 0, 0], 'frame_width': 70, 'edgeTOP': ['Z', 0, 0, 0], 'matConstr': 'H3702', 'edges': True, 'elementInfo': {'fittings': {'KOL': 5}, 'production': {'EDGEBANDER': 2, 'HAND': 3, 'SAW': 1, 'COATING': False, 'CNC': 1}, 'group': 'dunt_71', 'visibility': 'NORMAL', 'block': True}, 'rotation': [0, 0, 0], 'matFront': 'H3702', 'product_type': 'product', 'name': 'dunt_71', 'position': [0, 0, 0], 'edgeDOOR': ['Z', 'Z', 'Z', 'Z']}
        dunt_71 = CabinetMaker(args, login=False, host="localhost", port=2000, tls=False)
        dunt_71.fce = 'product'
        dunt_71.add_side_left(info=None, area_id=None, mat=None, pos=None, diff=None, save=True, size=None)
        dunt_71.add_side_right(info=None, area_id=None, mat=None, pos=None, diff=[0, 0, 0, 0, 0, 400], save=True, size=None)
        dunt_71.add_top(info=None, area_id=None, mat=None, bars_width=None, pos=None, diff=[0, 400, 0, 0, 0, 0], save=True, size=None)
        dunt_71.add_base(info=None, area_id=None, mat=None, diff=None, save=True, size=None)
        dunt_71.add_dividers(info=None, area_id=None, array_dist=[1, 18], mat=None, part_size=None, thickness=None, diff=None, part=False, save=True, typ='B', areas=True)
        dunt_71.add_dividers(info=None, area_id=1, array_dist=[1, 400], mat=None, part_size=None, thickness=None, diff=[18, 0, 0, 0, 0, 0], part=False, save=True, typ='C', areas=True)
        dunt_71.add_element(area_id=3, mat=None, joints=None, number=None, pos=None, diff=None, typ='B', size=[580, 510, 18], info=None, size_override=False, name=None, rot=[0, -45, 0], edge=None, shape_contour=None, save=True)
        dunt_71.add_doors(area_id=None, handleHeight='DOWN', handle=True, mat=None, handleSize=[160, 25, 5], stacking='HORIZONTAL', number=1, door_type='AUTOMAT', diff=None, pars_front=[3, 3, 3, 3, 3], handleSide=None, info=None, style='FLAT', grains=True, post_diff=None, handleOrientation='HORIZONTAL', save=True, handlePos=[50, 50])
        dunt_71.add_shelve(info=None, area_id=None, mat=None, number=[400, 1], diff=None, rotation=None, save=True, size=None)
        dunt_71.add_empty(func_key='add_shape_cut', origin=2, tool_side='center', number=4, pos=None, joint='add_shape_cut_diag', shape=True, x_dist=400, tool_side_close='center', rot=None, size=None, tool_diameter=10, index=5, y_dist=400, process_type='acamProcessROUGH_FINISH', tool_number=1, final_depth=0, planes=None, save=True)
        dunt_71.finish()
    
    def test_closer():
        args = {'edgeSIDE': ['Z', 0, 0, 0], 'thickConstr': 18, 'frontOut': False, 'socle': 0, 'matSteel': 'F509', 'matBack': '101', 'size': [2000, 600, 2000], 'style': 'FLAT', 'thickDrawer': 18, 'thickBack': 5, 'edgeDRAWER': ['X', 0, 0, 0], 'frame_width': 70, 'edgeTOP': ['Z', 0, 0, 0], 'matConstr': 'H3702', 'edges': True, 'elementInfo': {'fittings': {'KOL': 5}, 'production': {'EDGEBANDER': 2, 'HAND': 3, 'SAW': 1, 'COATING': False, 'CNC': 1}, 'group': 'dunt_77', 'visibility': 'NORMAL', 'block': True}, 'rotation': [0, 0, 0], 'matFront': 'H3702', 'product_type': 'product', 'name': 'dunt_77', 'position': [0, 0, 0], 'edgeDOOR': ['Z', 'Z', 'Z', 'Z']}
        dunt_77 =CabinetMaker(args, login=False, tls=True)
        dunt_77.fce = 'product'
        dunt_77.add_bar(area_id=None, diff_Z=False, mat=None, diff_X=True, bar_width='X', locations=[0, 1], bar_length='Z', diff=[18, 18, 0, 0, 0, 0], size=120, info=None, name=None, grains=True, diff_Y=True, edge=None, post_diff=None, save=True)
        dunt_77.add_side_left(info=None, area_id=None, mat=None, pos=None, diff=None, save=True, size=None)
        dunt_77.add_side_right(info=None, area_id=None, mat=None, pos=None, diff=None, save=True, size=None)
        dunt_77.add_bar(area_id=None, diff_Z=False, mat=None, diff_X=False, bar_width='Y', locations=[0, 1], bar_length='X', diff=None, size=120, info=None, name=None, grains=True, diff_Y=True, edge=None, post_diff=None, save=True)
        dunt_77.add_dividers(info=None, area_id=None, array_dist=[5, 4, 5, 4, 5], mat=None, part_size=None, thickness=None, diff=None, part=True, save=True, typ='B', areas=True)
        dunt_77.add_shelve(info=None, area_id=[1, 3], mat=None, number=None, diff=None, rotation=None, save=True, size=None)
        dunt_77.add_dividers(info=None, area_id=[2], array_dist=[1, 1], mat=None, part_size=None, thickness=None, diff=None, part=True, save=True, typ='C', areas=True)
        dunt_77.add_dividers(info=None, area_id=[0], array_dist=[8, 1], mat=None, part_size=None, thickness=None, diff=None, part=True, save=True, typ='C', areas=True)
        dunt_77.add_dividers(info=None, area_id=[4], array_dist=[9, 9, 2], mat=None, part_size=None, thickness=None, diff=None, part=True, save=True, typ='C', areas=True)
        dunt_77.add_shelve(info=None, area_id=[6], mat=None, number=None, diff=None, rotation=None, save=True, size=None)
        dunt_77.add_drawers(info=None, area_id=5, save=True, handle=True, mat=None, grains=True, number=None, drawer_type='AUTOMAT', diff=None, pars_front=[3, 3, 39, 3, 3], mat_front=None, pars_in=[12, 12, 0, 40, 10, 40])
        dunt_77.add_doors(area_id=None, handleHeight='TOP', handle=False, mat=None, handleSize=[160, 25, 5], stacking='HORIZONTAL', number=[4, 3, 4], door_type='INSIDE', diff=[0, 0, -80, 0, 18, 18], pars_front=[3, 3, 3, 3, 3], handleSide=None, info=None, style='FLAT', grains=True, post_diff=None, handleOrientation='VERTICAL', save=True, handlePos=[50, 50])
        dunt_77.add_del_element(index=-2, save=True)
        dunt_77.add_doors(area_id=None, handleHeight='TOP', handle=False, mat=None, handleSize=[160, 25, 5], stacking='HORIZONTAL', number=[3, 4, 3], door_type='INSIDE', diff=[0, 0, -140, 0, 18, 18], pars_front=[3, 3, 3, 3, 3], handleSide=None, info=None, style='FLAT', grains=True, post_diff=None, handleOrientation='VERTICAL', save=True, handlePos=[50, 50])
        dunt_77.add_del_element(index=[-1, -3], save=True)
        dunt_77.finish()

    
    def test_count_base_elements():
        con = CabinetMaker(host="localhost", port=2000, tls=False, args=None, login=False)
        products = con.get_products()
        count = 0
        for prod in products.products:
            if prod.fce != "item":
                for name, element in prod.elements.items():
                    if name in prod.names['base']:
                        pos = [x + y for x, y in zip(element.elementPosition, element.product_position)]
                        if 50 < pos[2] <= 150:
                            count += 4
        ret = con.action(url="/db/nozicky/append")
        ret = con.action(url="/products/db_nozicky/edit", data={"quantity":count}, method="POST")
        pass
