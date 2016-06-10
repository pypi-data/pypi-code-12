def WikiSearch():
    from bmtURLTools import soupifyURL

    correct = 'no'
    while correct == 'no':
        searchTerm = input("What would you like to search?")
        url = getWikiURL(searchTerm)

        WikiSoup = soupifyURL(url)

        results = getWikiResults(WikiSoup)

        correct = getCorrectResult(searchTerm, results)

    return results[int(correct)].find('a')['href']


def getWikiURL(searchTerm):
    return 'http://en.wikipedia.org/w/index.php?title=Special%3ASearch&search=' + \
          searchTerm.replace(' ','+') + '&fulltext=Search'

def getWikiResults(WikiSoup):
    return WikiSoup.find_all('div','mw-search-result-heading')

def getCorrectResult(searchTerm, results):
    resultOptions = printWikiResults(results)
    correct = input("title = " + searchTerm + "; Are any of these correct? (number or \"no\")")
    if correct not in [str(a) for a in resultOptions]+["no"]:
        correct = "no"
    return correct

def printWikiResults(results):
    resultOptions = range(min([10,len(results)]))
    for i in resultOptions:
        print(str(i)+': '+results[i].text)
    return resultOptions