#-*- coding: utf-8 -*-
from datetime import date, datetime
import bs4, nltk, os, pytz, re, time, urlparse
from nltk.corpus import wordnet
import numpy, random
from bs4 import BeautifulSoup
from bscrp import isJavaScript
#from pattern.en import pluralize, singularize
from location_extractor import extract_locations
from stop_words import get_stop_words
from nltk.tree import Tree
from bs4.element import NavigableString
from titlecase import titlecase
from re import findall, finditer, MULTILINE, sub
from re import compile as re_compile
#from interviews import *

from acronyms import *
from arabic import *
from dates import *
from bnames import *
from english import *
from headers import *
from locations import *
from organizations import *
from pagination import *
from titles import *
from transliterate import *
from variate import *

# uses topic in the NLP sense
# takes in a list of words for an LDA analysis
# and returns one word
#def getTopic(listOfWords):
pathToBnlpInit = os.path.dirname(os.path.realpath(__file__))

stopwords = get_stop_words("en")

try:
    with open(pathToBnlpInit + '/custom.txt') as f:
        for line in f:
            stopwords.append(line.rstrip().lower())    
except:
    stopwords = []


def isGibberishListOrSet(lst):
    length = len(lst)
    count = 0
    for string in lst:
        count += isGibberishString(string)
    percentage = float(count) / float(length)
    print "percentage gibberish is", percentage
    return percentage > 0.3

def isGibberishString(string):
    if search("&[a-z]", string) or search(",[a-z]", string) or search("[A-Za-z]\d[A-Za-z]", string) or search(";[A-Za-z]", string) or search("[a-z]\d{3,}", string):
        return True
    else:
        return False

def isGibberish(inpt):
    if isinstance(inpt, list) or isinstance(inpt, set):
        return isGibberishListOrSet(inpt)
    elif isinstance(inpt, str):
        return isGibberishString(inpt)

# return regexp that we can guess matches domain
def guess_domain_as_string(text, translate=None):
    fuzzy_string = get_fuzzy_string(text)
    acronym = getAcronymForWordPhrase(text)
    pattern = "(?:" + fuzzy_string + "|" + acronym
    if translate:
        translation = translate(text)
        fuzzy_string = get_fuzzy_string(translation)
        acronym = getAcronymForWordPhrase(translation)
        pattern += "|" + fuzzy_string + "|" + acronym
    pattern += ")"
    regexp = re_compile(pattern, IGNORECASE|UNICODE)
    return regexp

def get_sentences(text):
    return findall("[^\.\n]+",text)

def get_paragraphs(text):
    return findall("[^\n\r]+",text)

def get_paragraph(text, index):
    for paragraph in finditer("[^\n\r]+", text):
        if paragraph.start() < index < paragraph.end():
            return paragraph.group(0)

def get_first_sentence(text):
    return get_sentences(text)[0].strip()
def get_first_paragraph(text):
    return get_paragraphs(text)[0].strip()

def get_last_sentence(text):
    return get_sentences(text)[-1].strip()
def get_last_paragraph(text):
    return get_paragraphs(text)[-1].strip()

def isEntityInText(aliases, text):
    if isinstance(text, str):
        text = unicode(text, encoding="utf-8")

    for alias in aliases:
        if isinstance(alias, str):
            alias = unicode(alias, encoding="utf-8")
        if alias.count(u" ") > 0 and alias in text:
            return True
    return False

def getKeyWordsFromUrl(url):

    #first check if this the type of url for which we can get keywords
    if isUrlToArticle:
       pass
    else:
        return False

#def removeAllLowerCaseWords(string):

def isRegular(string):
    excerpt = string[:200]
    excerpt_split = excerpt.split()
    titled = 0
    uppered = 0
    lowered = 0
    for word in excerpt_split:
        if string == titlecase(word):
            titled += 1
        elif word.isupper():
            uppered += 1
        elif word.islower():
            lowered += 1

    percentageLowered = float(lowered) / float(len(excerpt_split))
    if percentageLowered > .4:
        return True
    else:
        return False


def getKeywordsFromString(string):
#    print "starting getKeywordsFromString with:", string[:50],"..."
    if isTitle(string):
#        print 'string is title'
        string = string.replace("\"","").replace(".  ", ". ").replace("'s "," ").replace(",","")
#        print "\treplaced is ", string
        acronyms = re.findall(r"[A-Z]{2,}", string)
        titled = re.findall(r"(?<!\.\s)[A-Z][a-z]{2,}", string)
        keywords = acronyms + titled
    elif isSlug(string):
        keywords = []
    elif isRegular(string):
#        print "\tstring is regular text"
        string_replaced = string.replace("\"","").replace(".  ", ". ").replace("'s "," ") 
