""" iven cloud api """
from hashlib import sha1
import hmac
import requests
import json
from models import IvenResponse
from time import sleep

callback_fxn = None
activation_url = "http://demo.iven.io/activate/device"
data_url = "http://demo.iven.io/data"
api_key = None
break_loop = False
freq = 0
loop_data = None


def activate_device(secret_key, device_uid):
    if device_uid is not None and secret_key is not None:
        global api_key
        hashed = hmac.new(secret_key, device_uid, sha1)
        activation_code = hashed.digest().encode("hex")
        headers = {'Activation': activation_code, 'Content-Type': "application/json"}
        r = requests.get(activation_url, headers=headers)
        ir = IvenResponse()
        ir.status = r.status_code
        if r.status_code < 500 and 'application/json' in r.headers['Content-Type']:
            j = r.json()
            if 'api_key' in j:
                api_key = j['api_key']
                ir.api_key = api_key  # this may be wrong reference garbage collector wont delete
            if 'description' in j:
                ir.description = j['description']
            if 'device_uid' in j:
                ir.device_uid = j['device_uid']
            if 'ivenCode' in j:
                ir.iven_code = j['ivenCode']
        return ir
    else:
        return None


def send_data(datas):
    if api_key is not None:
        headers = {'API-KEY': api_key, 'Content-Type': "application/json"}
        payload = {'data': [{'dataArray': [], 'at': 'now'}]}

        for key, value in datas.iteritems():
            payload['data'][0]['dataArray'].append({key: value})

        r = requests.post(data_url, data=json.dumps(payload), headers=headers)
        ir = IvenResponse()
        ir.status = r.status_code
        if r.status_code < 500 and 'application/json' in r.headers['Content-Type']:
            j = r.json()
            if 'description' in j:
                ir.description = j['description']
            if 'ivenCode' in j:
                ir.iven_code = j['ivenCode']
            if 'message' in j:
                ir.message = j['message']
                if 'UPDATE_REQUIRED' in ir.message:
                    ir.need_firm_update = True
                if 'CONFIGURATION_UPDATE_REQUIRED' in ir.message:
                    ir.need_conf_update = True
        return ir


def send_data_wloop(callback):
    while break_loop is False:
        if api_key is not None and loop_data is not None:
            headers = {'API-KEY': api_key, 'Content-Type': "application/json"}
            payload = {'data': [{'dataArray': [], 'at': 'now'}]}

            for key, value in loop_data.iteritems():
                payload['data'][0]['dataArray'].append({key: value})

            r = requests.post(data_url, data=json.dumps(payload), headers=headers)
            ir = IvenResponse()
            ir.status = r.status_code
            if r.status_code < 500 and 'application/json' in r.headers['Content-Type']:
                j = r.json()
                if 'description' in j:
                    ir.description = j['description']
                if 'ivenCode' in j:
                    ir.iven_code = j['ivenCode']
                if 'message' in j:
                    ir.message = j['message']
                    if 'UPDATE_REQUIRED' in ir.message:
                        ir.need_firm_update = True
                    if 'CONFIGURATION_UPDATE_REQUIRED' in ir.message:
                        ir.need_conf_update = True
            callback(ir)
            sleep(freq)
        if loop_data is None:
            callback(None)


def set_data_tosend(datas):
    global loop_data
    loop_data = datas


def set_frequency(_freq):
    global freq
    freq = _freq


def break_sendloop():
    global break_loop
    break_loop = True

