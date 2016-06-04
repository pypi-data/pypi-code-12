
from flask import Flask, Response, json

app = Flask('system-status-server')

from .uptimeprovider import UptimeProvider
from .loadprovider import LoadProvider
from .cpuprovider import CPUProvider
from .memoryprovider import MemoryProvider
from .hddprovider import HDDProvider

providers = []

providers.append(UptimeProvider())
providers.append(LoadProvider())
providers.append(CPUProvider())
providers.append(MemoryProvider())
providers.append(HDDProvider())

@app.route('/', methods = ['GET'])
def index():

    data = dict()

    for provider in providers:
        data.update(provider.fetch())

    resp = Response(json.dumps(data))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
