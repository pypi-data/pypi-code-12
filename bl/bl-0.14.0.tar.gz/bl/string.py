
"""
The String() class provided in this library allows a more object-oriented usage pattern and adds 
several convenience methods that are not available in the standard library. String() inherits from 
str and overrides all of its methods that return strings, so that the return value is itself a 
String(), which enables chaining. For example:

>>> s = String('In the beginning God created')
>>> s.titleify()                    # knows English capitalization rules, can be taught other languages.
'In the Beginning God Created'
>>> _.hyphenify()                   # adds hyphens
'In-the-Beginning-God-Created'
>>> s                               # the original string is not changed -- immutability by default
'In the beginning God created'
"""

import re

# articles, conjunctions, prepositions, the s in 's
LOWERCASE_WORDS = {
    'en': """a an the and or nor for but than because vs to in on off from at of by under over 
            through with against about across aboard above according after along alongside amid 
            among apart around beneath beyond below beside behind before between concerning despite 
            during into near onto throughout toward until unto upon versus via within without s amp 
            n v adj adv prep ed ing eth th""".split()
}

class String(str):
    """our own str string class that adds several useful methods"""
    
    def digest(self, alg='sha256', b64=True, strip=True):
        """return a url-safe hash of the string, optionally (and by default) base64-encoded
            alg='sha256'    = the hash algorithm, must be in hashlib
            b64=True        = whether to base64-encode the output
            strip=True      = whether to strip trailing '=' from the base64 output
        """
        import base64, hashlib
        h = hashlib.new(alg)
        h.update(str(self).encode('utf-8'))
        if b64==True:
            # this returns a string with a predictable amount of = padding at the end
            b = base64.urlsafe_b64encode(h.digest()).decode('ascii')
            if strip==True:
                b = b.rstrip('=')
            return b
        else:
            return h.hexdigest()

    def camelify(self):
        """turn a string to CamelCase, omitting non-word characters"""
        outstring = self.titleify(allwords=True)
        outstring = re.sub("&[^;]+;", " ", outstring)
        outstring = re.sub("\W+", "", outstring)
        return String(outstring)

    def titleify(self, lc_words=LOWERCASE_WORDS['en'], allwords=False, lastword=True):
        """takes a string and makes a title from it"""
        outstring = str(self)
        l = re.split("([_\W]+)", outstring.strip())
        for i in range(len(l)):
            l[i] = l[i].lower()
            if allwords==True or i == 0 \
            or (lastword==True and i == len(l)-1) \
            or l[i].lower() not in lc_words:
                w = l[i]
                if len(w) > 1:
                    w = w[0].upper() + w[1:]
                else:
                    w = w.upper()
                l[i] = w
        outstring = "".join(l)
        return String(outstring)

    def identifier(self, camelsplit=False):
        """return a python identifier from the string"""
        outstring = self.nameify(camelsplit=camelsplit).replace('-', '_')
        if len(outstring)==0 or re.match("[^A-Za-z]", outstring[0]):
            outstring = "_" + outstring
        return String(outstring)

    def tagify(self):
        """lowercase, hyphen-separated string, useful for XML tags."""
        return self.nameify().lower()

    def nameify(self, camelsplit=False):
        if camelsplit==True: 
            s = self.camelsplit()
        else:
            s = self
        return s.hyphenify()

    def hyphenify(self):
        """Turn non-word characters (incl. underscore) into single hyphens"""
        outstring = str(self)
        outstring = re.sub("&[^;]*?;", ' ', outstring)                          # entities
        outstring = re.sub("""['"\u2018\u2019\u201c\u201d]""", '', outstring)   # quotes
        outstring = re.sub("\W+", '-', outstring).strip(' -')                   # collapse multiple
        return String(outstring)

    def camelsplit(self):
        """Turn a CamelCase string into a string with spaces"""
        outstring = str(self)
        for i in range(len(outstring)-1, -1, -1):
            if i != 0 \
            and ((outstring[i].isupper() 
                    and outstring[i-1].isalnum() 
                    and not outstring[i-1].isupper()) 
                or (outstring[i].isnumeric() 
                    and outstring[i-1].isalpha())):
                outstring = outstring[:i] + ' ' + outstring[i:]
        return String(outstring.strip())

    def words(self):
        l = [String(w) for w in re.split(r"\s+", str(self))]
        return l

    def __add__(self, other):
        return String(str(self) + str(other))

    # add regexp methods as re*
    def refindall(self, pattern, flags=0):
        return [String(s) for s in re.findall(pattern, self, flags=flags)]
    def research(self, pattern, flags=0):
        return re.search(pattern, self, flags=flags)
    def rematch(self, pattern, flags=0):
        return re.match(pattern, self, flags=flags)
    def resplit(self, pattern, maxsplit=0, flags=0):
        return [String(s) for s in re.split(pattern, self, maxsplit=maxsplit, flags=flags)]
    def resub(self, pattern, repl, count=0, flags=0):
        return String(re.sub(pattern, repl, self, count=count, flags=flags))
    def resubn(self, pattern, repl, count=0, flags=0):
        s, n = re.subn(pattern, repl, self, count=count, flags=flags)
        return (String(s), n)

    # override common string methods to return String() rather than str
    def capitalize(self): return String(str.capitalize(self))
    def casefold(self): return String(str.casefold(self))
    def center(self, *args): return String(str.center(self, *args))
    def encode(self, **kwargs): return str.encode(self, **kwargs)
    def expandtabs(self, *tabsize): return String(str.expandtabs(self, *tabsize))
    def find(self, sub, *args): return String(str.find(self, sub, *args))
    def format(self, *args, **kwargs): return String(str.format(self, *args, **kwargs))
    def format_map(self, mapping): return String(str.format_map(self, mapping))
    def index(self, sub, *args): return String(str.index(self, sub, *args))
    def join(self, iterable): return String(str.join(self, iterable))
    def ljust(self, width, *fillchar): return String(str.ljust(self, width, *fillchar))
    def lower(self): return String(str.lower(self))
    def lstrip(self, *chars): return String(str.lstrip(self, *chars))
    def replace(self, old, new, *count): return String(str.replace(self, old, new, *count))
    def rfind(self, sub, *args): return String(str.rfind(self, sub, *args))
    def rindex(self, sub, *args): return String(str.rindex(self, sub, *args))
    def rjust(self, width, *fillchar): return String(str.rjust(self, width, *fillchar))
    def rsplit(self, **kwargs): return String(str.rsplit(self, **kwargs))
    def rstrip(self, *chars): return String(str.rstrip(self, *chars))
    def split(self, **kwargs): return [String(s) for s in str.split(self, **kwargs)]
    def splitlines(self, *keepends): return [String(l) for l in str.splitlines(self, *keepends)]
    def strip(self, *chars): return String(str.strip(self, *chars))
    def swapcase(self): return String(str.swapcase(self))
    def title(self): return String(str.title(self))
    def translate(self, mapping): return String(str.translate(self, mapping))
    def upper(self): return String(str.upper(self))
    def zfill(self, width): return String(str.zfill(self, width))


if __name__=='__main__':
    import doctest
    doctest.testmod()
