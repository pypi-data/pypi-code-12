#!/usr/bin/env python
import urllib2, re, sys

def getMAC(interface):
  # Return the MAC address of interface
  try:
    str = open('/sys/class/net/' + interface + '/address').read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]


configurl =  "http://www.rxwave.com/config/" + getMAC('eth0')
response = urllib2.urlopen(configurl)
configfl = response.read()
#print configfl
orig = configfl.splitlines(configfl.count('\n'))
target = open("/etc/piscan/piscan.ini", 'r+')
origfl = target.read()

newconfig = ''
for line in orig:
    newln = line
    if re.match("^RID:\s", line, re.I):
        newln = re.sub(r'^RID:\s', line, origfl)
    newconfig = newconfig + newln 
#print target.read()
print newconfig
#target.write(configfl)

#target.close()

