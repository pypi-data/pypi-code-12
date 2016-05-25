import json
from collections import OrderedDict

import requests


class Response(requests.Response):

    def __repr__(self):
        r = "{method} {url}\n\n".format(method=self.request.method, url=self.request.url)

        r += "HTTP/1.1 {status}\n".format(status=self.status_code)
        for key, value in OrderedDict(sorted(self.headers.items())).items():
            r += "{key}: {value}\n".format(key=key, value=value)

        content_type = self.headers.get("content-type", "text/plain").lower()
        if content_type.startswith("text/") or content_type.endswith("/text"):
            r += "\n" + str(self.text)
        elif content_type.startswith("application/json"):
            text = json.loads(self.text or "")
            r += "\n" + json.dumps(text, sort_keys=True, ensure_ascii=False, indent=2)

        return r
