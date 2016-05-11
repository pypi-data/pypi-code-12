from tornado.httpclient import AsyncHTTPClient
import yajl


def _optional_args(args_lst):
    args_str = "?"
    for args in args_lst:
        if args[1] is not None:
            args_str = "%s%s=%s&" % (args_str, args[0], str(args[1]))
    return args_str


class _Payments:
    def __init__(self, api_key, api_secret, client: AsyncHTTPClient):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.razorpay.com/"
        self.version = "v1"
        self.payment_directory = "payments"
        self.api_url = "%s%s/%s/" % (self.base_url, self.version, self.payment_directory)
        self.http_client = client

    async def all(self, from_time=None, to_time=None, count=None, skip=None):
        args = _optional_args([["from", from_time], ["to", to_time], ["count", count], ["skip", skip]])
        url = "%s%s" % (self.api_url, args)
        response = await self.http_client.fetch(url, auth_username=self.api_key, auth_password=self.api_secret,
                                                raise_error=False)
        return response

    async def fetch(self, payment_id):
        url = "%s%s" % (self.api_url, payment_id)
        response = await self.http_client.fetch(url, method="GET", auth_username=self.api_key,
                                                auth_password=self.api_secret, raise_error=False)
        return response

    async def capture(self, payment_id):
        url = "%s%s/capture" % (self.api_url, payment_id)
        response = await self.http_client.fetch(url, method="POST", auth_username=self.api_key,
                                                auth_password=self.api_secret, raise_error=False)
        return response


class _Refunds:
    def __init__(self, api_key, api_secret, client: AsyncHTTPClient):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.razorpay.com/"
        self.version = "v1"
        self.payment_directory = "payments"
        self.api_url = "%s%s/%s/" % (self.base_url, self.version, self.payment_directory)
        self.http_client = client

    async def create(self, payment_id, data={}):
        url = "%s%s/refund" % (self.api_url, payment_id)
        body = yajl.dumps(data)
        response = await self.http_client.fetch(url, body=body, method="POST", auth_username=self.api_key,
                                                auth_password=self.api_secret, raise_error=False)
        return response

    async def all(self, payment_id, from_time=None, to_time=None, count=None, skip=None):
        args = _optional_args([["from", from_time], ["to", to_time], ["count", count], ["skip", skip]])
        url = "%s%s/refunds%s" % (self.api_url, payment_id, args)
        response = await self.http_client.fetch(url, auth_username=self.api_key, auth_password=self.api_secret,
                                                raise_error=False)
        return response

    async def fetch(self, payment_id, refund_id):
        url = "%s%s/refunds/%s" % (self.api_url, payment_id, refund_id)
        response = await self.http_client.fetch(url, auth_username=self.api_key, auth_password=self.api_secret,
                                                raise_error=False)
        return response


class Client:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.http_client = AsyncHTTPClient()
        self.payment = _Payments(api_key, api_secret, self.http_client)


# if __name__ == "__main__":
#     from tornado.ioloop import IOLoop
#     from bpython import embed
#
#     client = Client("<YOUR_API_KEY>", "<YOUR_API_SECRET>")
#     event_loop = IOLoop().current()
#     resp1 = event_loop.run_sync(lambda: client.payment.all(count=1))
#     resp2 = event_loop.run_sync(lambda: client.payment.fetch(payment_id="pay_5UWWNIhctVbyRS"))
#     embed(locals())
