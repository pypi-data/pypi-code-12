import collections

from .parser import Content, Tag

class NoSuchAttribute(Exception):
    pass



class Finder:
    def __init__(self, element_list):
        self.first_page_simple_element_list = ['SHA256', 'File name', 'Detection ratio', 'Analysis date']
        self.element_list = element_list
        self.content_list = []
        for element in self.element_list:
            if isinstance(element, Content):
                self.content_list.append(element)

    def find_attributes_from_list(self, attributes_to_find):
        attributes_found = collections.OrderedDict()
        for element_to_find in attributes_to_find:
            found_element = self._find_simple_attribute(element_to_find)
            attributes_found.update(found_element)
        return attributes_found

    def find_first_page_attributes(self):
        attributes_found = self.find_attributes_from_list(self.first_page_simple_element_list)
        attributes_found['Antyviruses'] = self._find_antyviruses_info()
        return attributes_found

    # w przypadku prostych atrybutów zawsze szukamy następnego elementu typu Content
    def _find_simple_attribute(self, element_to_find):
        j = -1
        for i, content in enumerate(self.content_list):
            if element_to_find in content.content:
                j = i + 1
                break
        if j == -1:
            return {element_to_find: "Element not found"}
        else:
            return {element_to_find: self.content_list[j].content}

    def _find_antyviruses_info(self):
        antyviruses_found = {}
        antyviruses_found = self._find_red_antyviruses_info(antyviruses_found)
        antyviruses_found = self._find_green_antyviruses_info(antyviruses_found)
        return antyviruses_found

    def _next_green_antyvirus(self):
        antyvirusTag = Tag(tagname='td', attributes={'class': 'ltr text-green'})
        for i, element in enumerate(self.element_list):
            if antyvirusTag == element:
                yield i
        return None

    def _find_green_antyviruses_info(self, antyviruses_found):
        for index in self._next_green_antyvirus():
            antyvirus = {self.element_list[index - 2].content:
                             self.element_list[index + 1].attributes['title']}

            antyviruses_found.update(antyvirus)
        return antyviruses_found

    def _next_red_antyvirus(self):
        antyvirusTag = Tag(tagname='td', attributes={'class': 'ltr text-red'})
        for i, element in enumerate(self.element_list):
            if antyvirusTag == element:
                yield i
        return None

    def _find_red_antyviruses_info(self, antyviruses_found):
        for index in self._next_red_antyvirus():
            antyvirus = {self.element_list[index - 2].content:
                             self.element_list[index + 1].content}
            antyviruses_found.update(antyvirus)
        return antyviruses_found
