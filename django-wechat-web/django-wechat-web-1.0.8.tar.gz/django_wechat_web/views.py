from django.shortcuts import redirect
from django.views.generic import View
from django.conf import settings

from .models import WechatBase, WechatUserInfo
from .wechat import WechatWeb

class WechatView(View):
    '''
        WechatView extends django.views.generic.View
    '''
    scope = 'snsapi_base'
    switch = True
    models = {
        'base': WechatBase,
        'userinfo': WechatUserInfo,
    }

    def __init__(self, **kwargs):
        super(WechatView, self).__init__(**kwargs)

    def _limit_scope(self):
        assert self.scope in ['snsapi_base', 'snsapi_userinfo'],\
            'scope must be snsapi_base or snsapi_userinfo'

    def before_request(self, request, *args, **kwargs):
        pass

    def wechat(self, request, *args, **kwargs):
        '''
            获取openid 或者 获取用户详细信息

            @param request object
            @return (redirect_or_not, redirect_function_or_other)
        '''
        self._limit_scope()
        # WechatView Object

        if 'code' not in request.GET or 'openid' not in request.session:
            wb = WechatWeb(
                    request=request,
                    appid=settings.WECHAT.get('appid', None),
                    appsecret=settings.WECHAT.get('appsecret', None),
                    redirect_uri=request.get_raw_uri(),
                    scope='snsapi_base',
                    code=request.GET.get('code', None)
                )

            # s1: 如果openid不存在, 且code不存在, 直接跳转
            # s2: 如果openid不存在, 但code存在, 则设置openid到session, 然后s3
            # s3: 如果scope=='snsapi_base', 那么返回，不跳转
            # s4: 如果scope=='snsapi_userinfo', 那么设置scope, 并跳转
            if 'code' in request.GET:
                wb.set_session()
                if wb.validate_code():
                    wb.save_base()
                    if self.scope in ['snsapi_base']:
                        return (False, None)

            if 'openid' in request.session:
                if not WechatBase.objects.filter(openid=request.session.get('openid')).exists():
                    WechatBase.objects.create(openid=request.session.get('openid'))
                if self.scope in ['snsapi_userinfo'] and \
                    not WechatUserInfo.objects.filter(openid=request.session.get('openid')).exists():
                    wb.set_scope(self.scope)

            return (True, wb.redirect())
        else:
            # snsapi_base not to save userinfo
            if self.scope in ['snsapi_base']:
                return (False, None)

            # s6 如果userinfo已经存在，就不跳转
            openid = request.session.get('openid')
            if self.models['userinfo'].objects.filter(openid=openid).exists():
                return (False, None)

            # s5: 在s4之后，这里是跳转后的二次授权
            #   已经有code
            wb = WechatWeb(
                    request=request,
                    appid=settings.WECHAT.get('appid', None),
                    appsecret=settings.WECHAT.get('appsecret', None),
                    redirect_uri=request.get_raw_uri(),
                    scope='snsapi_userinfo',
                    code=request.GET.get('code', None)
                )
            # s6: 保存用户信息
            wb.save_userinfo()

            # session已经有openid, 而code可能是无效的, 则跳转
            if wb.validate_code():
                return (False, None)

            return (True, wb.redirect())

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exits.
        # defer to the error handler.Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:

            # when swicth=True and 'get' method, wechat works
            if self.switch and request.method.lower() in ['get']:
                redirect_or_not, callback = self.wechat(
                        request, *args, **kwargs)
                if redirect_or_not:
                    return callback

            self.before_request(request, *args, **kwargs)
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        '''
        Override
        @return Reponse Object
        '''
        raise Exception('You must override get method')


class Wechat(WechatView):
    scope = 'snsapi_base'

    def get(self, request, *args, **kwargs):
        super(Wechat, self).get(request, *args, **kwargs)
        if self.is_redirect:
            return self._response

        return Response({
            'openid': request.session.get('openid')    
        })
