import os


# get local proxy setting from system env and bypass proxy for local address
HTTPS_PROXY = os.environ.get('https_proxy')
os.environ['no_proxy'] = 'localhost,127.0.0.0/8,127.0.1.1,127.0.1.1'
