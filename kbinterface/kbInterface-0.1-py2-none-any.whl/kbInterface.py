# kbInterface.py
"""Python module to get a KBase GenomeAnnotation interface."""

def get(ref):
	import os
	from doekbase.data_api.annotation.genome_annotation import api
	
	try:
		token=os.environ['KB_AUTH_TOKEN']
	except KeyError:
		acc=loadKbAcc()
		os.environ['KB_AUTH_TOKEN']=getKbSession(acc['username'],acc['password'])

	token=os.environ['KB_AUTH_TOKEN']

	return api.GenomeAnnotationAPI(
	    token=token,
	    services={'workspace_service_url': 'https://kbase.us/services/ws/'},
	    ref=ref)

def loadKbAcc():
	#import bcrypt
	from subprocess import call
	import pickle
	from getpass import getpass
	import os.path

	filepath=os.path.join(os.path.expanduser('~'),".kbacc")

	print("Retrieving KBase account info.\n")

	try:
		acc=pickle.load(open(filepath,"rb"))
	except:
		print("No passfile found. Enter KBase account info.\n")
		username = raw_input("Username: ");
		password = getpass("Password: ");
		#hashed = bcrypt.hashpw(password, bcrypt.gensalt())
		acc={'username': username, 'password': password}
		pickle.dump(acc,open(filepath,"wb"))
		call(["chmod","0600",filepath])

	return acc


def getKbSession(user_id,password):
	from requests import Session
	import json

	payload = {
		'fields': 'un,token,user_id,kbase_sessionid,name',
	    'user_id': user_id,
	    'password': password,
	    'status': 1
	}

	s = Session()

	log = s.post('https://kbase.us/services/authorization/Sessions/Login', data=payload)
	jres = json.loads(log.text)

	return jres['token']
