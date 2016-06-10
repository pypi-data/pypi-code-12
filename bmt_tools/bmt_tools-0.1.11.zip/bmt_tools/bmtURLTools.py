def soupifyURL(url):
    from bs4 import BeautifulSoup as BS
    
    request = requestURL(url)
    return BS(request.text,'html.parser')

def requestURL(url):
    from requests import get
    return get(url)

def jsonURL(url):
    request = requestURL(url)
    return request.json()

def getRatingVotes(url):
    import re
    
    cont = 0
    while cont==0:
        try:
            soup = soupifyURL(url)
            cont = 1
        except:
            print("error in URL parsing")

    spanRating = soup.find_all('span',{'itemprop':'ratingValue'})
    spanVotes = soup.find_all('span',{'itemprop':'ratingCount'})
    reCheck = re.findall('[0-9]*\.[0-9]/10[\s\(from]*[0-9\,]{1,}', soup.text)
    rating = 0
    votes = 0
    if len(spanRating)==1 and len(spanVotes)==1:
        rating = float(spanRating[0].text)
        votes = int(spanVotes[0].text.replace(',',''))
    elif len(reCheck)==1:
        rString,vString = reCheck[0].split('/10')
        rating = float(rString)
        votes = int(''.join([a for a in vString if a.isdigit()]))
    return rating,votes,[len(spanRating),len(spanVotes),len(reCheck)]
