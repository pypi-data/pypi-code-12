from urlparse import urlparse

def get_domain(url):
    parsed_uri = urlparse(url)
    domain = ('{uri.netloc}/'.format(uri=parsed_uri)).strip("/")
    return domain