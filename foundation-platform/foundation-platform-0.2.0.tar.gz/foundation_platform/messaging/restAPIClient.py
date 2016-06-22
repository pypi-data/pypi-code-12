from __future__ import print_function
import json
import requests

ip = '135.111.96.21'
port = 5000
url = 'http://' + ip + ':' + str(port)
path_map = {'IMAGE': '/VIM/images',
            'CATALOG': '/VNFM/appcatalog',
            'HEAT': '/VIM/orchestration'}


# https://realpython.com/blog/python/api-integration-in-python/


class restAPIClient(object):
    """restAPIClient."""

    def __init__(self, msg):
        """__init__"""
        self.message = msg
        try:
            self.full_url = self.build_full_url()
            self.printarg()
            # self.health_check()
            self.send_msg()
        except Exception:
            raise

    def printarg(self):
        """Method printarg."""
        print('<-- Sending the msg , my msg is -->')
        print(self.message)
        print(self.full_url)

    def build_full_url(self):
        path = self.get_path()
        return url + path

    def get_path(self):
        return path_map.get(str(self.message.get('type')))

    def health_check(self):
        resp = requests.get(url + '/VNFM/appcatalog')
        print(resp.status_code)
        if resp.status_code != 200:
            # This means something went wrong.
            # raise StandardError(resp.status_code)
            # TODO: fix reference to above undefined class
            pass
        return resp.ok

    def send_msg(self):
        resp = requests.post(self.full_url, json=self.message)
        print("<------ Server Response ------->")
        print(resp.content)
        print(resp.status_code)


def obj_to_JSON(object):
    return json.dumps(object)


''' this is used just for local testing'''


def main():
    res = restAPIClient()
    print(res)


if __name__ == '__main__':
    main()