#        print "\treplaced is ", string_replaced
        acronyms = re.findall(r"[A-Z]{2,}", string_replaced)
	titled = re.findall(r"(?<!\.\s)[A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})*", string_replaced)
        keywords = list(set(acronyms + titled))
    else:
        keywords = []
#    print "finishing getKeywordsFromString with", keywords
    return keywords


    """via nltk
    keywords = []

    tokens = nltk.word_tokenize(string)
    tagged = nltk.pos_tag(tokens)
    res = entities = nltk.ne_chunk(tagged)
    print "res is", res
    for entity in entities:
        if isinstance(entity, Tree):
            print "entity is", entity
    
    print "res is", res
    """

#make sure to clean html
def getKeywordsFromHtmlAsString(htmlAsString):
    soup = BeautifulSoup(htmlAsString)
    soup_title = str(soup.title).replace("<title>","").replace("</title>","")
    return getKeywordsFromString(soup_title)
    

# checks to see if two lists have at least one element in common
def overlap(alpha, beta):
    print "starting overlap with", alpha, beta
    result = set(alpha) & set(beta)
    print "result is", result
    return result

# groups LDA output into lists with different ideas separated
# e.g., so if list is sea, ocean, travel, ship, water
# result would be [sea,ocean,water] [travel] [ship]
def groupWords(words):
    thesaurus = {}
    for word in words:
        thesaurus[word] = getSynonymsForWord(word)
    print "thesaurus are", thesaurus

    groups = []
    for key in thesaurus:
        synonyms = thesaurus[key]
        merged = False
        for group in groups:
            if overlap(synonyms, group):
                merged = True
                group.extend(synonyms)
        if not merged:
            groups.append(synonyms)

    results = []
    for group in groups:
        results.append(list(set(group)))

    print "groups are ", results

    lookupByLists(results)

def find_bigrams(input_list):
    bigram_list = []
    for i in range(len(input_list)-1):
        bigram_list.append((input_list[i], input_list[i+1]))
    return bigram_list

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def find_allgrams(input_list):
    result = []
    for i in range(len(input_list)+1):
        result.extend(find_ngrams(input_list, i)) 
    return result

def getPermutations(input_list):
    if isinstance(input_list, str) or isinstance(input_list, unicode):
        input_list = input_list.split(" ")
    output = []
    for listOfGrams in find_allgrams(input_list):
       output.append(" ".join(listOfGrams)) 
    return output
    

def getVariationsOfName(name, transliteratedFromArabic=False):
    names = [name]
    if re.search(r"(^|[ ])al", name, re.IGNORECASE):
#        print "al in name_lower"

        for tup in [("al",True), ("al ", True), ("Al-", False), ("Al-", True),  ("al-", True), ("Al ", True)]:

            variation = variateAl(name, tup[0], tup[1])
            if variation not in names:
                names.append(variation)

            variation_elided = elide(variation)
            if variation_elided not in names:
                names.append(variation_elided)
     

#        print "names are", names

    # add generic name, but without suffix
    names.append(getNameWithoutSuffix(name))

    #without first name initial
    pattern = "^\w\.\W"
    if re.search(pattern, name):
        result = re.sub(pattern,"", name)
        names.append(result)
        names.append(getNameWithoutSuffix(result))

    #without middle initial
    pattern = "\W\w\.(?=\W)"
    if re.search(pattern, name):
        result = re.sub(pattern,"", name)
        names.append(result)
        names.append(getNameWithoutSuffix(result))

    #just nickname
    nickName = getNickName(name)
    if nickName:
        names.append(nickName)

    #just lastname
    # commenting this out for now because too many false positives!!!!
    """
    lastName = getLastName(name)
    if lastName:
        names.append(lastName)
    """

    #nickName + lastName
    if nickName and lastName:
        names.append(nickName + " " + lastName)

    return list(set(names))

def extract_entities(text):
    print "starting extract_entities"
    results = []
    for sent in nltk.sent_tokenize(text):
        print "for sent", sent
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if "label" in dir(chunk):
                if chunk.label() in ["PERSON", "ORGANIZATION"]:
                    results.append((chunk.label(), ' '.join(c[0] for c in chunk.leaves())))
    print "results are", results
    return results


def isDate(text):
    if re.search("\d{4}", text):
        return True
    else:
        return False

def isUnknown(text):
    if isDate(text):
        return False
    elif isLocation(text):
        return False
    elif isOrganization(text):
        return False
    elif isPressRelease(text):
        return False
    elif isPosition(text):
        return False
    else:
        return True

