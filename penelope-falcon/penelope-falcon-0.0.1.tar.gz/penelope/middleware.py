import json


class JSONResponse:

    def process_response(self, req, res, resource):
        if 'json_resp' in req.context:
            res.body = json.dumps(req.context['json_resp'])
            res.content_type = 'application/json'
        else:
            res.body = None
