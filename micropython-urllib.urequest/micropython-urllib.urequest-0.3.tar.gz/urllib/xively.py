from urllib.urequest import urlopen


class Xively:

    def __init__(self, feed, key):
        self.url = "http://api.xively.com/v2/feeds/%s.json?key=%s" % (feed, key)

    def write(self, channel, value):
        data="""\
{
  "version": "1.0.0",
   "datastreams" : [ {
        "id" : "%s",
        "current_value" : "%s"
    }
  ]
}
""" % (channel, value)
        f = urlopen(self.url, method="PUT", data=data)
        resp = f.read()
        f.close()
        assert resp == b""