def getPeopleFromText(text):
    people = []
    for tag, token in extract_entities(text):
        if tag == "PERSON":
            people.append(clean(token.replace("Spokesperson",""))) 
    return people

def getFirstDateFromText(text):
    print 'starting getPageDate'
    datetimeobj = None
    result = re.search('(\d{4})-(\d{2})-(\d{2})', text, re.IGNORECASE)
    if result is not None and ((result.group(2) <= 31 and result.group(3) <= 12) or (result.group(2) <= 12 and result.group(3) <= 31)):
        date = result.group(0)
        datetimeobj = datetime.strptime(date, '%Y-%m-%d')
        return datetimeobj
    result = re.search('(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{2}, \\d{4}', text, re.IGNORECASE)
    if result is not None:
        date = result.group(0)
        datetimeobj = datetime.strptime(date, '%a, %b %d, %Y')
        return datetimeobj
    print 'finishing getPageDate'
    return datetimeobj


def getDateFromTextArabic(text):

    d = {}

    #january
    d[u'\u0643\u0627\u0646\u0648\u0646 \u0627\u0644\u062b\u0627\u0646\u064a'] = 1
    d[u'\u064a\u0646\u0627\u064a\u0631'] = 1
    d[u'\u0623\u064a \u0627\u0644\u0646\u0627\u0631'] = 1
    d[u'\u062c\u0627\u0646\u0641\u064a'] = 1
    d[u'\u064a\u0646\u0627\u064a\u0631'] = 1

    #february
    d[u'\u0634\u0628\u0627\u0637'] = 2
    d[u'\u0641\u0628\u0631\u0627\u064a\u0631'] = 2
    d[u'\u0627\u0644\u0646\u0648\u0627\u0631'] = 2
    d[u'\u0641\u064a\u0641\u0631\u064a'] = 2

    # march
    d[u'\u0622\u0630\u0627\u0631'] = 3
    d[u'\u0645\u0627\u0631\u0633'] = 3
    d[u'\u0627\u0644\u0631\u0628\u064a\u0639'] = 3
    d[u'\u0645\u0627\u0631\u0633'] = 3

    #april
    d[u'\u0646\u064a\u0633\u0627\u0646'] = 4
    d[u'\u0623\u0628\u0631\u064a\u0644'] = 4
    d[u'\u0625\u0628\u0631\u064a\u0644'] = 4
    d[u'\u0627\u0644\u0637\u064a\u0631'] = 4
    d[u'\u0623\u0641\u0631\u064a\u0644'] = 4
 
    #may
    d[u'\u0623\u064a\u0627\u0631'] = 5
    d[u'\u0645\u0627\u064a\u0648'] = 5
    d[u'\u0627\u0644\u0645\u0627\u0621'] = 5
    d[u'\u0645\u0627\u064a'] = 5

    #june
    d[u'\u062d\u0632\u064a\u0631\u0627\u0646'] = 6
    d[u'\u064a\u0648\u0646\u064a\u0648'] = 6
    d[u'\u064a\u0648\u0646\u064a\u0629'] = 6
    d[u'\u0627\u0644\u0635\u064a\u0641'] = 6
    d[u'\u062c\u0648\u0627\u0646'] = 6

    #july
    d[u'\u062a\u0645\u0648\u0632'] = 7
    d[u'\u064a\u0648\u0644\u064a\u0648'] = 7
    d[u'\u064a\u0648\u0644\u064a\u0629'] = 7
    d[u'\u0646\u0627\u0635\u0631'] = 7
    d[u'\u062c\u0648\u064a\u0644\u064a\u0629'] = 7
    d[u'\u064a\u0648\u0644\u064a\u0648\u0632'] = 7

    #august
    d[u'\u0622\u0628'] = 8
    d[u'\ufe82\ufe91'] = 8
    d[u'\u0623\u063a\u0633\u0637\u0633'] = 8
    d[u'\u0647\u0627\u0646\u064a\u0628\u0627\u0644'] = 8
    d[u'\u0623\u0648\u062a'] = 8
    d[u'\u063a\u0634\u062a'] = 8

    #september
    d[u'\u0623\u064a\u0644\u0648\u0644'] = 9
    d[u'\u0633\u0628\u062a\u0645\u0628\u0631'] = 9
    d[u'\u0627\u0644\u0641\u0627\u062a\u062d'] = 9
    d[u'\u0633\u0628\u062a\u0645\u0628\u0631'] = 9
    d[u'\u0634\u062a\u0645\u0628\u0631'] = 9

    #october
    d[u'\u062a\u0634\u0631\u064a\u0646 \u0627\u0644\u0623\u0648\u0644'] = 10
    d[u'\u0623\u0643\u062a\u0648\u0628\u0631'] = 10
    d[u'\u0627\u0644\u062a\u0645\u0648\u0631'] = 10
    d[u'\u0627\u0644\u062b\u0645\u0648\u0631'] = 10
    d[u'\u0623\u0643\u062a\u0648\u0628\u0631'] = 10

    #november
    d[u'\u062a\u0634\u0631\u064a\u0646 \u0627\u0644\u062b\u0627\u0646\u064a'] = 11
    d[u'\u0646\u0648\u0641\u0645\u0628\u0631'] = 11
    d[u'\u0627\u0644\u062d\u0631\u062b'] = 11
    d[u'\u0646\u0648\u0641\u0645\u0628\u0631'] = 11
    d[u'\u0646\u0648\u0646\u0628\u0631'] = 11

    #december
    d[u'\u0643\u0627\u0646\u0648\u0646 \u0627\u0644\u0623\u0648\u0644'] = 12
    d[u'\u062f\u064a\u0633\u0645\u0628\u0631'] = 12
    d[u'\u0627\u0644\u0643\u0627\u0646\u0648\u0646'] = 12
    d[u'\u062f\u064a\u0633\u0645\u0628\u0631'] = 12
    d[u'\u062f\u062c\u0645\u0628\u0631'] = 12

    result = re.search(ur'(?P<day>\d{1,2}) (?P<month>\u0643\u0627\u0646\u0648\u0646 \u0627\u0644\u062b\u0627\u0646\u064a|\u0634\u0628\u0627\u0637|\u0622\u0630\u0627\u0631|\u0646\u064a\u0633\u0627\u0646|\u0623\u064a\u0627\u0631|\u062d\u0632\u064a\u0631\u0627\u0646|\u062a\u0645\u0648\u0632|\u0622\u0628|\u0623\u064a\u0644\u0648\u0644|\u062a\u0634\u0631\u064a\u0646 \u0627\u0644\u0623\u0648\u0644|\u062a\u0634\u0631\u064a\u0646 \u0627\u0644\u062b\u0627\u0646\u064a|\u0643\u0627\u0646\u0648\u0646 \u0627\u0644\u0623\u0648\u0644)\u060c (?P<year>\d{4})', text)
    if result:
        return datetime(int(result.group("year")), d[result.group("month")], int(result.group("day")), tzinfo=pytz.UTC)


