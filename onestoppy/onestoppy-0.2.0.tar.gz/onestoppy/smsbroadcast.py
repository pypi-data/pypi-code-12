import consul, requests
proxies = {
    'http': 'http://proxy.query.onestop:3128',
    'https': 'http://proxy.query.onestop:3128'
}

c = consul.Consul(host='consul.service.onestop')

index, data = c.kv.get('global/config/common/smsbroadcast/username')
sms_username = data['Value']

index, data = c.kv.get('global/config/common/smsbroadcast/username')
sms_username = data['Value']

index, data = c.kv.get('global/config/common/smsbroadcast/password')
sms_password = data['Value']

index, data = c.kv.get('global/config/common/smsbroadcast/url')
sms_url = data['Value']

def send(to, message, from_number=None, source=None):
    payload = {
        'username': sms_username,
        'password': sms_password,
        'source': source,
        'from': from_number,
        'to': to,
        'message': message }

    result = requests.post(sms_url, data=payload, proxies=proxies)

    if result.status_code == 200:
        return True

    return False

