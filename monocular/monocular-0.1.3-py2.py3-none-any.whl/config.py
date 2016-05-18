config = {
    'version': '0.1.3',
    'client_id': '',
    'client_secret': '',
    'refresh_token': '',
    'access_token': '',
    'expires_in': '',
    'issued_at': '',
    'base_url': 'https://monocular.jemsoft.io/api'
}

def get(key):
    return config[key]

def set(key, value):
    config[key] = value
