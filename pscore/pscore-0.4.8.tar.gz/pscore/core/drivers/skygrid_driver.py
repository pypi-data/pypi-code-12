from selenium.webdriver.remote.webdriver import WebDriver
import requests
import six
from ...config.test_configuration import TestConfiguration as config
from ...clients.skygrid.api.skygridapiclient import SkyGridApiClient

if six.PY34:
    from urllib.parse import urlparse
else:
    # Python 2.7.* approach
    from urlparse import urlparse


class SkygridDriver(WebDriver):
    test_context = None

    @staticmethod
    def _get_host(url):
        parsed = urlparse(url)
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed)

    def active_node_ip(self):
        hub_uri = config.get_hub_url()
        hub_uri = self._get_host(hub_uri)

        uri = "{}/grid/api/testsession?session={}".format(hub_uri, self.session_id)
        reply = requests.get(uri)

        if reply.status_code == 200:
            url = reply.json()['proxyId']
            return self._get_host(url)

        # RG: TODO this should retry or raise?
        return None

    def active_node_ip_no_port(self):
        with_port = self.active_node_ip()
        parts = with_port.split(':')
        # no forward slash at end
        return "{}:{}".format(parts[0], parts[1])

    def get_screenshot_as_file(self, filename):
        self._get_screenshot()

    def get_screenshot_as_base64(self):
        self._get_screenshot()

    def get_screenshot_as_png(self):
        self._get_screenshot()

    def _get_screenshot(self):
        api_client = SkyGridApiClient(driver=self)
        shot = api_client.take_screenshot()
        self.test_context.skygrid_screenshots.append(shot.to_dict())
