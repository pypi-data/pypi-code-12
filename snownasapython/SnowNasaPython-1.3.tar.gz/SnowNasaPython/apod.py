from urllib2 import Request, urlopen, URLError


class Apod(object):

  def __init__(self, api_key):
    self.api_key = api_key 
  
  def get_apod_pic(self):
    api_key = self.api_key
    url = Request('https://api.nasa.gov/planetary/apod?api_key=%s' %api_key)
    try: 
       response = urlopen(url)
       data = response.read()
       print data 
    except URLError, e:
       print 'No data available', e 
