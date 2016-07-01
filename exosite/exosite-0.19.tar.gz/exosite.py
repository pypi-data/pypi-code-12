#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import readline
import urllib3
import json
import argparse
import getpass
import requests
import mimetypes
import hashlib
import binascii
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from distutils.version import LooseVersion
from multiprocessing.dummy import Pool as ThreadPool

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()

session = requests.Session()

# Python 2 + 3 support
try:
    input = raw_input
except NameError:
    pass

# srv_host = "biz-internal-api-dev.exosite.biz"
srv_host = "bizapi.hosted.exosite.io"
pool = ThreadPool(4)


SECRET_FILE = '.Solutionfile.secret'
CONFIG_FILE = 'Solutionfile.json'
VERSION = '0.19'
FORMAT_VERSION = '0.2'

PUB_CONF_DESC = {
    "custom_api": ["Custom api file: ", "sample_api.js"],
    "file_dir": ["Static file directory: ", "public"],
    "default_page": ["Default page: ", "index.html"]
}

def tohex(str):
    return binascii.hexlify(str)

def sha1(fname):
    hasher = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(tohex(chunk))
    return hasher.hexdigest()

def line_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def get_config(file):
    try:
        with open(file, 'r') as fh:
            content = fh.read()
            try:
                return json.loads(content)
            except Exception:
                print("Config file '{0}' is invalid json".format(file))
                sys.exit(0)
    except IOError:
        print("Config file '{0}' not exist".format(file))
        sys.exit(0)


# Prompt user to pick from a list of dict items,
# assuming the first column key is a unique ID
def pick_from_list(promptText, items, keys, headings):
    # assume first key is the one we need to fill in]
    id_key = keys[0]

    # display available products
    maxwidths = dict([(k, max([len(item[k]) for item in items] +
                              [len(h)]))
                      for (k, h) in zip(keys, headings)])
    print('\n' + ' | '.join([headings[i].ljust(maxwidths[k])
                      for (i, k) in enumerate(keys)]))
    for item in items:
        item['display_meta'] = ' | '.join([item[k] for k in keys[1:]])
        print(' | '.join([item[k].ljust(maxwidths[k]) for k in keys]))

    class ItemCompleter(Completer):
        def get_completions(self, document, complete_event):
            for item in items:
                for k in keys[:2]:
                    if item[k][:len(document.text)] == document.text:
                        yield Completion(
                            item[id_key],
                            start_position=-len(document.text),
                            display_meta=item['display_meta'])

    selected_item = None
    while selected_item is None:
        item_id = prompt(promptText, completer=ItemCompleter())
        matches = list(filter(lambda p: p[id_key] == item_id, items))
        if len(matches) == 1:
            selected_item = matches[0]
        else:
            print('Found {0} matches for "{1}". Try again.'.format(
                len(matches), item_id))
    return selected_item


def init_credential():
    private = {}
    print("Please log in with your Murano email and password, and " +
          "\nchoose an existing solution ID and product ID.")
    private["email"] = line_input("Email: ")
    private["password"] = getpass.getpass()
    sys.stdout.write("Testing those credentials... ")
    token = get_token(host, private['email'], private['password'])
    if token is None:
        print(
            "Unable to log in with those credentials. Be sure to \npass \
            --host if you're working with a development server"
        )
    else:
        print("OK")

    # get user's business memberships
    user = User(host, token, private["email"])
    businesses = user.get_businesses()

    # get user's solutions in all businesses
    solutions = []
    for b in businesses:
        # filter out non-Murano solutions
        bizsolutions = [s for s in user.get_solutions(b['bizid'])
                        if s['type'] == 'dataApi']
        for p in bizsolutions:
            p.update({'bizname': b['name']})
        solutions = solutions + bizsolutions

    solution = pick_from_list('Solution ID: ',
                              solutions,
                              ('apiId', 'domain', 'bizname'),
                              ('Solution ID', 'Domain', 'Business'))
    private['solution_id'] = solution['apiId']

    # get user's products in the business of the selected solution
    products = user.get_products(solution['bizid'])
    for p in products:
        p.update({'bizname': solution['bizname']})

    product = pick_from_list('Product ID: ',
                             products,
                             ('modelId', 'label', 'bizname'),
                             ('Product ID', 'Label', 'Business'))
    private['product_id'] = product['modelId']

    try:
        with open(SECRET_FILE, "w") as fh:
            fh.write(json.dumps(private))
        os.chmod(SECRET_FILE, 0o600)
        print("Successfully created credential file '{0}'. ".format(SECRET_FILE) +
              "To deploy your solution, run 'exosite --deploy'.")
    except Exception as e:
        print("Unable to generate credential: {0}".format(str(e)))


