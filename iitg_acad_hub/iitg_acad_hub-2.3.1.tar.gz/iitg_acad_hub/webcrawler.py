import requests
from bs4 import BeautifulSoup
from libSearch import libgenSearch, librarySearch
import string 

# Function to get rid of all the white spaces in the text
def stripAll(text):
	strippedText = ''.join(text.split())
	return strippedText
# Function to first split the string of all the white spaces and 
# then join the splitted list with a space
def splitAndJoin(text):
	return " ".join(text.split()).rstrip().lstrip()

# remove punctuations and "and" from the book name or author name
def removePunc(text):
	for c in string.punctuation:
		if c is not '.':
			text = text.replace(c, "")
	return text.replace(" and ", " ")

# For searching in institute library, get only the first author
def getFirstAuthor(text):
	if "," in text:
		authors = text.split(",")
		author = splitAndJoin(authors[0])
	elif " and " in text:
		authors = text.split(" and ")
		author = splitAndJoin(authors[0])
	else:
		author = splitAndJoin(text)
	author = author.replace(".", " ")
	temp = author.split()
	temp2 = []
	for word in temp:
		if len(word) > 1:
			temp2.append(word)
	return " ".join(temp2)


# given a row that contains info about some course, 
# return the relevant rows of the table that contain all that course's books and reference texts
def getBooks(row):
	para = row.findAll('p')

	bookPos = len(para)
	referencePos = len(para)
	for i in range(len(para)):
		if "Texts" in para[i].text:
			bookPos = i
			break
	for i in range(len(para)):
		if "References" in para[i].text:
			referencePos = i
			break


	books = []
	for i in range(bookPos+1, referencePos):
		if stripAll(para[i].text) != "":
			books.append(para[i])

	ref = []
	for i in range(referencePos+1, len(para)):
		if stripAll(para[i].text) != "":
			ref.append(para[i])
	return (books, ref)

# get all the books for the courses in the courses list and their authors, publications, 
# library search and download link
def getCourseBooks(courses, soup):
	# Table that contains detailed course info on the intranet page
	tables = soup.findAll('table', {'class':'MsoTableGrid'}) 
	rows = []
	for table in tables: # if there are more than 1 table
		rows += table.findAll('tr')

	strippedRows = []
	for row in rows:
		strippedRows.append(stripAll(row.text))
	# for row in rows:
	spans = rows[2].findAll('span', {'style':'font-size:10.0pt'+'*'})
	# print spans 
	courseBooks = [] # list of all the relevant course books
	for course in courses:
		for i in range(len(rows)):
			if courses[course]["code"] != "" and courses[course]["code"] in strippedRows[i][:10]:
				# if this row contains this course's info, 
				# get all the rows of the table containg books and references available for it
				books, ref = getBooks(rows[i]) 

				# Now, get all the relevant info for a book
				for book in books:
					name = book.find('i')	
					try:
						title = name.text
					except:
						continue
					title = splitAndJoin(title)
					row = ".".join(book.text.split(".")[1:])
					row = splitAndJoin(row)
					pos = row.find(title)
					author = row[:pos-2]
					pub = row[pos+len(title)+1:]
					# print title + "\t" + author + "\t" + pub
					downloadLink = unicode(libgenSearch([removePunc(title), removePunc(author)]))
					libraryInfo = unicode(librarySearch([removePunc(title), getFirstAuthor(author)]))
					# print [removePunc(title), getFirstAuthor(author)]
					courseBooks.append((course, courses[course]["code"], title, author, pub, libraryInfo, downloadLink))
				 
				break
	# print courseBooks
	return courseBooks





# Function that parses all the courses and their info and return a list of all 
# the books in the relevant courses by calling the function getcourseBooks
def showBooks(dept, sem, find="books"):
	sem = int(sem)
	if dept=="bdes":
		url= "http://shilloi.iitg.ernet.in/~acad/intranet/CourseStructure/bdes2013onwards.htm"
	else:	
		url = "http://shilloi.iitg.ernet.in/~acad/intranet/CourseStructure/"+dept.lower()+"UG2013onwards.htm"
	source_code = requests.get(url)
	plain_text = source_code.text

	soup = BeautifulSoup(plain_text, "lxml")

	# This table contains the list of courses according to the semester 	
	table = soup.find('table', {'class':'MsoNormalTable'})
	rows = table.findAll('tr')
	semTitleRows=[]
	for i in range(len(rows)):
		text = rows[i].text
		if "Semester" in text:
			semTitleRows.append(i)
			continue
	semTitleRows.append(len(rows))
	
	# which row to look at for a given sem
	rowSemEquivalent = sem/2 - (sem+1)%2

	# This list contains all the course info in the form 
	# courses["name of course"] = {"code": , "L": , "T": , "P": , "C": }
	courses = {} 
	courseList = []
	for i in range(semTitleRows[rowSemEquivalent]+1, semTitleRows[rowSemEquivalent+1]-1):
		td = rows[i].findAll('td')
		info = []
		if sem%2 == 1:
			if stripAll(td[0].text) == "" and stripAll(td[1].text) == "":
				continue
			for j in range(0,6):
				strippedText = splitAndJoin(td[j].text)
				info.append(strippedText)
		else:
			if len(td)<=8 or stripAll(td[7].text) == "" and stripAll(td[8].text) == "":
				continue
			for j in range(7,len(td)):
				strippedText = splitAndJoin(td[j].text)
				info.append(strippedText)

		info[0] = stripAll(info[0])
		courses[info[1]] = {"code":info[0], "L":info[2], "T":info[3], "P":info[4], "C":info[5]}
		courseList.append(info)

	
	if(find == "courses"): 		# If only the course list needs to be returned
		return courseList
	else:						# Return all the relevant course books
		return getCourseBooks(courses, soup) 

# print showBooks("ECE", 1, "books")