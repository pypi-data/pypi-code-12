from flask import session
from flask_oauthlib.client import OAuth
from werkzeug.urls import url_parse, url_encode

oauth = OAuth()


weibo = oauth.remote_app(
    'weibo',
    request_token_params={'scope': 'email,statuses_to_me_read'},
    base_url='https://api.weibo.com/2/',
    authorize_url='https://api.weibo.com/oauth2/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.weibo.com/oauth2/access_token',
    content_type='application/json',
    app_key='WEIBO',
)


@weibo.tokengetter
def get_weibo_oauth_token():
    return session.get('weibo_token')


def change_weibo_header(uri, headers, body):
    auth = headers.get('Authorization')
    if auth:
        auth = auth.replace('Bearer', 'OAuth2')
        headers['Authorization'] = auth
    return uri, headers, body

weibo.pre_request = change_weibo_header


qq = oauth.remote_app(
    'qq',
    base_url='https://graph.qq.com',
    request_token_url=None,
    request_token_params={'scope': 'get_user_info'},
    access_token_url='/oauth2.0/token',
    authorize_url='/oauth2.0/authorize',
    app_key='QQ',
)


@qq.tokengetter
def get_qq_oauth_token():
    return session.get('qq_token')


def change_qq_header(uri, headers, body):
    return uri, headers, body

qq.pre_request = change_qq_header


douban = oauth.remote_app(
    'douban',
    base_url='https://api.douban.com/',
    request_token_url=None,
    request_token_params={'scope': 'douban_basic_common,shuo_basic_r'},
    access_token_url='https://www.douban.com/service/auth2/token',
    authorize_url='https://www.douban.com/service/auth2/auth',
    access_token_method='POST',
    app_key='DOUBAN',
)


@douban.tokengetter
def get_douban_oauth_token():
    return session.get('douban_token')


weixin = oauth.remote_app(
    'weixin',
    app_key='WEIXIN',
    request_token_params={'scope': 'snsapi_base'},
    base_url='https://api.weixin.qq.com',
    authorize_url='https://open.weixin.qq.com/connect/qrconnect',
    access_token_params={'grant_type': 'authorization_code'},
    access_token_url='/sns/oauth2/access_token',
    content_type='application/json',
)


@weixin.tokengetter
def get_weixin_oauth_token():
    return session.get('weixin_token')


def weixin_oauth(weixin):
    """Fixes the nonstandard OAuth interface of Tencent WeChat."""

    original_methods = {
        'authorize': weixin.authorize,
        'authorized_response': weixin.authorized_response,
    }

    def authorize(*args, **kwargs):
        response = original_methods['authorize'](*args, **kwargs)
        url = url_parse(response.headers['Location'])
        args = url.decode_query()

        args['appid'] = args.pop('client_id')
        url = url.replace(query=url_encode(args), fragment='wechat_redirect')

        response.headers['Location'] = url.to_url()
        return response

    def authorized_response(*args, **kwargs):
        original_access_token_params = weixin.access_token_params
        weixin.access_token_params = {
            'appid': weixin.consumer_key,
            'secret': weixin.consumer_secret,
        }
        response = original_methods['authorized_response'](*args, **kwargs)
        weixin.access_token_params = original_access_token_params
        return response

    weixin.authorize = authorize
    weixin.authorized_response = authorized_response

    return weixin

weixin = weixin_oauth(weixin)
