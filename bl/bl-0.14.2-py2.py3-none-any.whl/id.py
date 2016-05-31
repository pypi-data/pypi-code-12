
"""Create a variety of different random ids.

id.random_id() returns a random_id with the given parameters.

id.hex_chars is 16 characters long, so you need a much longer string for the 
same level of security, but some contexts need hex.
    + 16^8 = 4.3 billion unique ids.

id.alphanum_chars is 62 characters long, so it is plenty for uniqueness and 
non-discoverability for most circumstances. For example:
    + 62^6 = 5.68e10, which is the length of a bit.ly id (56.8 billion unique URLs).
    + 62^16 = 4.77e28, which is huge 
    + 62^32 = 2.27e57, which is overkill by a lot -- we'll never get a repeat, and we can test for it.

id.id_chars is id.alphanum_chars with confusing ones removed, so the set is a 
respectable 54 characters long.

id.punct_chars has most ascii punctuation.

id.ascii_chars = id.alphanum_chars + id.punct_chars.

urlslug_chars adds to id.alphanum_chars certain punctuation that is allowed 
in urls. 73 characters. This is useful for URL shorteners.
    + 73^4 = 28.4 million unique URL slugs. 
    + So a private URL shortener can be like the following:
        - www.tld.to/YpH0
    which exactly fits the size for micro-QR codes (15 characters).
    (This is exactly the size of links from www.goo.gl )
"""

import random

lcase_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 
                'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 
                'w', 'x', 'y', 'z']

hex_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                'a', 'b', 'c', 'd', 'e', 'f',]

alphanum_chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                    'n','o','p','q','r','s','t','u','v','w','x','y','z', 
                    'A','B','C','D','E','F','G','H','I','J','K','L','M',
                    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                    '0','1','2','3','4','5','6','7','8','9']

id_chars = [i for i in alphanum_chars 
            if i not in ['i','o','l','I','O','L','0','1']]
    
punct_chars = ['~','!','@','#','$','%','^','&','*','(',')','_','-','+',
                '=','[','{',']','}','|',';',':',',','<','.','>','/','?']

ascii_chars = alphanum_chars + punct_chars

urlslug_punct = ['$', '-', '_', '.', '+', '!', '*', "'", '(', ')', ',']
urlslug_chars = alphanum_chars + urlslug_punct

def random_id(length=8, charset=id_chars, first_charset=lcase_chars, group_char='', group_length=0):
    """Creates a random id with the given length and charset.
        length=8                    the number of characters in the id
        charset=id_chars            what character set to use (a list)
        first_charset=lcase_chars   what character set for the first character
        group_char=''               what character to insert between groups
        group_length=0              how long the groups are (default 0 means no groups)
    """
    t = []
    firstchars = list(set(charset).intersection(first_charset))
    if len(firstchars)==0: 
        firstchars = charset
    t.append(firstchars[int(random.random()*len(firstchars))])
    for i in range(2,length+1):
        t.append(charset[int(random.random()*len(charset))])
        if (group_length > 0) and (i % group_length == 0) and (i < length): 
            t.append(group_char)
    return ''.join(t)

