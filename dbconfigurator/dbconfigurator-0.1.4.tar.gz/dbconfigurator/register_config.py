import json
import sys
import os
if sys.version_info.major == 3:
	pass
else:
	input = raw_input
script_dir = os.environ.get('HOME') + '/.dbconfig'

def register_config():
    connection = {}
    connection['profile_name'] = input('Profile Name? (leave blank to set as default)')
    connection['dbms'] = input('DBMS? ')
    connection['user'] = input('username? ')
    connection['password'] = input('Password? ')
    connection['module'] = input('DB Driver Name? (python package)')
    connection['host'] = input('Host? ')
    
    connection['port']= input('Port? ')
    connection['charset'] = input('Charset? ')
    if not connection.get('profile_name'):
	    connection['profile_name'] = 'default'
    with open(str(script_dir) + '/config_{profile_name}.json'.format(profile_name=connection['profile_name']), 'w') as f:
        json.dump(connection, f)

