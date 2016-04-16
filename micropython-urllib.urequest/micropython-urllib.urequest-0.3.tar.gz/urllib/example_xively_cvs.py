import time
from urequest import urlopen


FEED = "http://api.xively.com/v2/feeds/436311059"

t = time.time() - 2 * 3600
tstamp = time.strftime("%Y-%m-%dT%H:%M:00Z", int(t))
data="sensor1,%s,210\n" % tstamp
print(data)

f = urlopen(FEED + ".csv?key=2ez3VN73MFbOEP96fZ4KVBBxRZ2pe64RUXhpbINb6qMJIQ4e", method="PUT", data=data)
print(str(f.read(), "utf-8"))
