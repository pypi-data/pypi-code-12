import json
from datetime import datetime
from klein import Klein
from twisted.internet.defer import inlineCallbacks, returnValue

from .tools import encrypt_password, verify_password, encode_token
from .config import RETRIEVE_USER_RPC, REGISTER_USER_RPC, TOKEN_VALIDITY, CORS_ORIGIN


class Response400(Exception):
    pass


def _retreive_content(request):
    try:
        body = json.loads(request.content.read().decode())
    except ValueError:
        raise Response400('Invalid JSON body.')
    login = body.get('login')
    password = body.get('password')
    if type(login) is not str or type(password) is not str:
        raise Response400('Missing or invalid login and/or password.')
    return login, password, body


def _set_cors_headers(request):
    request.setHeader(b'Access-Control-Allow-Origin', CORS_ORIGIN)
    request.setHeader(b'Access-Control-Allow-Headers', b'accept, content-type')
    request.setHeader(b'Access-Control-Allow-Method', b'POST, OPTIONS')


def _create_token(login):
    exp = datetime.utcnow().timestamp() + TOKEN_VALIDITY
    return encode_token({'login': login, 'exp': exp})


def rest_api_factory(wamp_session):

    klein_app = Klein()

    @klein_app.handle_errors(Response400)
    def response_400(request, failure):
        request.setResponseCode(400)
        return json.dumps({'message': str(failure.value)})

    @klein_app.route('/login', methods=['POST', 'OPTIONS'])
    @inlineCallbacks
    def login(request):
        _set_cors_headers(request)
        if request.method == b'OPTIONS':
            return
        login, password, body = _retreive_content(request)
        user = yield wamp_session.call(RETRIEVE_USER_RPC, login)
        if (not user or not user.get('hashed_password') or
                not verify_password(password, user['hashed_password'])):
            raise Response400('Unknown user or invalid password')
        returnValue(json.dumps({'login': login, 'token': _create_token(login)}))

    @klein_app.route('/signin', methods=['POST', 'OPTIONS'])
    @inlineCallbacks
    def signin(request):
        _set_cors_headers(request)
        if request.method == b'OPTIONS':
            return
        login, password, body = _retreive_content(request)
        hashed_password = encrypt_password(password)
        user = yield wamp_session.call(REGISTER_USER_RPC, login, hashed_password, body)
        if not user:
            raise Response400("Couldn't create user")
        returnValue(json.dumps({'login': login, 'token': _create_token(login)}))

    # @klein_app.route('/login/github')
    # @inlineCallbacks
    # def login_github(request):
    #   pass

    return klein_app
