# -*- coding: utf-8 -*-

import os
import json
from scrapyd.webservice import WsResource
from subprocess import Popen, PIPE
from scrapyd.utils import get_crawl_args

class Crawl(WsResource):

    def jsonize(self, request, data):
        if not isinstance(data, list):
            request.setResponseCode(500)
            return {'code': 1, 'message': 'invalid data type', 'errors': data}
        try:
            data = json.loads(data)
            return {'code': 0, 'message': 'success', 'data': data}
        except ValueError as e:
            request.setResponseCode(500)
            return {'code': 1, 'message': 'json parse error', 'errors': data}

    def crawl(self, args):
        env = os.environ.copy()
        cmd = ['scrapy', 'crawl']
        args['_spider'] = args.get('spider')
        args['_project'] = args.get('project')
        cargs = get_crawl_args(args)
        cmd = cmd + cargs + ['-t', 'json', '-o', '-']
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, env=env)
        out, _ = process.communicate()
        return out

    def render_POST(self, request):
        settings = request.args.pop('setting', [])
        settings = dict(x.split('=', 1) for x in settings)
        args = dict((k, v[0]) for k, v in request.args.items())
        out = self.crawl(args)
        return self.jsonize(request, out)
