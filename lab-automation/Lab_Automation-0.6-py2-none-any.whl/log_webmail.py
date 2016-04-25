import getpass, poplib, sys

flag = 0

servers = {'disang' : '202.141.80.10', 'naambor' : '202.141.80.9', 'teesta' : '202.141.80.12', 'tamdil' : '202.141.80.11', 'dikrong' : '202.141.80.13'}
try:
	print "Enter Server name: "
	server = raw_input()
	M = poplib.POP3_SSL(servers[server], 995)
	print "Enter username: "
	user = raw_input()
	M.user(user)
	passwd = getpass.getpass()
	print "Enter password: "
	M.pass_(passwd)
except Exception, e:
	pass
else:
	flag = 1
if flag == 1:
	print "Login successful"
else:
	print "Username or password incorrect"