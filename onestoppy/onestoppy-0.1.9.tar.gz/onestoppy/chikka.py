import consul, requests, logging, os, sys
c = consul.Consul(host='consul.service.onestop')
index, data = c.kv.get('global/config/common/chikka/client_id')
client_id = data['Value']

index, data = c.kv.get('global/config/common/chikka/secret_key')
secret_key = data['Value']

index, data = c.kv.get('global/config/common/chikka/url')
sms_url = data['Value']

proxies = {
    'http': 'http://proxy.query.onestop:3128',
    'https': 'http://proxy.query.onestop:3128'
}

def reply_chikka_sms(mobile_number, message, shortcode, request_id='', request_cost='FREE'):
    logging.info("Sending SMS REPLY to %s with message via Chikka:\n%s\n(Chikka Req: %s)" % (mobile_number, message, request_id))

    message_id=os.urandom(16).encode("hex")

    payload = {
        "message_type": "REPLY",
        "mobile_number": mobile_number,
        "shortcode": shortcode,
        "request_id": request_id,
        "message_id": message_id,
        "message": message + "\n", # append a new line because Chikka appends 'This message is free.' to the end of each message
        "request_cost": request_cost,
        "client_id": client_id,
        "secret_key": secret_key
    }

    result = requests.post(sms_url, data=payload)

    data = None
    try:
        data = result.json()
    except:
        logging.error("Chikka error, can't decode (%s) JSON response: %s" % (result.response_code, result.text))
        return False

    if result.status_code != 200:
        logging.error("Chikka error: %s (%s) [%s] for send SMS request to %s" % (data['status'], data['message'], data['description'], mobile_number))
        return False

    # if the status code is 200, then the result should be: {"status": 200, "message": "ACCEPTED"}
    if data['message'] != 'ACCEPTED':
        logging.error("Chikka error, got 200 result, but status message not accepted, Status [%s]" % data['message'])
        return False

    logging.info("Chikka message sent and accepted to %s" % mobile_number)

    return True


def send_chikka_sms(mobile_number, message, shortcode):
    logging.info("Sending SMS to %s with message via Chikka:\n%s" % (mobile_number, message))
    message_id=os.urandom(16).encode("hex")

    payload = {
        "message_type": "SEND",
        "mobile_number": mobile_number,
        "shortcode": shortcode,
        "message_id": message_id,
        "message": message + "\n", # append a new line because Chikka appends 'This message is free.' to the end of each message
        "client_id": client_id,
        "secret_key": secret_key
    }

    result = requests.post(sms_url, data=payload, proxies=proxies)

    data = None
    try:
        data = result.json()
    except:
        logging.error("Chikka error, can't decode (%s) JSON response: %s" % (result.response_code, result.text))
        return False

    if result.status_code != 200:
        logging.error("Chikka error: %s (%s) [%s] for send SMS request to %s" % (data['status'], data['message'], data['description'], mobile_number))
        return False

    # if the status code is 200, then the result should be: {"status": 200, "message": "ACCEPTED"}
    if data['message'] != 'ACCEPTED':
        logging.error("Chikka error, got 200 result, but status message not accepted, Status [%s]" % data['message'])
        return False

    logging.info("Chikka message sent and accepted to %s" % mobile_number)

    return True

