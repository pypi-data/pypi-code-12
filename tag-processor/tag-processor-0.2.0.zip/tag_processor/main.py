from builtins import str
from builtins import object
import re
from tag_processor.models import FunctionTag, ObjectTag


class TagParser(object):

    def __init__(self, data_container):
        self.data_container = data_container

    def parse(self, input_string):
        result = list()

        if not input_string:
            return result

        tags = self._get_tags(input_string)
        for tag in tags:
            elements = self._get_elements(self._remove_tag_borders(tag))
            result.append({
                'text': tag,
                'chain': elements
            })

        return result

    def _get_elements(self, input_string):
        elements = input_string.split('__')
        elements = self._split_attributes(elements)
        return [self._box_element(element) for element in elements]

    @staticmethod
    def _get_tags(input_string):
        return re.findall("\$\{.+?[^\}]\}", input_string)

    @staticmethod
    def _remove_tag_borders(tag):
        return tag[2:-1]

    def _box_element(self, element):
        if element[0] == '[' and element[-1] == ']':
            return self.get_function_tag(element)
        return self.get_object_tag(element)

    def get_function_tag(self, element):
        function_elements = element[1:-1].split('=')
        function = getattr(self.data_container, function_elements[0], None)
        params = None
        if len(function_elements) > 1:
            params = function_elements[1]
        return FunctionTag(function, params)

    @staticmethod
    def get_object_tag(element):
        return ObjectTag(element)

    @staticmethod
    def _split_attributes(elements):
        result = []
        for raw_element in elements:
            attributes = re.findall("[^\[\];]+(?=[;\]])", raw_element)

            element_without_attribute = re.search("[^\[\]]+(?=[\[])", raw_element)
            element = raw_element
            if element_without_attribute:
                element = element_without_attribute.group(0)

            result.append(element)
            if attributes:
                for attribute in attributes:
                    result.append('[' + attribute + ']')

        return result


class TagProcessor(object):

    tag_parser = None

    def __init__(self, data_container):
        self.data_container = data_container
        self.tag_parser = TagParser(self.data_container)

    def execute(self, input_string):
        tags = self.tag_parser.parse(input_string)
        for tag in tags:
            tag_result = self.process_tag(tag)
            if len(tags) == 1 and tag.get('text') == input_string:
                return tag_result
            elif not tag_result:
                tag_result = u''

            input_string = input_string.replace(tag.get('text'), str(tag_result))
        return input_string

    def process_tag(self, tag):
        data = self.data_container
        for element in tag.get('chain', None):
            data = element.execute(data)
        return data
