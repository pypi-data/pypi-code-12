#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : wechat.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年04月19日 星期二 14时39分05秒
# *************************************************

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

import requests

from django.shortcuts import redirect
from django.views.generic import View
from django.conf import settings

from .models import WechatWebModel

from .response import Response

class WechatWeb:
    '''
    Doc: Wechat Web Develop
    
    @param request      Request Object
    @param appid        Appid       
    @param appsecret    App Secret  
    @param redirect_uri In Project settings.WECHAT or request.GET
    @param scope        snsapi_base or snsapi_userinfo
    @param code         From wechat Redirect
    @param state        Any to redirect_uri/?code=CODE&state=STATE

    Methods:
        One: for Step One, redirect uri
            @param appid
            @param redirect_uri
            @param scope            default='snsapi_base'
        
        Two: for Step 2/3/4, openid and userinfo
            @param appid
            @param appsecret
            @param request
            @param code     in request.GET
    '''
    def __init__(self, appid, appsecret=None, request=None,
                redirect_uri=None, scope='snsapi_base',
                code=None, state='STATE'):
        self._appid = appid
        self._appsecret = appsecret
        # self._redirect_uri = quote(redirect_uri)
        self._redirect_uri = quote(redirect_uri, safe='') if redirect_uri else None
        self._scope = scope
        self._code = request.GET.get('code', None)
        self._state = state
        self._request = request

        # ACCESS_TOKE, openid ...
        self._data = None 
        # part of _get_data
        self._access_token = None
        self._expires_in = None
        self._refresh_token = None
        self._openid = None
        # self._scope = None
        self._lang = 'zh_CN'

        # User data
        self._user_data = None
        # part of User data
        self._nickname = None
        self._sex = None
        self._province = None
        self._city = None
        self._country = None
        self._headimgurl = None
        self._privilege = None
        self._unionid = None

        # Django Session Data
        self._session = None

    def _get_user_data_with_openid(self):
        assert self._request != None
        assert 'openid' in self._request.session
        
        self._openid = self._request.session.get('openid')
        wb = WechatWebModel.objects.get(openid=self._openid)
        self._user_data = {
            'openid': self._openid,
            'nickname': wb.nickname,
            'sex': wb.sex,
            'province': wb.province,
            'city': wb.city,
            'country': wb.country,
            'headimgurl': wb.headimgurl,
            'privilege': wb.privilege,
            'unionid': wb.unionid
        }

    def _set_session(self):
        # Step 2/3/4
        #   request cannot be not
        assert self._request != None
        assert self._openid != None

        self._request.session['openid'] = self._openid

    def authenticate(self):
        '''
            Step 1: 用户同一授权, 获取code
        '''
        assert self._redirect_uri != None
        assert self._scope != None
        assert self._state != None

        if self._scope not in ('snsapi_base', 'snsapi_userinfo'):
            raise ValueError('Invalid Scope. Scope must be snsapi_base or snsapi_userinfo')

        return redirect(
            'https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}&state={STATE}#wechat_redirect'
            .format(
                APPID=self._appid,
                REDIRECT_URI=self._redirect_uri,
                SCOPE=self._scope,
                STATE=self._state
            )
        )

    def _set_data(self):
        assert self._data != None

        self._access_token = self._data.get('access_token')
        self._expires_in = self._data.get('expires_in')
        self._refresh_token = self._data.get('refresh_token')
        self._openid = self._data.get('openid')
        self._scope = self._data.get('scope')

        # set session
        self._set_session()

        # Save openid
        if not WechatWebModel.objects.filter(openid=self._openid):
            WechatWebModel.objects.create(openid=self._openid)

    def _detect_error(self, data):
        if data.get('errcode', None):
            raise Exception(data)

    @property
    def _set_data_by_code(self):
        '''
            Setp 2: 通过code换取网页授权access_token
        '''
        # already login session
        # if self._request.session.get('wechat', None):
        #    self._data = self._request.session.get('wechat')
        #    return self._data

        assert self._code != None

        if not self._data:
            self._data = requests.get(
                'https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={SECRET}&code={CODE}&grant_type=authorization_code'
                .format(
                    APPID=self._appid,
                    SECRET=self._appsecret,
                    CODE=self._code
                )).json()
            # Error Detctive
            self._detect_error(self._data)

            self._set_data()

        return self._data

    def get_data(self):
        return self._set_data_by_code

    def _get_data(self, name):
        if not self._data:
            return self._set_data_by_code.get(name, None)
        return self._data.get(name)

    def get_access_token(self):
        return self._get_data('access_token')

    def get_openid(self):
        return self._get_data('openid')

    def get_scope(self):
        return self._get_data('scope')

    def get_refresh_token(self):
        return self._get_data('refresh_token')

    def refresh_access_token(self):
        '''
            Step 3: 刷新 access_token (如果需要)
        '''
        self._data = requests.get(
            'https://api.weixin.qq.com/sns/oauth2/refresh_token?\
                appid={APPID}&grant_type=refresh_token&refresh_token={REFRESH_TOKEN}'
            .format(
                APPID=self._appid,
                REFRESH_TOKEN=self._refresh_token
            )
        ).json()

        # Error Detctive
        self._detect_error(self._data)

    def _save_user_data(self, user_data):
        '''
            Save user data to database
        '''
        _ = WechatWebModel.objects.get(openid=self._openid)
        _.nickname = user_data.get('nickname')
        _.sex = user_data.get('sex')
        _.province = user_data.get('province')
        _.city = user_data.get('city')
        _.country = user_data.get('country')
        _.headimgurl = user_data.get('headimgurl')
        _.privilege = user_data.get('privilege')
        _.unionid = user_data.get('unionid', None)
        _.save()
        

    def _set_user_data(self, data):
        assert data != None

        self._nickname = data.get('nickname')
        self._sex = data.get('sex')
        self._province = data.get('province')
        self._city = data.get('city')
        self._country = data.get('country')
        self._headimgurl = data.get('headimgurl')
        self._privilege = data.get('privilege')
        self._unionid = data.get('unionid', None)
        # save to database
        self._save_user_data(data)

    def get_user_data(self):
        '''
            Setp 4: 拉取用户信息(需scope为snsapi_userinfo)
        '''
        assert self._scope == 'snsapi_userinfo'

        if self._user_data:
            return self._user_data

        self._user_data = requests.get(
            'https://api.weixin.qq.com/sns/userinfo?access_token={ACCESS_TOKEN}&openid={OPENID}&lang={LANG}'
            .format(
                ACCESS_TOKEN=self.get_access_token(),
                OPENID=self._openid,
                LANG=self._lang
            )).json()

        # detector
        self._detect_error(self._user_data)

        self._user_data

        # set user data
        self._set_user_data(self._user_data)

        return self._user_data

    
    @classmethod
    def is_weixin(request):
        '''
            Judge login with weixin from request.session['openid']
        '''
        return 'openid' in request.session

