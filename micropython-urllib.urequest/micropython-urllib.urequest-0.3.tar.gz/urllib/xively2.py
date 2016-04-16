from urequest import urlopen


FEED = "http://api.xively.com/v2/feeds/436311059"

data="""\
{
  "version":"1.0.0",
   "datastreams" : [ {
        "id" : "sensor1",
        "current_value" : "150"
    }
  ]
}
"""
print(data)

f = urlopen(FEED + ".json?key=2ez3VN73MFbOEP96fZ4KVBBxRZ2pe64RUXhpbINb6qMJIQ4e", method="PUT", data=data)
print(str(f.read(), "utf-8"))
