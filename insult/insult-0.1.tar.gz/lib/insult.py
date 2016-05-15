## \package insult
## \copyright Copyright (C) 2016 Mattia Basaglia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import random
import os
import re
import json

class WordList(object):
    """!
    A list of insulting words of some kind
    """

    def __init__(self, id, words=[]):
        """!
        \param id       A WordListId (expanded with word_list_id())
        \param words    An iterable containing words to add to the list
        """
        id = word_list_id(id)

        ## Name of the word list
        self.name = id.name
        ## Set of words in the list
        self.words = set(words)
        ## Flags fot the set of words \todo
        ## \note Two word lists can have the same name iff they have different flags
        self.flags = id.flags

    def add_word(self, word):
        """!
        Appends a word to the list
        """
        self.words.add(word)

    def get(self, max_count=1, min_count=None):
        """!
        Retrieves a random subset of words
        \param max_count Maximum number of words to return
        \param min_count Minimum number of words to return,
                         if omitted, returns exactly \p max_count words
        """
        if max_count > len(self.words):
            max_count = len(self.words)
        if min_count is None:
            min_count = max_count
        return random.sample(self.words, random.randint(min_count, max_count))

    def check_flags(self, flags):
        """!
        Checks if the flags match
        \todo
        """
        return True


class WordListId(object):
    """!
    Identifier for a word list
    """

    def __init__(self, name, flags=0):
        self.name = name
        self.flags = flags

    def check(self, word_list):
        """!
        Checks if the word list matches this Id
        \param word_list a WordList object
        """
        return word_list.name == self.name and word_list.check_flags(self.flags)


def word_list_id(*args):
    """!
    Workaround for the lack of overloading
    """
    if len(args) == 1:
        if isinstance(args[0], basestring):
            return WordListId(args[0])
        if isinstance(args[0], WordListId):
            return args[0]
        if type(args[0]) is tuple and len(args[0]) == 2:
            return WordListId(*args[0])
    elif len(args) == 2:
        return WordListId(*args)
    raise TypeError("Invalid arguments to the WordListId constructor")


class Insulter(object):
    """!
    Object that can generate insults
    \note all methods that take a WordListId argument, will expand it
          using word_list_id()
    """

    ## Regex used to recognize valid word file names
    regex_word_file = re.compile(r'^[a-z_]+$')
    ## File name for language rules
    rules_file = "rules.json"

    def __init__(self):
        """!
        """
        ## Word lists to look up
        self.word_lists = []
        ## Maximum number of repetitions allowed
        self.max_count = None
        ## Maximum number of repetitions allowed for a specific word list
        self.list_max_count = {}
        ## Language rules
        self.rules = {}

    def word_list(self, wl_id, add=False):
        """!
        Returns a matching word list
        \param wl_id    WordListId to match the list
        \param add      if \c True, missing lists will be added to the insulter
        \throws Exception if the list cannot be retrieved
        """
        wl_id = word_list_id(wl_id)
        for word_list in self.word_lists:
            if wl_id.check(word_list):
                return word_list

        if add:
            self.word_lists.append(WordList(wl_id, []))
            return self.word_lists[-1]

        raise Exception("Word list not found: %s" % wl_id.name)

    def load_directory(self, path):
        """!
        Loads all word lists in \p path
        \param path The path to the directory to load
        \note Only files matching regex_word_file will be considered
        """
        for basename in os.listdir(path):
            full = os.path.join(path, basename)
            if basename == Insulter.rules_file:
                try:
                    with open(full) as file:
                        rules = json.load(file)
                    for name, rule in rules.iteritems():
                        self.set_rules(name, rule)
                except ValueError:
                    pass
            elif os.path.isfile(full) and self.regex_word_file.match(basename):
                with open(full) as file:
                    lines = filter(bool, (line.strip() for line in file))
                self.add_words(basename, lines)

    def add_words(self, wl_id, words):
        """!
        Adds words to a word list
        \param wl_id    WordListId to match the list
        \param words    Iterable with words to be added
        """
        self.word_list(wl_id, True).words |= set(words)

    def get(self, wl_id, max_count=1, min_count=None):
        """!
        Retrieves a random subset of words form a word list
        \param wl_id     WordListId to match the list
        \param max_count Maximum number of words to return,
                         note that it will be checked against the value set
                         with set_max()
        \param min_count Minimum number of words to return,
                         if omitted, returns exactly \p max_count words
        \see set_max(), WordList.get()
        """
        wl_id = word_list_id(wl_id)
        if self.max_count is not None and max_count > self.max_count:
            max_count = self.max_count
        if max_count > self.list_max_count.get(wl_id.name, max_count):
            max_count = self.list_max_count[wl_id.name]
        return self.word_list(wl_id).get(max_count, min_count)

    def format(self, string):
        """!
        Formats an insult string
        """
        doc = NotQuiteXml(string, lambda e: e.attrs.get("_expansion", ""))

        new_unexpanded = [
            elem
            for elem in doc.contents
            if isinstance(elem, NotQuiteXmlElement)
        ]
        unexpanded = []

        while len(new_unexpanded) != len(unexpanded) and new_unexpanded:
            unexpanded = new_unexpanded
            new_unexpanded = []
            for elem in unexpanded:
                if not self._expand_element(elem, doc):
                    new_unexpanded.append(elem)
        return str(doc)

    def _expand_element(self, element, doc):
        try:
            if element.tag_name in self.rules:
                return self._expand_rule(element, doc)
            min = None
            max = 1
            if "count" in element.attrs:
                max = int(element.count)
            elif "max" in element.attrs:
                max = int(element.max)
                min = int(element.attrs.get("min", element.max))
            element._expansion = " ".join(self.get(element.tag_name, max, min))
            return True
        except Exception:
            return False

    def _expand_rule(self, element, doc):
        for rule in self.rules[element.tag_name]:
            pattern = rule["target"]
            target = doc.element_by_id(element.target)
            if re.match(pattern, target._expansion):
                element._expansion = re.sub(pattern, rule["result"], target._expansion)
                return True
        return False

    def set_max(self, max_count, word_list=None):
        """!
        Set the maximum number of repetitions for get()
        \param max_count    Maximum to be set,
                            if \c None will disable the maximum limit
        \param word_list    Word list name (note: not a WordListId)
        """
        if word_list is None:
            self.max_count = max_count
        elif max_count is None:
            if str(word_list) in self.list_max_count:
                del self.list_max_count[str(word_list)]
        else:
            self.list_max_count[str(word_list)] = max_count

    def set_rules(self, name, rules):
        """!
        Sets some language rules for the given identifier
        """
        self.rules[name] = rules


