# coding=utf-8
class UserAgent(object):
    def __init__(self, is_mobile, os):
        self.is_mobile = is_mobile
        self.os = os


class UserAgentDetectMiddleware(object):
    def process_request(self, request):
        """
        检测是否是移动浏览器，然后设置is_mobile、os
        @param request:
        @type request:  django.http.HttpRequest
        @return:
        """
        user_agent = request.META['HTTP_USER_AGENT'].lower()
        is_mobile = False
        os = 'Windows'
        if 'micromessenger' in user_agent:
            is_mobile = True
            os = 'MicroChat'
        elif 'android' in user_agent:
            is_mobile = True
            os = 'Andriod'
        elif 'iphone' in user_agent:
            is_mobile = True
            os = 'iPhone/iOS'
        elif 'ipad' in user_agent:
            is_mobile = True
            os = 'iPad/iOS'
        elif 'windows phone' in user_agent:
            is_mobile = True
            os = 'Windows Phone'
        elif 'ucweb' in user_agent:
            is_mobile = True
            os = 'UCWEB'

        ua = UserAgent(is_mobile, os)
        setattr(request, 'ua', ua)