def wbredirect(request, *args, **kwargs):
    scope = request.GET.get(
        'scope',
        settings.WECHAT.get('scope', 'snsapi_base')
        )
    return WechatWeb(
            request=request,
            appid=settings.WECHAT.get('appid', None),
            redirect_uri=request.get_raw_uri(),
            scope=scope
        ).authenticate()

def wbauthorize(request, *args, **kwargs):
    return WechatWeb(
            request=request,
            appid=settings.WECHAT.get('appid', None),
            appsecret=settings.WECHAT.get('appsecret', None),
            code=request.GET.get('code', None)
        )



class WechatView(View):
    '''
        WechatView extends django.views.generic.View
    '''
    def __init__(self, **kwargs):
        super(WechatView, self).__init__(**kwargs)

        self._wb = None
        self._openid = None
        self._redirect = False

    def get(self, request, *args, **kwargs):
        '''
        Override
        @return Response Object
        '''
        raise Exception('You must override callback method')


    
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error hadller if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            # wechat only need get method
            if request.method.lower() in ['get']:
                self.wechat(request, *args, **kwargs)
                if self._redirect:
                    return self._response
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def wechat(self, request, *args, **kwargs):
        '''
            获取openid 并 执行返回self.callback
        ''' 
        if self._openid:
            pass
        elif 'openid' in request.session:
            self._openid = request.session.get('openid')
        elif 'code' not in request.GET:
            self._redirect = True
            self._response = wbredirect(request, *args, **kwargs)    
        else:
            wb = wbauthorize(request, *args, **kwargs)
            self._openid = wb.get_openid()
        
        # 跳转
        # if self._redirect:
        #    return self._response
        # return self.callback(request, *args, **kwargs)

    def get_data(self):
        return WechatWeb.wb.get_data()

    def get_openid(self):
        return WechatWeb.openid

    @property
    def is_redirect(self):
        return False if not self._redirect else True
