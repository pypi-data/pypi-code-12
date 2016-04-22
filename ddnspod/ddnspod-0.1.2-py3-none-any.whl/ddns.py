import time
import logging
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s,  %(message)s')
fh = logging.FileHandler('ddnspod.log')
fh.setFormatter(formatter)
logger.addHandler(fh)


class Ddns:
    """simple ddns
    DNSPod API DOC: https://www.dnspod.cn/docs/index.html
    get domain_id and record_id
    curl -X POST https://dnsapi.cn/Domain.List -d 'login_token=LOGIN_TOKEN&format=json'
    curl -X POST https://dnsapi.cn/Record.List -d 'login_token=LOGIN_TOKEN&format=json&domain_id=2317346'
    """
    DNSPOD_API = 'https://dnsapi.cn/Record.Ddns'
    API_IP_URL = 'http://httpbin.org/ip'

    def __init__(self, login_token, domain_id, record_id, sub_domain):
        self.login_token = login_token
        self.domain_id = domain_id
        self.record_id = record_id
        self.sub_domain = sub_domain,

        self.current_ip = '127.0.0.1'

    @staticmethod
    def get_public_ip():
        """find a more reliable api
        :return: ip address, example: '1.2.3.4'
        """
        return requests.get(Ddns.API_IP_URL).json()['origin']

    def _ddns(self, ip):
        """
        curl -X POST https://dnsapi.cn/Record.Ddns -d 'login_token=LOGIN_TOKEN&format=json&domain_id=2317346&record_id=16894439&record_line=默认&sub_domain=www'
        :return:
        """

        headers = {"Accept": "text/json", "User-Agent": "ddns/0.1.0 (imaguowei@gmail.com)"}

        data = {
            'login_token': self.login_token,
            'format': "json",
            'domain_id': self.domain_id,
            'record_id': self.record_id,
            'sub_domain': self.sub_domain,
            'record_line': '默认',
            'value': ip
        }

        res = requests.post(Ddns.DNSPOD_API, data, headers=headers)
        logger.debug(res.json())
        return res.json()['status']['code'] == '1'

    def checker(self, seconds=60*5):
        while True:
            try:
                ip = Ddns.get_public_ip()

                if ip == self.current_ip:
                    logger.info('ip no change! current_id: {}'.format(self.current_ip))
                else:
                    if self._ddns(ip):
                        logger.info('ip change success! before: {}, after: {}'.format(self.current_ip, ip))
                        self.current_ip = ip
                    else:
                        logger.info('ip change error! before: {}, after: {}'.format(self.current_ip, ip))
            except Exception as e:
                logger.info(e)
            finally:
                time.sleep(seconds)


if __name__ == '__main__':
    token_id = '12345'
    token = 'ec589ccfa8jk4b1241d3e63b7690b53b'

    d = Ddns('{},{}'.format(token_id, token), 37642234, 18292123, 'dev')
    d.checker(10)