def getDateFromTextOld(text):
    print "starting getDateFromText with, ", type(text)
    print dir(text)

    year = '\\d{4}'
    months = '(January|February|March|April|May|June|July|August|September|October|November|December)'
    day = '\\d{1,2}'


    pattern = months + " " + day + ", " + year
    print "pattern is", pattern
    result = re.search(pattern, text) 
    if result is not None:
        date = result.group(0)
        print "date is", date
        dateObj = datetime.strptime(date, '%B %d, %Y') 
        print "dateObj is", dateObj
        dateObjTz = dateObj.replace(tzinfo=pytz.UTC)
        return dateObjTz

    #sometimes there's a typo and no comma
    pattern = months + " " + day + " " + year
    print "pattern is", pattern
    result = re.search(pattern, text) 
    if result is not None:
        date = result.group(0)
        print "date is", date
        dateObj = datetime.strptime(date, '%B %d %Y') 
        print "dateObj is", dateObj
        dateObjTz = dateObj.replace(tzinfo=pytz.UTC)
        return dateObjTz

    #day month year
    pattern = day + " " + months + " " + year
    print "pattern is", pattern
    result = re.search(pattern, text) 
    if result is not None:
        date = result.group(0)
        print "date is", date
        dateObj = datetime.strptime(date, '%d %B %Y') 
        print "dateObj is", dateObj
        dateObjTz = dateObj.replace(tzinfo=pytz.UTC)
        return dateObjTz

    #day month, year
    pattern = day + " " + months + ", " + year
    print "pattern is", pattern
    result = re.search(pattern, text) 
    if result is not None:
        date = result.group(0)
        print "date is", date
        dateObj = datetime.strptime(date, '%d %B, %Y') 
        print "dateObj is", dateObj
        dateObjTz = dateObj.replace(tzinfo=pytz.UTC)
        return dateObjTz

def doesGroupExist(match_object, group_name):
    try:
        match_object("group_name")
        return True
    except:
        return False
    
"""
def x(text, reference_date=None):
    dates = []
    for pattern in patterns.dates:
        print "pattern is", pattern
        p = re.compile(pattern)
        print "p is", p
        for m in re.finditer(pattern, text, re.IGNORECASE):
            print "m is", m

            if doesGroupExist(m,"year"):
                year = m.group("year")
            elif reference_date:
                year = reference_date.year
            else:
                year = datetime.now().year


            if doesGroupExist(m,"month"):
                month = m.group("month")
            elif reference_date:
                month = reference_date.month
            else:
                month = datetime.now().month

            if doesGroupExist(m,"day"):
                day = m.group("day")
            elif reference_date:
                day = reference_date.day
            else:
                day = datetime.now().day

            dates.append(date(year, month, day))

    print "dates are", dates
""" 

