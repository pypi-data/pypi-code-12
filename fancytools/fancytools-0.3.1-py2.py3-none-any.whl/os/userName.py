import os

try:
	import pwd
except ImportError:
	import getpass
	pwd = None


def userName():
	'''return the user-name of the current user'''
	if pwd:
		return pwd.getpwuid(os.geteuid()).pw_name
	else:
		return getpass.getuser()



if __name__ == '__main__':
	print("your user name is '%s'" %userName() )