"""@package docstring
Documentation for this module.

This module has functions to fetch and update book lenders' list.
"""

import requests


def lendBook(roll, contact, course, book):
	"""Function that completes the lending process of a book.
	Takes input the roll number, contact number, course and book and stores the info on the database
	"""
	url = 'http://172.16.115.76/lendbook.php'
	data = {'roll':roll, 'contact':contact, 'course':course, 'book':book}
	r = requests.post(url, data=data)


def listLenders(course, book):
	"""Function to return the roll number and contact number of all the lenders of a given book
	"""
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
	"""Function to remove the entry from the lenders database
	"""
	url = 'http://172.16.115.76/deletelenders.php'
	data = {'course':course, 'book':book, 'roll':roll}
	r = requests.post(url, data=data)
	response = r.text
	if response == "Yes":
		print "Yo"


# listLenders('CS204', 'Introduction to Algorithms')
# deleteLender('140101063', 'CS204', 'Introduction to Algorithms')