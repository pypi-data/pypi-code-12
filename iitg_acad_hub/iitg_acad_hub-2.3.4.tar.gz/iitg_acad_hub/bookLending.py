import requests


def lendBook(roll, contact, course, book):
	url = 'http://172.16.115.76/lendbook.php'
	data = {'roll':roll, 'contact':contact, 'course':course, 'book':book}
	r = requests.post(url, data=data)


def listLenders(course, book):
	url = 'http://172.16.115.76/listlenders.php'
	data = {'course':course, 'book':book}
	r = requests.post(url, data=data)

	lenders = r.text.split("\n")[:-1]
	rolls = []
	contacts = []
	for i in lenders:
		rolls.append(i[:9])
		contacts.append(i[9:19])
	return rolls, contacts

def deleteLender(roll, course, book):
	url = 'http://172.16.115.76/deletelenders.php'
	data = {'course':course, 'book':book, 'roll':roll}
	r = requests.post(url, data=data)
	response = r.text
	if response == "Yes":
		print "Yo"


# listLenders('CS204', 'Introduction to Algorithms')
# deleteLender('140101063', 'CS204', 'Introduction to Algorithms')