def get_token(host, email, password):
    srv_url = host + '/token/'
    try:
        resp = session.post(
            srv_url,
            headers = {'Content-Type': 'application/json'},
            json = {"email": email, "password": password}
        )
        resp.raise_for_status()
        return resp.json()['token']
    except Exception as e:
        print("Unexpected exception: {0}".format(str(e)))
    return None

class Product:
    def __init__(self, host, token, product_id):
        self.token = token
        self.host = host
        self.product_id = product_id
        self.session = session
        self.session.headers.update({
            "content-type": "application/json",
            "authorization": "token " + self.token
        })

    def sn_enable(self, sn):
        ret = self.session.post(self.host + '/product/' + self.product_id + "/device/" + sn)
        ret.raise_for_status()
        return ret.json()

class User:
    def __init__(self, host, token, email):
        self.host = host
        self.token = token
        self.session = session
        self.email = email
        self.session.headers.update({
            "content-type": "application/json",
            "authorization": "token " + self.token
        })

    def get_businesses(self):
        ret = session.get(self.host + "/user/" + self.email + "/membership/")
        ret.raise_for_status()
        return ret.json()

    def get_products(self, bizid):
        ret = session.get(self.host + "/business/" + bizid + "/product/")
        ret.raise_for_status()
        return ret.json()

    def get_solutions(self, bizid):
        ret = session.get(self.host + "/business/" + bizid + "/solution/")
        ret.raise_for_status()
        return ret.json()

