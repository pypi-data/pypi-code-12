import re
from urllib.parse import urlparse
from app.config import ALLOWED_ORIGINS, ALLOWED_ORIGINS_REGEX


def is_allowed_origin(origin, allowed_origins, allowed_origins_regex):
    url = urlparse(origin)
    if url.netloc.split(':')[0] in ALLOWED_ORIGINS:
        return True
    else:
        for pattern in ALLOWED_ORIGINS_REGEX:
            if re.match(pattern, origin):
                return True
    return False


class CORS:

    def __init__(self, allowed_origins, allowed_origins_regex):
        self.allowed_origins = allowed_origins
        self.allowed_origins_regex = allowed_origins_regex

    def process_request(self, req, res):
        origin = req.get_header('Origin')
        if origin and is_allowed_origin(origin, self.allowed_origins, self.allowed_origins_regex):
            res.set_header('Access-Control-Allow-Origin', origin)
            res.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, Origin, X-API-Key')
            res.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
