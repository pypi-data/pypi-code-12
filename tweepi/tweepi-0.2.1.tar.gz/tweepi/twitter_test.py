import unittest

from requests import Session
from httmock import urlmatch, HTTMock, response

from twitter import Twitter

class TwitterMethods(unittest.TestCase):

    def test_request(self):

        @urlmatch(netloc=r'.*')
        def mock_followers(url, request):
            self.assertEqual(url.path, '/1.1/followers/ids.json')
            self.assertEqual(url.query, 'count=5000&user_id=1234')

            headers = {
                'Content-Type': 'application/json'
            }
            content = {
                "ids": [1, 2, 3], 
                "previous_cursor": 0, 
                "previous_cursor_str": "0", 
                "next_cursor": 0, 
                "next_cursor_str": "0"
            }

            return response(status_code=200, content=content, headers=headers, reason=None, elapsed=1, request=request)
        
        with HTTMock(mock_followers):
            session = Session()
            twitter = Twitter(session)
            resp = twitter.request('followers/ids', {'user_id': 1234, 'count': 5000, 'cursor': None})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json['ids']), 3)
            self.assertEqual(resp.json['ids'][0], 1)
            self.assertEqual(resp.json['ids'][1], 2)
            self.assertEqual(resp.json['ids'][2], 3)

if __name__ == '__main__':
    unittest.main()
