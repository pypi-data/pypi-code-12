import json
import falcon
from penelope.utils.misc import parse_content_type


class JSONResponse:

    def process_response(self, req, res, resource):
        if 'json_resp' in req.context:
            res.content_type = 'application/json'
            res.body = json.dumps(req.context['json_resp'])
        else:
            res.body = None


class JSONRequest:

    def process_request(self, req, res):
        if req.content_type is not None:
            mimetype, charset = parse_content_type(req.content_type)
            if mimetype == 'application/json':
                data = req.stream.read().decode(charset)
                if data:
                    try:
                        parsed = json.loads(data, encoding=charset)
                        req.context['data'] = parsed if parsed is not None else {}
                        req.context['raw_data'] = data
                    except ValueError:
                        message = "Request body is not valid 'application/json'"
                        raise falcon.HTTPBadRequest('Invalid JSON', message)