def getDatesFromText(text, pagedate):
    print 'starting getDatesFromText'

    days_abbreviated = '(Mon|Tue|Wed|Thu|Fri|Sat|Sun)'
    months_abbreviated = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    months = '(january|february|march|april|may|june|july|august|september|october|november|december)'
    year = '\\d{4}'
    result = re.search('\(' + months + ' ' + year + '-\)', text, re.IGNORECASE)
    if result is not None:
        print 'a'
        date = result.group(0)
        print 'date is', date
        start = datetime.strptime(date, '%B %Y-)')
        print 'datetimeobj is', start
        end = datetime.now()
        return (start, end)
    result = re.search('(\\d{4}-\\d{2}-\\d{2})', text, re.IGNORECASE)
    if result is not None:
        print 'b'
        date = result.group(0)
        print 'date is', date
        datetimeobj = datetime.strptime(date, '%Y-%m-%d')
        print 'datetimeobj is', datetimeobj
        return (datetimeobj, datetimeobj)
    result = re.search(days_abbreviated + ', ' + months_abbreviated + ' \\d{2}, \\d{4}', text, re.IGNORECASE)
    if result is not None:
        print 'c'
        date = result.group(0)
        print 'date is', date
        datetimeobj = datetime.strptime(date, '%a, %b %d, %Y')
        print 'datetimeobj is', datetimeobj
        return (datetimeobj, datetimeobj)
    result = re.search('\\d{1,2} ' + months + ' ' + year, text, re.IGNORECASE)
    if result is not None:
        print 'd'
        date = result.group(0)
        print 'date is', date
        datetimeobj = datetime.strptime(date, '%d %B %Y')
        print 'datetimeobj is', datetimeobj
        return (datetimeobj, datetimeobj)
    result = re.search(months + ' ' + year, text, re.IGNORECASE)
    if result is not None:
        print 'e'
        date = result.group(0)
        print 'date is', date
        datetimeobj = datetime.strptime(date, '%B %Y')
        print 'datetimeobj is', datetimeobj
        return (datetimeobj, datetimeobj)
    result = re.search(months, text, re.IGNORECASE)
    if result is not None:
        print 'f'
        month = result.group(0)
        monthAsNumber = time.strptime(month, '%B').tm_mon
        if month <= pagedate.month:
            year = pagedate.year
        else:
            year = pagedate.year - 1
        datetimeobj = datetime(year, monthAsNumber, 1)
        return (datetimeobj, datetimeobj)
    result = re.search('(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)', text, re.IGNORECASE)
    if result is not None:
        print 'g'
        day = result.group(0)
        dayAsNumber = time.strptime(day, '%A').tm_mday
        datetimeobj = datetime(pagedate.year, pagedate.month, dayAsNumber)
        return (datetimeobj, datetimeobj)
    result = re.search(year, text, re.IGNORECASE)
    if result is not None:
        print 'h'
        date = result.group(0)
        if int(date) > 1900 and int(date) < 3000:
            print 'date is', date
            datetimeobj = datetime.strptime(date, '%Y')
            print 'datetimeobj is', datetimeobj
            return (datetimeobj, datetimeobj)
    return (pagedate, pagedate)

"""
def clean(text):
    if isinstance(text, str):
        text = text.decode("utf-8")
    elif isinstance(text, NavigableString):
        text = unicode(text)

    soup = BeautifulSoup(text)
    text = soup.get_text()
""" 

