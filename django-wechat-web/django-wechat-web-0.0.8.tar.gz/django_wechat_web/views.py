from django.shortcuts import redirect
from django.views.generic import View
from django.conf import settings

from .wechat import WechatView, wbredirect
from .response import Response

class Wechat(WechatView):
    scope = 'snsapi_base'

    def get(self, request, *args, **kwargs):
        super(Wechat, self).get(request, *args, **kwargs)
        if self.is_redirect:
            return self._response

        return Response({
            'openid': request.session.get('openid')    
        })
