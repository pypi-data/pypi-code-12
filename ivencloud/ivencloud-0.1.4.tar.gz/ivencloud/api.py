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
isFreqSet = False


def activate_device(secret_key, device_uid):
    if device_uid is not None and isinstance(device_uid, str) and \
                    secret_key is not None and isinstance(secret_key, str) and \
            bool(device_uid) and bool(secret_key):
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
        if isinstance(datas, dict) and bool(datas):
            headers = {'API-KEY': api_key, 'Content-Type': "application/json"}
            payload = {"data": []}
            payload['data'].append(datas)
            if isFreqSet:
                # TODO: need to change
                payload['data'].append({"task": 0})
            r = requests.post(data_url, data=json.dumps(payload), headers=headers) # add null check
            ir = IvenResponse()
            ir.status = r.status_code
            if r.status_code < 500 and 'application/json' in r.headers['Content-Type']:
                j = r.json()
                if 'description' in j:
                    ir.description = j['description']
                if 'ivenCode' in j:
                    ir.iven_code = j['ivenCode']
                if 'task' in j:
                    if j['ivenCode'] == 10180:  # change this
                        global freq
                        freq = j['task']
                if 'message' in j:
                    ir.message = j['message']
                    if 'UPDATE_REQUIRED' in ir.message:
                        ir.need_firm_update = True
                    if 'CONFIGURATION_UPDATE_REQUIRED' in ir.message:
                     ir.need_conf_update = True
            return ir
        else:
            # datas is NULL or not valid format
            return [None, 1]
    else:
        # Api key is not set
        return [None, 2]


def send_data_wloop(data, frequency, callback):
    if set_frequency(frequency) is True:
        global break_loop
        while break_loop is False:
            if api_key is not None and data is not None:
                ir = send_data(data)
                callback(ir)
                sleep(freq)
        break_loop = False
        return True
    return False


def set_frequency(_freq):
    if _freq > 0:
        global freq
        freq = _freq
        return True
    return False


def break_sendloop():
    global break_loop
    break_loop = True

