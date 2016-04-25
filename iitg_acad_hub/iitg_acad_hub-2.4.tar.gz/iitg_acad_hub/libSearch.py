import requests
from bs4 import BeautifulSoup as bs

def splitAndJoin(text):
	"""Function that returns a string formed after replacing all the white spaces of the given input string(text) with a single space
	"""
	return " ".join(text.split()).rstrip().lstrip()

def libgenSearch(book):
	"""Function that returns the libgen download link for a given book. 
	Input is a list of length 2 with first entry as book name and second as author
	If not found, string "None" is returned.
	"""
	return "None" #returning none for now, below is the main function
	# return "https://www.google.com"
	name = book[0] #getting the name of the book
	author = book[1] #getting the authors
	url = "http://gen.lib.rus.ec/search.php?req="+name+" "+author+"&open=0&view=simple&phrase=1&column=def"
	source_code = requests.get(url)
	#making the request
	plain_text = source_code.text
	# print url
	soup = bs(plain_text, "lxml") #using BS4 to parse the text
	table = soup.find('table', {'class':'c'}) #fidning the appropriate table
	links = table.findAll('a') #finding the link
	link = ""
	# print links
	for i in links:
		if 'book/index.php?' in i['href']:
			link = i
			break 
	if link is "":
		return "None"

	url = "http://gen.lib.rus.ec/"+link['href'] #going to the correct url
	# print url
	soup = bs(requests.get(url).text, "lxml") 
	table = soup.find('table')
	link = table.find('a') #finding the first link in the table
	
	soup = bs(requests.get(url).text, "lxml")
	table = soup.find('table') 
	link = table.find('a') #getting the final download link
	print "http://libgen.io"+link['href']

	return "http://libgen.io"+link['href'] #returning the final link

def librarySearch(book):
	"""Function that returns the IITG library location for a given book. 
	Input is a list of length 2 with first entry as book name and second as author.
	If not found, string "None" is returned.
	"""
	return "None"
	name = book[0]
	author = book[1]
	url = "http://bidya.iitg.ernet.in:8680/opac/search/searchResult.html?searchdata="+name+"&qcon1=1&cat1=1&con1=1&searchdata2="+author+"&qcon2=1&cat2=0&con2=1&searchdata3=&qcon3=1&cat3=7&docType=BK&fromTF1=&toTF1=&sortBy=-1&level1=&physicalForm1=&sourceTF1=&subjectCode1=&subjectDocType1=&locationTF1=&db=8&databaseList=&search_selectedSites=1"
	#seraching for the book in the library
	soup = bs(requests.get(url).text,"lxml")
	#parsing the post request
	bookdiv = soup.find('div', {'class':'recordObjectDiv'})
	#finding the correct div
	if bookdiv is None:
		return "None"

	bookInfo = bookdiv.findAll('p')
	#finding the p tag with lib location info
	return splitAndJoin(bookInfo[2].text)
	#returning the text

# librarySearch(["Digital Design", "M Mano"])