def clean(string):
    if isinstance(string, str):
        string = unicode(string, encoding="utf-8")
    # NavigableString is an instance of unicode, so no need to convert to byte str
    elif isinstance(string, NavigableString):
        string = unicode(string)
   
    replaced = string.replace(u"“", u"\"").replace(u"’", u"'").replace(u"”", u"\"").replace(u"”", u"\"").replace(u"—", u"-").replace(u"&apos;", u"'").strip(u"]").strip(u"[").replace(u"\xc2\xa0", u" ").replace(u"\xa0", u" ").replace(u"\u0194", u'a').replace(u"‘",u"'").replace(u"…",u"...")

    # remove anything between comments
    replaced = sub("\/\*{0,5}.*\*\/", " ", replaced)

    # remove anything between script tags
    replaced = sub("<script[^>]*>[^<]</script>", " ", replaced)

    #replaces span tags with spaces
    replaced = sub("</?span([^>]){0,100}>", " ", replaced)

    #replaces any other tags with new lines
    replaced = sub("</?([a-z]{1,7})([^>]){0,9999}>", "\r\n", replaced) 
    replaced = sub("(?<=\w)( , )(?=\w)", ", ", replaced)
    replaced = sub("(?<=\w)( ')(?=\w)", "'", replaced)

    # remove extra carriage returns (i.e., more than one line between paragraphs)
    replaced = sub(r"(\r|\n)(\r|\n| )+(\r|\n)",r"\r\n\r\n",replaced)

    #strip all starting and trailing white space
    while True:
        old_length = len(replaced)
        replaced = replaced.strip().strip(u"\xc2").strip(u"\xa0").strip()
        new_length = len(replaced)
        if new_length == old_length:
            break

    #cleaned = replaced.encode("utf-8", errors="ignore")
    #print "finishing clean with:", cleaned
    return replaced

def pos_tag(tokens):
    tagged = nltk.pos_tag(tokens)
    print "tagged is", type(tagged)
    retagged = []

    # tag indirect speech verbs

    #indirect speech, quoted speech
    listOfIndirectSpeechVerbs = ['announced', 'say','said','called','calls','noted','noting','responded', 'signed', 'spoken', 'written']
    skip = False
    for index, tup in enumerate(tagged):
        if skip:
            #print "skipping"
            skip = False
        else:
            #p("\nindex is")
            token, tag = tup
            #"(", token, ",", tag, ")"
            if token in listOfIndirectSpeechVerbs:
                retagged.append((token,tag, "IndirectSpeech"))
            elif token == "that" and index > 0 and len(retagged[index-1]) == 3 and retagged[index-1][2] == "IndirectSpeech":
                retagged.append((token,"Complementizer"))
            elif token == "Dels" and len(tagged) > index + 1 and tagged[index+1][0] == ".":
                retagged.append((token + ".", tag))
                skip = True
            else:
                retagged.append((token,tag))

    #print "retagged is", retagged

    return retagged

def getPartOfTree(tree, label):

    found = []

    for part in tree:
#        print "part is", part
        if isinstance(part, nltk.tree.Tree):
            if part.label() == label:
                found.append(part)
            deep = getPartOfTree(part, label)
            if deep:
                found.extend(deep)
 
        elif len(part) >= 2 and part[1] == label:
            found.append(part[0])

    return found


def getStatementsFromText(text, language=None):
    if language:
        if language == "English":
            return getStatementsFromTextEnglish(text)
        elif language == "Arabic":
            return getStatementsFromTextArabic(text)
    else:
        if isEnglish(text):
            return getStatementsFromTextEnglish(text)
        else:
            return getStatementsFromTextArabic(text)


    
def getStatementsFromTextEnglish(text):
    print "starting getStatementsFromText with", type(text)
    print text
    text = clean(text)
    print "text after clean is", text
#    paragraphs = text.split(u"\n\n")
#    print "paragraphs are", len(paragraphs)
    tokens = nltk.word_tokenize(text)
    print "tokens are", tokens
    tagged = pos_tag(tokens)
    print "tagged is", tagged
    statements = []
    grammar = """
              Colon: {<:>}
              Adverbs: {<RB>+}
              NNPS: {<NNP>+}

              AdjectivePhrase: {<Adverbs><JJ>}

              Infinitive: {<TO><VB>}
              Passive: {<VBD><VBN>}
              PresentPerfect: {<VBP><VBN>}
              PresentProgressive: {<VBZ><VBG>}

              Verb: {<VBD|PresentPerfect|PresentProgressive|IndirectSpeech>}
              VerbPassive: {<Passive><IN>}

              NounPhrase: {<DT|PP\$>?<CD>*<JJ.*>*<N.*>+}
                          {<PRP>}
              NounPhraseConjunctive: {<NounPhrase>(<CC|,><NounPhrase>)+}
              PrepositionalPhrase: {<IN|TO><NounPhrase>}
              Quote: {<``><[^''].*>*<''>}
                    <Colon>{<.*>*}

              VerbPhrase: {<Verb><Adverbs>}
                          {<Adverbs><Verb><IN>}


              Subject: {<NounPhrase>}<Verb>
                       <VerbPassive>{<NounPhrase.*>}
              SubjectPhrase: {<NounPhrase><PrepositionalPhrase>}<Verb|VerbPhrase>

              Object:  {<NounPhrase.*>}<VerbPassive>
              ObjectQ: <Verb>{<Quote>}
                       {<Quote>}<Subject><Verb>

              Clause: {<Object><VerbPassive><Subject.*>}
                      {<Subject.*><Verb><Object>}
              ClauseQ: {<ObjectQ><VerbPassive><Subject.*>}
                       {<Subject.*><Verb><ObjectQ>}
                       {<ObjectQ><Subject><Verb>}

              DependentClause:
                      {<WP|Complementizer><Clause.*>}
              IndependentClause:
                      {<Clause>}

              Sentence: {<IndependentClause>}
    """


