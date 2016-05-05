import unittest
from flask import Flask
from flask.ext.testing import LiveServerTestCase
from urllib.request import urlopen

# class TestSimpleController(LiveServerTestCase):
#
#     def create_app(self):
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         return app
#
#     def test_call(self):
#         content = urlopen(self.get_server_url())
#         print(content)
        # print(self.get_server_url())
        # content = urlopen()

def test():
    print('asdf')

if __name__ == '__main__':
    a = test()
    print(a)