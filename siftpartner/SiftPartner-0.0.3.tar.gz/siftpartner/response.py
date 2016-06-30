__author__ = 'yoavschatzberg'
import json

class Response(object):
    def __init__(self, http_response):
        self.body = http_response.json()
        self.http_status_code = http_response.status_code

        # if it's an error, grab the associated fields
        if self.http_status_code != 200:
            self.error = self.body['error']

            self.error_message = self.error + ": " + self.body['description']
            if 'issues' in self.body:
                self.error_issues = self.body['issues']
                for issue in self.error_issues:
                    self.error_message += issue + ": " + self.error_issues[issue] + "\n"


        if 'request' in self.body.keys() and isinstance(self.body['request'], str):
            self.request = json.loads(self.body['request'])
        else:
            self.request = None

    def __str__(self):
        return ('{"body": %s, "http_status_code": %s}' %
                (json.dumps(self.body), str(self.http_status_code)))

    def is_ok(self):
        return self.http_status_code == 200