#    grammar = """
#              AdverbialPhrase: {<RB>+}
#              Infinitive: {<TO><VB>}
#              PresentPerfect: {<VBP><VBN>}
#              PresentProgressive: {<VBZ><VBG>}
#              Verb: {<VBD|PresentPerfect|PresentProgressive>}
#              NounPhrase: {<DT|PP\$>?<CD>*<JJ.*>*<N.*>+}
#              PrepositionalPhrase: {<IN|TO><NounPhrase>}
#              Quote: {<``><[^''].*>*<''>}
#              Clause: {<NounPhrase><Verb><Quote>}
#                      {<Quote><Verb><NounPhrase>}
#                      {<Quote><NounPhrase><Verb>}
#              """
 
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(tagged)
    print "result is", type(result)

#    grammar = nltk.data.load("file:bgrammar.cfg")
#    grammar = nltk.CFG.fromstring("""
#              S -> NP VP
#              NP -> Det Nom | PropN
#              VP -> V Adj | V NP | V S | V NP PP
#              PP -> P NP
#              PropN ->
#              """)

#    rd_parser = nltk.RecursiveDescentParser(grammar)
#    for tree in rd_parser.parse(ta


    #get clauses with quotes in them

    clauses = getPartOfTree(result, "ClauseQ")
#    print "clauses are", [treeToString(clause) for clause in clauses]

    statements = []
    for clause in clauses:
        subjects = getPartOfTree(clause, "Subject")
        if len(subjects) > 0:
            subject = subjects[0] 
            speakers = getPartOfTree(subject, "NNPS")
            print "speakers are", speakers
            if len(speakers) > 0:
                speaker = treeToString(speakers[0])
                objects = getPartOfTree(clause, "ObjectQ")
                if len(objects) > 0:
                    obj = objects[0]
                    quotes = getPartOfTree(obj, "Quote")
                    print "quotes are", quotes
                    if len(quotes) >= 0:
                        quote = treeToString(quotes[0])
                        statements.append({'speaker': speaker, 'quote': quote})

    print"\n\nstatements are", statements
    return statements

def getProperNounsFromText(text):
    print "starting getProperNounsFromText"
    text = clean(text)
    print "text is", text
    tokens = nltk.word_tokenize(text)
    tagged = pos_tag(tokens)
    properNouns = []
    for tup in tagged:
        if tup[1] in ["NNP", "NNPS"]:
            properNouns.append(tup[0])
    return properNouns

# includes support for Arabic transliterated titled like
# al-Shams
# handles Arabic transliteration where 'a in the middle like Asa'ib
# handles "of the" like Forces of Abu Ibrahim
# wal- like in Jaish al-Muhajireen wal-Ansar
# -i- like in Tehrik-i-Taliban 
def getTitledFromText(text):
    return re.findall(r"(?:\d*(?:st|nd|th)[ ])?(?:al-|ash-|ath-)?[A-Z][a-z(a'|'a)]{2,}(?:(?:\s|-i-)(?:al-|ash-|ath-|bin |of |of the |wal-|wa-)?[A-Z][a-z('a|a')]{2,})*", text)

def getOrgsFromText(text):
    acronyms = getAcronymsFromText(text)
    titled = getTitledFromText(text)
    orgs = [wordphrase for wordphrase in titled if isOrganization(wordphrase) and not isAmbiguousOrg(wordphrase)]
    return orgs

# sees if two terms share the same subject
# i.e. The Federal Elections Commision and the FEC refer to the same thing
def shareSubject(a, b):
    a_terms = generateWordsForSameSubject(a)
    b_terms = generateWordsForSameSubject(b)
    return overlap(a_terms, b_terms)

def generateWordsForSameSubject(subject):
#    print "starting generateWordsForSameSubject with ", subject
    terms = [subject, subject.lower(), subject.upper(), titlecase(subject)]
    terms += pluralize(subject)
    terms += singularize(subject)
    terms += getSynonymsForWord(subject)
    terms = list(set(terms))
#    print "terms are", terms
    return terms


#groupWords(["sea", "ocean", "travel", "boat", "ship"])

