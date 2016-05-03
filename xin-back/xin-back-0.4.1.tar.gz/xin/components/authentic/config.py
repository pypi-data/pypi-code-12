from os import environ


SECRET_KEY = environ.get('SECRET_KEY', 'secret_for_test_only!')
REGISTER_USER_RPC = environ['AUTHENTIC_REGISTER_USER_RPC']
RETRIEVE_USER_RPC = environ['AUTHENTIC_RETRIEVE_USER_RPC']
LISTEN_PORT = environ.get('AUTHENTIC_LISTEN_PORT', 8081)
TOKEN_VALIDITY = environ.get('AUTHENTIC_TOKEN_VALIDITY', 7 * 24 * 3600)
CORS_ORIGIN = environ.get('AUTHENTIC_CORS_ORIGIN', '*').encode()
