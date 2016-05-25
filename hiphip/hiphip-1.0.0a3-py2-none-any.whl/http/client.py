import errno
from json import loads as json_loads, dumps as json_dumps

try:
    import requests
    from requests.cookies import RequestsCookieJar
except ImportError:
    print("Python module requests is required. Run this in your terminal:")
    print("$ pip3 install requests")
    exit(errno.ENOPKG)

try:
    from requests_toolbelt import MultipartEncoder
except ImportError:
    print("Python module requests is required. Run this in your terminal:")
    print("$ pip3 install requests_toolbelt")
    exit(errno.ENOPKG)


class Client:
    params = None
    headers = None
    cookies = None
    timeout = None

    def __merge_params(self, request_params):
        params = request_params
        if type(self.params) is dict:
            for name, value in self.params.items():
                params[name] = value
        return params

    def __merge_headers(self, request_headers):
        headers = request_headers
        if type(self.headers) is dict:
            for name, value in self.headers.items():
                headers[name] = value
        return headers

    def __merge_cookies(self, request_cookies):
        if type(request_cookies) is RequestsCookieJar:
            cookies = request_cookies
        else:
            cookies = RequestsCookieJar()
            for name, value in request_cookies:
                cookies.set(name, value)

        if type(self.cookies) is RequestsCookieJar:
            for cookie in iter(self.cookies):
                cookies.set_cookie(cookie)
        elif type(self.cookies) is dict:
            for name, value in self.cookies.items():
                cookies.set(name, value)

        return cookies

    def __patch_data(self, data):
        patched_data = {}
        for key, val in data.items():
            if type(val) in [type(None), bool, int, float, list, dict]:
                patched_data[key] = json_dumps(val)
            else:
                patched_data[key] = val
        return patched_data

    def request(self,
                method,
                url,
                params=None,
                headers=None,
                cookies=None,
                data=None,
                form=None,
                json=None,
                timeout=None,
                allow_redirects=False,
                **kwargs):
        """
        :param method: HTTP method to use.
        :type method: str

        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param data: The body to attach to the application/x-www-form-urlencoded request.
        :type data: dict | None

        :param form: The body to attach to the multipart/form-data request.
        :type form: dict | None

        :param json: JSON for the body to attach to the request.
        :type json: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        params = self.__merge_params(params or {})
        headers = self.__merge_headers(headers or {})
        cookies = self.__merge_cookies(cookies or {})
        timeout = self.timeout if (self.timeout is not None) else timeout

        if form is not None:
            data = MultipartEncoder(self.__patch_data(form))
            headers["content-type"] = data.content_type
        elif json is not None:
            data = json_dumps(json)
            headers["content-type"] = "application/json"
        elif data is not None:
            data = self.__patch_data(data)

        response = requests.request(method=method,
                                    url=url,
                                    params=params,
                                    headers=headers,
                                    cookies=cookies,
                                    data=data,
                                    timeout=timeout,
                                    allow_redirects=allow_redirects,
                                    **kwargs)

        response.body = response.text
        content_type = response.headers.get("content-type")
        if content_type and "json" in content_type:
            try:
                response.body = json_loads(response.text)
            except ValueError:
                pass

        return response

    def head(self,
             url,
             params=None,
             headers=None,
             cookies=None,
             timeout=None,
             allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("HEAD",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def options(self,
                url,
                params=None,
                headers=None,
                cookies=None,
                timeout=None,
                allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("OPTIONS",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def get(self,
            url,
            params=None,
            headers=None,
            cookies=None,
            timeout=None,
            allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("GET",
                            url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def post(self,
             url,
             params=None,
             headers=None,
             cookies=None,
             data=None,
             form=None,
             json=None,
             timeout=None,
             allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param data: The body to attach to the application/x-www-form-urlencoded request.
        :type data: dict | None

        :param form: The body to attach to the multipart/form-data request.
        :type form: dict | None

        :param json: JSON for the body to attach to the request.
        :type json: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("POST",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            data=data,
                            form=form,
                            json=json,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def put(self,
            url,
            params=None,
            headers=None,
            cookies=None,
            data=None,
            form=None,
            json=None,
            timeout=None,
            allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param data: The body to attach to the application/x-www-form-urlencoded request.
        :type data: dict | None

        :param form: The body to attach to the multipart/form-data request.
        :type form: dict | None

        :param json: JSON for the body to attach to the request.
        :type json: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("PUT",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            data=data,
                            form=form,
                            json=json,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def patch(self,
              url,
              params=None,
              headers=None,
              cookies=None,
              data=None,
              form=None,
              json=None,
              timeout=None,
              allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param data: The body to attach to the application/x-www-form-urlencoded request.
        :type data: dict | None

        :param form: The body to attach to the multipart/form-data request.
        :type form: dict | None

        :param json: JSON for the body to attach to the request.
        :type json: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("PATCH",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            data=data,
                            form=form,
                            json=json,
                            timeout=timeout,
                            allow_redirects=allow_redirects)

    def delete(self,
               url,
               params=None,
               headers=None,
               cookies=None,
               data=None,
               form=None,
               json=None,
               timeout=None,
               allow_redirects=False):
        """
        :param url: URL to send.
        :type url: str

        :param params: Dictionary of URL parameters to append to the URL.
        :type params: dict | None

        :param headers: Dictionary of HTTP Headers to send.
        :type headers: dict | None

        :param cookies: Dictionary or CookieJar of cookies to attach to this request.
        :type cookies: dict | None

        :param data: The body to attach to the application/x-www-form-urlencoded request.
        :type data: dict | None

        :param form: The body to attach to the multipart/form-data request.
        :type form: dict | None

        :param json: JSON for the body to attach to the request.
        :type json: dict | None

        :param timeout: How long to wait for the server to send data before giving up.
        :type timeout: float | None

        :param allow_redirects: Set to False by default.
        :type allow_redirects: bool

        :return requests.Response
        """
        return self.request("DELETE",
                            url=url,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            data=data,
                            form=form,
                            json=json,
                            timeout=timeout,
                            allow_redirects=allow_redirects)
