from requests import Session
from requests.models import Request, PreparedRequest, DEFAULT_REDIRECT_LIMIT
from hashlib import sha1
from pymongo import MongoClient,DESCENDING
from datetime import datetime

class cache_session(Session):
    def __init__(self, db_uri, dbname='tmp', colname='cache', expire_time=None, disabled=False, url_only=True):
        self.col = MongoClient(db_uri)[dbname][colname]
        self.disabled = disabled
        self.url_only = url_only
        if expire_time:
            if not self.col.index_information().get('cache_time'+'_-1'):
                self.col.create_index([("cache_time", DESCENDING)],expireAfterSeconds=expire_time)
            else:
                self.col.drop_indexes()
                self.col.create_index([("cache_time", DESCENDING)],expireAfterSeconds=expire_time)
        super(cache_session, self).__init__()

    def request(self, method, url,
                params=None,
                data=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None):
        req = (
            method.upper(),
            url,
            headers,
            files,
            data or {},
            json,
            params or {},
            auth,
            cookies,
            hooks,
        )
        if self.url_only:
            req1 = {
                'url': url,
            }
        else:
            req1 = {
                'method': method.upper(),
                'url': url,
                'headers': headers,
                'files': files,
                'data': data or {},
                'json': json,
                'params': params or {},
                'auth': auth,
                'cookies': cookies,
                'hooks': hooks,
            }
        req_to_str = '&'.join("%s=%s" % (k, v) for k, v in req1.items())
        key = sha1(req_to_str).hexdigest()
        cached_one = self.col.find_one({'key': key})
        if cached_one and not self.disabled:
            print 'cached'
            return cached_one['html']
        else:
            online_req = super(cache_session, self).request(method, url,
                                                 params=None,
                                                 data=None,
                                                 headers=None,
                                                 cookies=None,
                                                 files=None,
                                                 auth=None,
                                                 timeout=None,
                                                 allow_redirects=True,
                                                 proxies=None,
                                                 hooks=None,
                                                 stream=None,
                                                 verify=None,
                                                 cert=None,
                                                 json=None
                                                 )

            html = online_req.text
            self.col.insert_one({'key': key, 'html': html, 'cache_time': datetime.utcnow()})
            return html


if __name__ == '__main__':
    a = my_session('mongodb://admin:scrapy@localhost:27017/?authMechanism=SCRAM-SHA-1')
    a.get('http://www.baidu.com')
    from pymongo import MongoClient

    client = MongoClient('mongodb://admin:scrapy@localhost:27017/?authMechanism=SCRAM-SHA-1')
    print client.req.cache.count()