class NotQuiteXml(object):
    """!
    Parses strings with flat xml elements intermixed with text
    Only a very minimal subset of xml/sgml is supported
    """
    _entities = {
        "lt": "<",
        "gt": ">",
        "amp": "&",
    }

    def __init__(self, contents=None, to_string=lambda x: ""):
        """!
        \param contents     \c None or a sting to be parsed
        \param to_string    A functor to convert NotQuiteXmlElement
                            objects to a string
        """
        ## List mixing strings and NotQuiteXmlElement elements
        self.contents = []
        ## Elements with an ID
        self.elements_with_id = {}
        ## Functor to convert NotQuiteXmlElement objects to a string
        self.to_string = to_string

        if isinstance(contents, basestring):
            self.parse_string(contents)

    def element_by_id(self, id):
        """!
        Returns the element matching the given id
        """
        return self.elements_with_id[id]

    def elements_by_tag_name(self, name):
        """!
        Returns a list of elements with the given tag name
        """
        return [
            element
            for element in self.contents
            if isinstance(element, NotQuiteXmlElement) and
            element.tag_name == name
        ]

    def elements_by_attribute(self, name, value):
        """!
        Returns a list of elements having the given attribute with the given value
        """
        return [
            element
            for element in self.contents
            if isinstance(element, NotQuiteXmlElement) and
            name in element.attrs and element.attrs[name] == value
        ]


    def __str__(self):
        """!
        Converts the document to a string (using self.to_string for elements)
        """
        return "".join(str(elem) for elem in self.contents)

    def __repr__(self):
        return "".join(
            elem if type(elem) is str else repr(elem)
            for elem in self.contents
        )

    def parse_string(self, string):
        """!
        Parses a string into self.contents
        """
        self.contents = list(self._lex_text(iter(string)))

    def _lex_text(self, iterator):
        """!
        Internal lexer, starting state (text)
        yields elements for self.contents
        \param iterator A character iterator
        """
        string = ""
        try:
            while True:
                ch = iterator.next()
                if ch == "<":
                    if string:
                        yield string
                    string = ""
                    yield self._lex_elem_name(iterator)
                elif ch == "&":
                    string += self._lex_entity(iterator)
                else:
                    string += ch
        except StopIteration:
            if string:
                yield string

    def _lex_entity(self, iterator):
        """!
        Internal lexer, entity state
        in: (text) -> &
        out: ; -> (text)
        \returns A string corresponding to the entity
        \param iterator A character iterator
        """
        name = ""
        while True:
            ch = iterator.next()
            if ch == ";":
                break
            else:
                name += ch
        return self._entities.get(name, "")

    def _lex_elem_name(self, iterator):
        """!
        Internal lexer, element name state
        in: (text) -> <
        out: /> | > | _ -> (attrs) -> (text)
        \returns A string corresponding to the entity
        \param iterator A character iterator
        """
        name = ""
        while True:
            ch = iterator.next()
            if ch.isspace() or ch in "/>":
                element = NotQuiteXmlElement(self, name)
                self._lex_elem_attrs(ch, iterator, element)
                return element
            name += ch

    def _lex_elem_attrs(self, och, iterator, element):
        """!
        Internal lexer, element attributes state
        in: (text) -> (element name) -> _ | > | />
        out: /> | > | -> (text)
        \param och      Character used to enter this state
        \param iterator A character iterator
        \param element  Element to set the attributes to
        """
        ch = och
        while True:
            if ch == ">":
                return element
            elif ch == "/":
                iterator.next()
                return element
            elif ch.isspace() or ch == "":
                ch = iterator.next()
            else:
                ch = self._lex_elem_attr_name(ch, iterator, element)

    def _lex_elem_attr_name(self, och, iterator, element):
        """!
        Internal lexer, element attribute name
        in: (attrs) -> [not space or tag end]
        out: = -> (attr_value) -> (attrs)
        out: /> | > | _ -> (attrs)
        \param och      Character used to enter this state
        \param iterator A character iterator
        \param element  Element to set the attributes to
        \returns A lookahead character
        """
        name = och
        while True:
            ch = iterator.next()
            if ch.isspace() or ch in "/>":
                if name != "id":
                    element[name] = name
                return ch
            elif ch == "=":
                return self._lex_elem_attr_value(name, iterator, element)
            name += ch

    def _lex_elem_attr_value(self, name, iterator, element):
        """!
        Internal lexer, element attribute value
        in: (attr_name) -> =
        out: (attr_name) -> =" -> (here) -> " -> (attrs)
        out: (attr_name) -> =' -> (here) -> ' -> (attrs)
        out: (attr_name) -> = -> (here) -> _ -> (attrs)
        \param name     Name of the attribute
        \param iterator A character iterator
        \param element  Element to set the attributes to
        \returns A lookahead character
        """
        ch = iterator.next()
        value = ""
        skip = True
        if ch == '"' or ch == "'":
            delim = ch
            break_cond = lambda char: char == delim
        elif ch.isspace() or ch in "/>":
            break_cond = lambda char: True
            skip = False
        else:
            break_cond = lambda char: char.isspace() or char in "/>"
            value = ch
            skip = False

        ch = iterator.next()
        while not break_cond(ch):
            value += ch
            ch = iterator.next()

        self._elem_set_attr(element, name, value)
        if skip:
            ch = iterator.next()
        return ch

    def _elem_set_attr(self, element, name, value):
        """!
        Internal, sets an element attribute during parsing
        \todo handle this where you can set attributes in NotQuiteXmlElement
        """
        if name == "id":
            if value not in self.elements_with_id:
                element.id = value if value else None
        else:
            element[name] = value


