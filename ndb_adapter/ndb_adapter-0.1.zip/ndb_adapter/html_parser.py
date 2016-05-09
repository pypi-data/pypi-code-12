from html.parser import HTMLParser
from typing import List, Dict


class NDBHtmlParser(HTMLParser):
    """Class for html parse"""
    def __init__(self):
        """Default constructor"""
        HTMLParser.__init__(self)
        self.__tree = None
        self.__elementsStack = []

    def error(self, message: str):
        """Function for error messages

        :param message: message string
        :type message: str
        """
        pass

    def analyze(self, data: str) -> None:
        """Function for analyze html structure

        :param data: html string
        :type data: str
        :return: None
        """
        self.__tree = None
        self.__elementsStack = []
        self.feed(data)
        self.close()

        if self.__elementsStack:
            self.__tree = self.__elementsStack.pop()

    def get_tree(self) -> 'Tag':
        """Function for get tree top element

        :rtype: 'Tag'
        :return: Tree top
        """
        return self.__tree

    def find_one(self, name: str =None, after: 'Tag'=None, before: 'Tag'=None, params: dict=None) -> 'Tag':
        """Function for get tree node matching criteria

        :param name: node name (default value = None)
        :type name: str
        :param after: after node instance (default value = None)
        :type after: Tag
        :param before: before node instance (default value = None)
        :type before: Tag
        :param params: node parameters (default value = None)
        :type params: dict
        :return: searched node
        :rtype: 'Tag'
        """
        if after and not isinstance(after, Tag):
            raise TypeError("After is not instance of Tag class")
        if before and not isinstance(before, Tag):
            raise TypeError("Before is not instance of Tag class")
        if params and not isinstance(params, dict):
            raise TypeError("Params is not instance of dictionary class")

        root = self.__tree if after is None else after
        next_tag = Tag(name="root", next_sib=root)
        while True:
            try:
                next_tag = next(next_tag)

                if before and before == next_tag:
                    raise StopIteration
                elif name and next_tag.name != name:
                    continue
                elif next_tag.has_attr(params):
                    return next_tag

            except StopIteration:
                return None

    def find_all(self, name: str=None, after: 'Tag'=None, before: 'Tag'=None, params: dict=None) -> List['Tag']:
        """Function for get tree node matching criteria

            :param name: node name (default value = None)
            :type name: str
            :param after: after node instance (default value = None)
            :type after: Tag
            :param before: before node instance (default value = None)
            :type before: Tag
            :param params: node parameters (default value = None)
            :type params: dict
            :return: searched nodes list
            :rtype: List[Tag]
        """
        if after and not isinstance(after, Tag):
            raise TypeError("After is not instance of Tag class")
        if before and not isinstance(before, Tag):
            raise TypeError("Before is not instance of Tag class")
        if params and not isinstance(params, dict):
            raise TypeError("Params is not instance of dictionary class")

        root = self.__tree if after is None else after
        next_tag = Tag(name="root", next_sib=root)
        result = []
        while True:
            try:
                next_tag = next(next_tag)

                if before == next_tag:
                    raise StopIteration
                elif name and next_tag.name != name:
                    continue
                elif next_tag.has_attr(params):
                    result.append(next_tag)

            except StopIteration:
                return result

    def handle_starttag(self, tag, attrs) -> None:
        """Function to handle start tag and add to stack of nodes

        :param tag: tag string
        :param attrs: attributes dictionary
        :return: None
        """
        to_add = Tag(tag, attrs=dict(attrs))
        self.__elementsStack.append(to_add)

    def handle_endtag(self, tag) -> None:
        """Function to handle end tag and add to tree

        :param tag: tag ending
        :return: None
        """
        try:
            poped = self.__elementsStack.pop()
            if not self.__elementsStack:
                if not self.__tree:
                    self.__tree = poped
                else:
                    self.__tree.add_child(poped)
            else:
                self.__elementsStack[-1].add_child(poped)
        except IndexError:
            pass

    def handle_data(self, data) -> None:
        """Function to handle data in tags

        :param data: data inside tag
        :return: None
        """
        #   TO DO: rest unicode char to null
        data = data.translate({ord('\xc5'): '', ord('\xa0'): '', ord('\n'): '',
                               ord('\t'): '', ord('\r'): '', ord('\f'): ''})
        data = data.strip()
        try:
            self.__elementsStack[-1].data += data
        except IndexError:
            pass


class Tag(object):
    """Class for handle html tags"""
    def __init__(self, name: str, data: str='', attrs: dict=None, parent: 'Tag'=None, next_sib: 'Tag'=None,
                 prev_sib: 'Tag'=None, children: List['Tag']=None):
        """Default constructor

        :param name: tag name
        :type name: str
        :param data: tag data (default value = '')
        :type data: str
        :param attrs: tag attributes (default value = None)
        :type attrs: dict
        :param parent: parent tag
        :type parent: Tag
        :param next_sib: next sibling tag
        :type next_sib: Tag
        :param prev_sib: previous sibling tag
        :type prev_sib: Tag
        :param children: list of children's
        :type children: List[Tag]
        """
        self.name = name    # type: str
        self.data = data    # type: str
        self.attrs = [] if attrs is None else attrs     # type: Dict[str]
        self.parent = parent    # type: Tag
        self.next_sib = next_sib    # type: Tag
        self.prev_sib = prev_sib    # type: Tag
        self.children = [] if children is None else children    # type: List[Tag]
        for child in self.children:
            child.parent = self

    def has_attr(self, params: dict) -> bool:
        """To check if tag has given attributes

        :param params: attributes to check
        :type params: dict
        :return: True/False if there is attribute
        """
        if not params:
            return True

        for attr_key in self.attrs:
            for par_key in params:
                if par_key == attr_key and params[par_key] == self.attrs[attr_key]:
                    return True
        return False

    def add_child(self, child: 'Tag') -> None:
        """To add child to tag

        :param child: tag to add
        :type child: Tag
        :return: None
        """
        child.parent = self
        if self.children:
            self.children[-1].next_sib, child.prev_sib = child, self.children[-1]
        self.children.append(child)

    def prev(self) -> 'Tag':
        """Previous tag

        :return: previous tag
        :rtype: Tag
        """
        if self.prev_sib:
            return self.prev_sib
        elif self.parent:
            return self.parent
        else:
            raise StopIteration

    def __next__(self) -> 'Tag':
        """Next tag

        :return: next tag
        :rtype: Tag
        """
        if self.children:
            return self.children[0]
        elif self.next_sib:
            return self.next_sib

        parent = self.parent
        while parent:
            if parent.next_sib:
                return parent.next_sib
            parent = parent.parent
        else:
            raise StopIteration

    next = __next__

    def next_data(self) -> str:
        """Next tag data

        :return: next tag data
        :rtype: str
        """
        next_tag = self.next()
        if next_tag:
            return next_tag.data
        return ''

    def prev_data(self) -> str:
        """Previous tag data

        :return: previous tag data
        :rtype: str
        """
        next_tag = self.prev()
        if next_tag:
            return next_tag.data
        return ''

    def __repr__(self) -> str:
        """Tag to string"""
        return self.__str__()

    def __iter__(self):
        """For iteration handle"""
        return self

    def __str__(self) -> str:
        """Tag to string

        :return: tag as string
        :rtype: str
        """
        result = "<" + str(self.name)

        for key in self.attrs:
            result += " " + str(key) + "=\"" + str(self.attrs[key]) + "\""
        result += ">" + str(self.data)

        for child in self.children:
            result += str(child)

        result += "</" + str(self.name) + ">"

        return result
