from sparkpost import SparkPost

import requests
import os

class SparkPostIPNotifier:
    current_ip = None
    fetched_ip = None

    def __init__(self, sparkpost_api_key, subject, from_email, recipients):
        self.subject = subject
        self.from_email = from_email
        self.recipients = recipients

        self.current_ip = self.get_saved_ip()
        self.fetched_ip = self.fetch_and_save_ip_from_sites()
        self.sparkpost = SparkPost(sparkpost_api_key)

        if self.has_ip_changed():
            self.send_notification()

    @staticmethod
    def get_sites():
        return [
            {'url': 'http://jsonip.com/', 'key': 'ip', 'kind': 'json'},
            {'url': 'http://httpbin.org/ip', 'key': 'origin', 'kind': 'json'},
            {'url': 'https://api.ipify.org?format=json', 'key': 'ip', 'kind': 'json'},
            {'url': 'http://ip.42.pl/raw', 'key': 'ip', 'kind': 'text'}
        ]

    @staticmethod
    def save_ip(ip):
        with open('ip.txt', 'w') as f:
            f.write(ip)

    @staticmethod
    def get_saved_ip():
        if not os.path.isfile('ip.txt'):
            return

        with open('ip.txt', 'r') as f:
            return f.read()

    @classmethod
    def fetch_and_save_ip_from_sites(self):
        ip = self.current_ip
        sites = self.get_sites()

        for site in sites:
            key = site.get('key')
            url = site.get('url')
            kind = site.get('kind')

            try:
                response = requests.get(url)
                if kind is 'text':
                    ip = response.text
                elif kind is 'json':
                    json = response.json()
                    ip = json.get(key)

            except Exception, e:
                pass

            if ip is not None:
                break

        self.save_ip(ip)
        return ip

    def send_notification(self):
        text = 'New IP-address: {}.\nOld IP-address: {}'.format(self.fetched_ip, self.current_ip)
        r = self.sparkpost.transmission.send(subject=self.subject, from_email=self.from_email, text=text, recipients=self.recipients)
        return r

    def has_ip_changed(self):
        return self.current_ip != self.fetched_ip