class NotQuiteXmlElement(object):
    """!
    Non-text element in a NotQuiteXml document.
    Attributes can be accessed with the subscript operator or as members
    (if they don't clash with other members)
    """
    def __init__(self, document, tag_name, id=None, attrs={}):
        """!
        \param document     A NotQuiteXml object which contains this element
        \param tag_name     Name of the element tag in the source string
        \param id           Element id, must be unique in \p document or None
        \param attrs        Extra attribues
        """
        self._document = document
        self._tag_name = tag_name
        self.attrs = attrs.copy()
        self._id = None # this must be last (see __setattr__)
        self.id = id

    @property
    def document(self):
        return self._document

    @property
    def tag_name(self):
        return self._tag_name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value == self._id:
            return

        if value is None:
            del self.id
            return

        if value in self.document.elements_with_id:
            raise KeyError("ID already in use: %s" % value)

        if self._id is not None:
            del self.document.elements_with_id[self._id]
        self._id = value
        self.document.elements_with_id[value] = self

    @id.deleter
    def id(self):
        if self._id is not None:
            del self.document.elements_with_id[self._id]
            self._id = None

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __delitem__(self, key):
        del self.attrs[key]

    def __getattr__(self, name):
        try:
            super(NotQuiteXmlElement, self).__getattr__(name)
        except AttributeError:
            if name in self.attrs:
                return self.attrs[name]
            else:
                raise

    def __setattr__(self, name, value):
        if name in dir(self) or "_id" not in dir(self):
            super(NotQuiteXmlElement, self).__setattr__(name, value)
        else:
            self.attrs[name] = value

    def __delattr__(self, name):
        try:
            super(NotQuiteXmlElement, self).__delattr__(name)
        except AttributeError:
            if name in self.attrs:
                del self.attrs[name]
            else:
                raise

    def __str__(self):
        """!
        Converts the element to a string using the document to_string attribute
        """
        return self.document.to_string(self)

    def __repr__(self):
        return "<%s%s%s/>" % (
            self.tag_name,
            " id=\"%s\"" % self._id if self._id is not None else "",
            "".join(" %s=\"%s\"" % attr for attr in self.attrs.iteritems() )
        )