#text = """
#President of SNC George Sabra: (speaking in English) What happened the last four, five days was really something unbelievable in Syria.  There were massacres during the last two years in the villages of Jdeidet al-Fadel, Jdeidet Artooz, Artooz, and Moadamia;  More than 500 people were slaughtered, and at least a thousand of injured.  Some of the victims were killed by knives in very barbaric ways; it is really something unbelievable.  Also, we were afraid that this kind of behavior would continue with other villages in the area.  It is a massacre, and a crime against humanity.  We convey this fact to the international community to do what they feel is appropriate.
#
#Question: (inaudible) Your Excellency is the president of SNC and now you are president of the Syrian Coalition, how will you manage the two posts?
#
#"""
#getStatementsFromText(text)

def get_info_from_match_group(m):
    location = m.group(1).title()
    if isLocation(location):

        text = m.string
        start = m.start()
        end = m.end()

        before = text[:start]
        after = text[end:]

        dates = extract_dates(get_last_sentence(before)) + extract_dates(get_last_sentence(after))
        if dates:
            date = dates[0]
        else:
            dates = extract_dates(get_last_paragraph(before)) + extract_dates(get_last_paragraph(after))
            if dates:
                date = dates[0]
            else:
                date = None

        context = get_paragraph(text, int((start+end)/2))
        if isJavaScript(context):
            context = ''

        result = {'date': date, 'hash': str(date) + "-" + str(location), 'location': location, 'context': context}

        return result
 

def getLocationsAndDatesFromEnglishText(text):
    global dictionary
    if not dictionary:
        print "if first time calling, initialize demonym dict"
        with open(os.path.dirname(os.path.abspath(__file__)) + "/data/demonyms.txt","r") as f:
            for line in f:
                words = line.strip().split(",")
                country = words[0]
                for word in words[1:]:
                    dictionary[word] = country


    #print "getting locations from ", type(text)
    if isinstance(text, str):
        text = text.decode("utf-8")
    #print "type(text) is", type(text)

    results = []

    # location after keyword
    for m in finditer(ur"(?:(?:[^A-Za-z]|^)(?:cross the|in|entered|into|outside of|from|eastern|western|northern|southern|reached|countries|leaving|to) )((?:[A-Z][a-z]+)(?: [A-Z][a-z]+)?)", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)
        
    # keyword after country as name or acronym
    for m in finditer(ur"([A-Z][a-z]+|[A-Z]{2,}) (?:city|county|province)", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)
 

    # keyword after country as name or acronym
    for m in finditer(ur"([A-Z][a-z]+|[A-Z]{2,})'s (?:border|prime minister|southern|western|northern|eastern|defense minister)", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)


    # Greece-Macedonia border
    for m in finditer(ur"([A-Z][a-z]+)-([A-Z][a-z]+) border", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)


    #countries, especially/like/ Italy, Greece and Hungary.
    for m in finditer(ur"(?:countries|nations|places), [a-z]+ ([A-Z][a-z]+), ([A-Z][a-z]+) and ([A-Z][a-z]+)", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)



    #islands of Kos, Chios, Lesvos and Samos 
    for m in finditer(ur"(?:countries|islands|nations|places|states) of ([A-Z][a-z]+), ([A-Z][a-z]+), ([A-Z][a-z]+)+ and ([A-Z][a-z]+)", text, MULTILINE):
        result = get_info_from_match_group(m)
        if result:
            results.append(result)



    #ignore demonyms for now, because accuracy is not that high
    #Eritreans, Syrian
    for m in finditer(ur"([A-Z][a-z]{3,}ans?)", text, MULTILINE):
        demonym = m.group(0)
        if demonym in dictionary:
            country = dictionary[demonym]
            result = get_info_from_match_group(m)
            result['location'] = country
            results.append(result)


    # this essentially changes the location name from the short version to any verbose version used in the text
    # e.g. Capsian changes to Caspian Sea
    locations = [result['location'] for result in results]

    #see: http://stackoverflow.com/questions/21720199/python-remove-any-element-from-a-list-of-strings-that-is-a-substring-of-anothe
    locations_verbose = filter(lambda x: [x for i in locations if x in i and x != i] == [], locations)
    for result in results:
        location = result['location']
        for location_verbose in locations_verbose:
            if not location == location_verbose and location in location_verbose:
                print "changing " + location + " to " + location_verbose
                result['location'] = location_verbose

    grouped_by_hash = {}
    for result in results:
        h = result['hash']
        if h in grouped_by_hash:
            #if have same hash, then have same exact location and date, so just need to update context
            grouped_by_hash[h]['context'] += "\n ... \n" + result['context']

        else:
            grouped_by_hash[h] = {'context': result['context'], 'date': result['date'], 'location': result['location']}

    results = grouped_by_hash.values()

    return results
x = getLocationsAndDatesFromEnglishText