class Solution:

    def __init__(self, host, token, solution_id):
        self.token = token
        self.host = host
        self.solution_id = solution_id
        self.session = session
        self.session.headers.update({
            "content-type": "application/json",
            "authorization": "token " + self.token
        })


    def url(self, append = ''):
        return self.host + "/solution/" + self.solution_id + append
    def request(self, method, append = '', **kwargs):
        # print(self.url(append))
        r = self.session.request(method, self.url(append), **kwargs)

        if r.status_code >= 400:
            print(" Request:  {0} \n failed with status: {1} \n Request: \n {2} \n Response: \n {3}".format(self.url(append), r.status_code, kwargs, r.text))

        r.raise_for_status()
        if r.text == "":
            return r.status_code
        else:
            # print(json.dumps(r.json()))
            return r.json()
    def get(self, append = '', **kwargs):
        return self.request('get', append, **kwargs)
    def put(self, append = '', **kwargs):
        return self.request('put', append, **kwargs)
    def post(self, append = '', **kwargs):
        return self.request('post', append, **kwargs)
    def delete(self, append = '', **kwargs):
        return self.request('delete', append, **kwargs)


    def version(self):
        return self.get('/version')

    def list_endpoints(self):
        return self.get('/endpoint')

    def create_endpoint(self, endpoint):
        resp = self.post('/endpoint', json=endpoint)
        print("  {0} {1} {2}".format(endpoint["method"], endpoint["path"], json.dumps(resp)))

    def delete_endpoint(self, id):
        sys.stdout.write('.')
        sys.stdout.flush()
        return self.delete('/endpoint/' + id)

    def update_custom_api(self, script_file):
        print('  Fetching endpoint list')
        existing_endpoints = {}
        for endpoint in self.list_endpoints():
            existing_endpoints[endpoint['method'] + endpoint['path']] = endpoint

        try:
            with open(script_file, 'r') as fh:
                content = fh.read()
        except IOError:
            print("Custom script file '{0}' not exist".format(script_file))
            sys.exit(0)
        new_endpoints = {}
        for snippet in content.split('--#ENDPOINT '):
            raw = snippet.strip()
            if len(raw) == 0:
                continue

            signature, script = raw.split('\n', 1)
            method, path = signature.split(' ')
            path = path.strip()
            endpoint = {
                'method': method,
                'path': path,
                'script': script,
            }
            key = method.lower() + path.lower()
            if key in existing_endpoints and existing_endpoints[key]['script'] == script:
                del existing_endpoints[key]
            else:
                new_endpoints[key] = endpoint

        if len(existing_endpoints) > 0:
            sys.stdout.write('  Deleting old endpoints')
            pool.map(lambda k: self.delete_endpoint(existing_endpoints[k]['id']), existing_endpoints)
            print("")
        pool.map(lambda k: self.create_endpoint(new_endpoints[k]), new_endpoints)
        return list(new_endpoints.keys()) + list(existing_endpoints.keys())

    def list_files(self):
        return self.get('/file')

    def delete_file(self, path):
        sys.stdout.write('.')
        sys.stdout.flush()
        return self.delete('/file' + path)

    def upload_files(self, assets):
        existing_files = {}
        for asset in self.list_files():
            existing_files[asset['path']] = asset

        new_assets = {}
        for asset in assets:
            key = asset['path']
            if key in existing_files:
                if (existing_files[key]['checksum'] != asset['checksum'] or
                    existing_files[key]['mime_type'] != asset['mime_type']):
                    new_assets[key] = asset
                del existing_files[key]
            else:
                new_assets[key] = asset

        if len(existing_files) > 0:
            sys.stdout.write('  Deleting old assets')
            pool.map(lambda k: self.delete_file(existing_files[k]['path']), existing_files)
            print("")
        pool.map(lambda k: self.upload_file(new_assets[k]), new_assets)
        return list(new_assets.keys()) + list(existing_files.keys())

    def upload_file(self, asset):
        resp = self.put(
            "/fileupload" + asset['path'],
            files={"file": (asset['name'], open(asset['full_path'], 'rb'), asset['mime_type'])},
            headers={"content-type": None}
        )
        print("  {0} {1} {2}".format(asset['path'], asset['checksum'], json.dumps(resp)))

    def upload_productid(self, pid):
        item = self.get_product_serviceconfig()
        if item is not None:
            item["triggers"] = {"pid": [pid], "vendor": [pid]}
            return self.put(
                "/serviceconfig/" + item["id"],
                json = item
            )
        return "serviceconfig not found"

    def get_product_serviceconfig(self):
        resp = self.get("/serviceconfig/")
        items = resp["items"]
        for item in items:
            if item["service"] == "device":
                return self.get("/serviceconfig/" + item["id"])
        return None

    def update_service(self, type, name, content):
        try:
            return self.put(
              "/" + type + "/" + self.solution_id + "_" + name,
               json = content
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return self.post(
                  "/" + type + "/",
                  json = content
                )
            else:
                raise(err)

    def update_module(self, module, content):
        resp = self.update_service('library', module, {
            "name": module,
            "solution_id": self.solution_id,
            "script": content
        })
        print("  {0} {1}".format(module, json.dumps(resp)))

    def update_eventhandler(self, service, event, content):
        resp = self.update_service(
            'eventhandler', service + "_" + event, {
                "service": service,
                "event": event,
                "solution_id": self.solution_id,
                "script": content
            }
        )
        print("  {0} {1} {2}".format(service, event, json.dumps(resp)))

    def get_solution(self):
        return self.get()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Deploy Solution to Exosite Murano')
    parser.add_argument('--host', nargs='?', default=srv_host)
    parser.add_argument("-k", "--insecure", dest="secured",
                        required=False, action='store_false',
                        help='Ignore SSL')
    parser.add_argument("-p", "--upload_productid", required=False,
                        action='store_true', help='Upload static file')
    parser.add_argument("-s", "--upload_static", required=False,
                        action='store_true', help='Upload static file')
    parser.add_argument("-a", "--upload_api", required=False,
                        action='store_true', help='Upload api')
    parser.add_argument("-e", "--upload_eventhandler", required=False,
                        action='store_true', help='Upload event handler')
    parser.add_argument("-m", "--upload_modules", required=False,
                        action='store_true', help='Upload modules')
    parser.add_argument("--enable_sn", required=False)
    parser.add_argument("--deploy", required=False, action='store_true',
                        help='Upload all solution configurations')
    parser.add_argument("--init", required=False, action='store_true',
                        help='Configure for credential parameters')
    parser.add_argument("-v", "--version", required=False,
                        action='store_true', help='Show Version number')
    parser.set_defaults(secured=True)
    args = parser.parse_args()

    host = "https://" + args.host + "/api:1"
    verify_ssl = args.secured

    if args.version:
        print("exosite cli version: " + VERSION)
        sys.exit(0)

    # init private credential
    if args.init:
        init_credential()
        sys.exit(0)

    if not os.path.isfile(SECRET_FILE):
        print(
            "No credential file found, please run with --init to " +
            "generate secret configuration."
        )
        sys.exit(0)

    args.upload_api = args.upload_api or args.deploy
    args.upload_static = args.upload_static or args.deploy
    args.upload_modules = args.upload_modules or args.deploy
    args.upload_eventhandler = args.upload_eventhandler or args.deploy
    args.upload_productid = args.upload_productid or args.deploy

    if not (args.upload_api or args.upload_static or args.upload_modules or
            args.upload_eventhandler or args.upload_productid or
            args.enable_sn):
        print("One option of -a, -s, -e, -m, -p, --enable_sn or --deploy must be set")
        sys.exit(0)

    private = get_config(SECRET_FILE)
    # public configuration
    public = {}
    if not os.path.isfile(CONFIG_FILE):
        public['version'] = FORMAT_VERSION
        for key in PUB_CONF_DESC.keys():
            item = PUB_CONF_DESC[key]
            public[key] = line_input(item[0], item[1])
        fh = open(CONFIG_FILE, "w")
        fh.write(json.dumps(public))
        print("Configuration file '{0}' is created".format(CONFIG_FILE))
    else:
        public = get_config(CONFIG_FILE)
        changed = False
        for key in PUB_CONF_DESC.keys():
            item = PUB_CONF_DESC[key]
            if key not in public:
                public[key] = line_input(item[0], item[1])
                changed = True
        if changed:
            fh = open(CONFIG_FILE, "w")
            fh.write(json.dumps(public))
    # print(public, private)

    solution_id = private['solution_id']
    product_id = private['product_id']

    if 'version' in public:
        version = public['version']
    else:
        version = '0.1'

    if LooseVersion(version) > LooseVersion(FORMAT_VERSION):
        print(
            "Solutionfile format version {0} is not supported by this ".
            format(version) +
            "version of the exosite murano tool. Please update using: \n" +
            "pip install exosite --upgrade"
        )
        exit(0)

    custom_api = public['custom_api']
    file_dir = public['file_dir']
    default_page = public['default_page']

    # get token
    token = get_token(host, private['email'], private['password'])
    if not token:
        print(
            "Username/Password is not valid for server '{0}', please ".
            format(host) +
            "update credential file or run with --init option "
        )
        exit(0)

    # get config
    napi = Solution(host, token, solution_id)

    version_info = napi.version()

    if LooseVersion(version_info['min_cli_version']) > LooseVersion(VERSION):
        print(
            "This version of the exosite murano tool is outdated. Please update: \n" +
            "pip install exosite --upgrade"
        )
        sys.exit(0)

    if args.enable_sn:
        print("Enable new serial number...")
        prod = Product(host, token, product_id)
        print("  {0} {1}".format(product_id, prod.sn_enable(args.enable_sn)))
        sys.exit(0)

    if args.upload_productid:
        print("Assigning product id...")
        print("  {0} {1}".format(product_id, napi.upload_productid(product_id)))

    if args.upload_eventhandler:
        print("Updating event handlers...")
        if 'event_handler' in public:
            event_handlers = public['event_handler']
            for service in event_handlers:
                for event in event_handlers[service]:
                    with open(event_handlers[service][event], 'r') as fh:
                        content = fh.read().replace("$PRODUCT_ID", product_id)
                    napi.update_eventhandler(service, event, content)
        else:
            print("no event handlers found!")

    if args.upload_modules:
        print("Updating modules...")
        if 'modules' in public:
            modules = public['modules']
            for modulename in modules:
                with open(modules[modulename], 'r') as fh:
                    content = fh.read().replace("$PRODUCT_ID", product_id)
                napi.update_module(modulename, content)
        else:
            print("no modules found!")
    # update custom api
    if args.upload_api:
        print("Updating custom api...")
        updates = napi.update_custom_api(custom_api)
        if 'custom_api_hook' in public:
            key = 'get/'+public['custom_api_hook']
            if key in updates:
                print("  Executing init call")
                init_url = "https://{0}/{1}".format(
                    napi.get_solution()['domain'],
                    public['custom_api_hook'])
                print("    GET " + init_url + " " + str(session.get(init_url)))

    # upload static file
    if args.upload_static:
        print("Updating static files...")
        assets = []
        for root, dirs, files in os.walk(file_dir):
            for name in files:
                full_path = os.path.join(root, name)
                checksum = sha1(full_path)
                if name == default_page:
                    target_path = '/'
                else:
                    target_path = full_path[len(file_dir):]
                (mime_type, encoding) = mimetypes.guess_type(full_path)
                if mime_type is None:
                    mime_type = 'application/binary'
                assets.append({
                    'full_path': full_path,
                    'checksum': checksum,
                    'mime_type': mime_type,
                    'name': name,
                    'path': target_path,
                })
        napi.upload_files(assets)
        # pool.map(lambda a: napi.upload_file(*a), assets)

    print(
        "\nSolution URL: https://{0}\n".format(napi.get_solution()['domain'])
    )
