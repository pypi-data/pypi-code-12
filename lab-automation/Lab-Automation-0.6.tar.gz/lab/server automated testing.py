import requests
import json

URL_BASE = "http://172.16.115.106:8080/"
URL_list = [ r'^login/$', r'^register/$', r'^courseregister/$', r'^assignments/$', r'^courselist/$',
			 r'^coursestudentlist/$', r'^assignmentlist/$', r'^addassignment/$', r'^tastudents/$', 
			 r'^savesubmission/$', r'^addquestions/$',  r'^addtastud/$', r'stupro/$',  r'^ansassign/$',
			 r'^updcodemarks/$', r'^logout/$']

for url in URL_list:
	print "requested URL => "+URL_BASE+url[1:-1]
	try:
		response = json.loads(requests.post(URL_BASE+url[1:-1], proxies={}, headers=dict(Referer=URL_BASE+url[1:-1])).content)
		print "response for POST request => "+response
	except Exception as e:
		print "response for POST request => "
		print e
	try:
		response = json.loads(requests.get(URL_BASE+url[1:-1], proxies={}, headers=dict(Referer=URL_BASE+url[1:-1])).content)
		print "response for GET request => "+response
	except Exception as e:
		print "response for GET request => "
		print e