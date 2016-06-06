
"""
This module is for XHTML rendering

Some sort of template engine
"""

import logging
import re
import sys
import urllib.parse
import xml.sax.saxutils

import wayround_org.utils.dict
import wayround_org.utils.error
import wayround_org.utils.text


def pi(content):
    return {
        'type': 'pi',
        'content': content
        }


def comment(text):
    return {
        'type': 'comment',
        'content': text
        }


def dtd(text):
    return {
        'type': 'dtd',
        'content': text
        }


def cdata(text):
    return {
        'type': 'cdata',
        'content': text
        }


def char(text):
    return {
        'type': 'char',
        'content': text
        }


def static(text):
    return {
        'type': 'static',
        'content': text
        }


def html_head(
        title='',
        description='',
        keywords=[]
        ):
    return tag(
        'head',
        content={
            '00010_title': tag(
                'title',
                content=title
                ),
            '00020_description': tag(
                'meta',
                closed=True,
                attributes={
                    'name': 'description',
                    'content': description
                    }
                ),
            '00030_keywords': tag(
                'meta',
                closed=True,
                attributes={
                    'name': 'keywords',
                    'content': ' '.join(list(keywords))
                    }
                ),
            }
        )


def xhtml11(
        head=None,
        content=None,
        body_module=None,
        body_uid=None,
        body_js=None,
        body_css=None
        ):

    return {
        '00010_xml_pi': pi('xml version="1.0" encoding="UTF-8"'),
        '00015_html_dtd': dtd(
            'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
            '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
            ),
        '00020_html': tag(
            'html',
            attributes={
                'version': '-//W3C//DTD XHTML 1.1//EN',
                'xmlns': 'http://www.w3.org/1999/xhtml',
                'xml:lang': 'en',
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xsi:schemaLocation':
                    'http://www.w3.org/1999/xhtml '
                    'http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd'
                },
            closed=False,
            module=None,
            uid=None,
            required_css=[],
            required_js=[],
            content={
                '00010_head': head,
                '00020_body': tag(
                    'body',
                    module=body_module,
                    uid=body_uid,
                    required_css=body_css,
                    required_js=body_js,
                    content=content
                    )
                }
            )
        }


def html5(
        head=None,
        content=None,
        body_module=None,
        body_uid=None,
        body_js=None,
        body_css=None
        ):

    return {
        '00010_xml_pi': pi('xml version="1.0" encoding="UTF-8"'),
        '00015_html_dtd': dtd(
            'DOCTYPE xhtml'
            ),
        '00020_html': tag(
            'html',
            attributes={
                'lang': 'en'
                },
            closed=False,
            module=None,
            uid=None,
            required_css=[],
            required_js=[],
            content={
                '00010_head': head,
                '00020_body': tag(
                    'body',
                    module=body_module,
                    uid=body_uid,
                    required_css=body_css,
                    required_js=body_js,
                    content=content
                    )
                }
            )
        }


def tag(
        name,
        attributes=None,
        closed=False,
        module=None,
        uid=None,
        required_css=None,
        required_js=None,
        content=None,
        new_line_before_start=None,
        new_line_before_content=None,
        new_line_after_content=None,
        new_line_after_end=None
        ):
    ret = {
        'type': 'tag',
        'tag_info': {
            'name': name,
            'closed': closed,
            'attributes': attributes
            },
        'module': module,
        'uid': uid,
        'required_css': required_css,
        'required_js': required_js,
        'content': content
        }
    for i in [
            'new_line_before_start',
            'new_line_before_content',
            'new_line_after_content',
            'new_line_after_end'
            ]:
        if eval(i) is not None:
            ret[i] = eval(i)

    return ret


def check_unit(indict, path=[]):

    if isinstance(indict, str):
        return

    for i in list(indict.keys()):
        if not i in [
                'type',
                'tag_info',
                'content',
                'module',
                'uid',
                'required_css',
                'required_js',
                'new_line_before_start',
                'new_line_before_content',
                'new_line_after_content',
                'new_line_after_end'
                ]:
            raise KeyError("Wrong key `{}' at `{}'".format(i, '/'.join(path)))

    logging.debug("check_unit path {}".format('/'.join(path)))

    if len(path) >= 255:
        raise DictatorshipUnitTooDeep(
            "Dictatorship tree recursion limit reached `{}'".format(
                '/'.join(path)
                )
            )

    # Supplied data definitely must be a dict or list, otherwise - error
    if not isinstance(indict, (dict, list, str)):
        raise ValueError("Supplied data is not a dict or a list")

    # 'type' must be supplied
    if not 'type' in indict:
        raise MissingDictatorshipUnitAttribute(
            "Dictatorship unit type missing"
            )

    # 'type' must be one of following
    if not indict['type'] in [
            'tag', 'dtd', 'comment', 'cdata', 'static',
            'pi', 'char'
            ]:
        raise ValueError("Wrong dictatorship unit type")

    # If 'type' is 'tag', then check 'tag_info' and everything,
    # what underlie
    if indict['type'] == 'tag':
        if not 'tag_info' in indict \
                or not isinstance(indict['tag_info'], dict):
            raise MissingDictatorshipUnitAttribute(
                "Dictatorship unit type is `tag', but not `tag_info' supplied"
                )

        else:
            for i in list(indict['tag_info'].keys()):
                if not i in [
                        'attributes',
                        'name',
                        'closed'
                        ]:
                    raise KeyError(
                        "Wrong key `{}' at `{}'['tag_info']".format(
                            i, '/'.join(path)
                            )
                        )

            # tag name MUST be supplied and must be a string!
            if not 'name' in indict['tag_info']:
                raise MissingDictatorshipUnitAttribute(
                    "`name' not supplied in dictatorship unit `tag_info'"
                    )
            else:
                if not isinstance(indict['tag_info']['name'], str):
                    raise TypeError("tag `name' must be a string")

            # attributes CAN be supplied or CAN be a None or a dict
            if 'attributes' in indict['tag_info']:
                if indict['tag_info']['attributes'] is None:
                    indict['tag_info']['attributes'] = {}
                else:
                    if not isinstance(indict['tag_info']['attributes'], dict):
                        raise TypeError("tag `attributes' must be dict")
                    else:
                        # attribute values can be a strings or callabels
                        for i in list(indict['tag_info']['attributes'].keys()):
                            if not isinstance(
                                    indict['tag_info']['attributes'][i], str
                                    ):
                                raise TypeError(
                                    "tag `attributes' dict "
                                    "values must be strings"
                                    )
            else:
                indict['tag_info']['attributes'] = {}

            # 'tag_info' 'closed' attribute CAN be supplied and CAN be
            #  None or bool.
            if 'closed' in indict['tag_info']:
                if not isinstance(indict['tag_info']['closed'], bool):
                    raise TypeError("tag `closed' attribute can be only bool")
            else:
                indict['tag_info']['closed'] = False

    for i in ['required_css', 'required_js']:
        if i in indict:
            if indict[i] is None:
                indict[i] = []
            elif not isinstance(indict[i], list):
                raise TypeError("`{}' can only be list or None".format(i))
            else:
                for j in indict[i]:
                    if not isinstance(j, str):
                        raise TypeError(
                            "All `{}' values must be strings".format(i)
                            )

        else:
            indict[i] = []

    for i in ['module', 'uid']:
        if i in indict:
            if indict[i] is not None:
                if isinstance(indict[i], str):
                    if not re.match(r'[a-zA-Z][a-zA-Z\-]*', indict[i]):
                        raise ValueError(
                            "Wrong `{i}' value at `{path}'".format_map(
                                {
                                    'path': '/'.join(path),
                                    'i': i
                                    }
                                )
                            )
                else:
                    raise ValueError("`{}' can be None or str".format(i))

    if not 'content' in indict:
        indict['content'] = ''
    elif indict['content'] is None:
        indict['content'] = ''
    elif isinstance(indict['content'], str):
        pass
    elif isinstance(indict['content'], dict):
        pass
    elif isinstance(indict['content'], list):
        pass
    else:
        raise ValueError(
            "wrong unit content value: `{}', but "
            "must be None, str, dict or list".format(
                type(indict['content'])
                )
            )

    default_new_line_before_start = False
    default_new_line_before_content = False
    default_new_line_after_content = False
    default_new_line_after_end = False

    if indict['type'] == 'tag':
        default_new_line_before_start = True
        if indict['tag_info']['closed']:
            default_new_line_after_content = False
        else:
            if isinstance(indict['content'], (dict, list)):
                default_new_line_after_content = True

    elif indict['type'] in ['tag', 'comment', 'dtd', 'pi']:
        default_new_line_after_end = True

    for i in [
            ('new_line_before_start', default_new_line_before_start),
            ('new_line_before_content', default_new_line_before_content),
            ('new_line_after_content', default_new_line_after_content),
            ('new_line_after_end', default_new_line_after_end)
            ]:
        if i[0] in indict:
            if not isinstance(indict[i[0]], bool):
                raise TypeError("Wrong `{}' value type".format(i[0]))
        else:
            indict[i[0]] = i[1]

    return


def render_attributes(indict, path=[], tagname='', xml_indent_size=2):
    ret = ''

    inaddr_l = len(path)

    indent = wayround_org.utils.text.fill(' ', inaddr_l * xml_indent_size)
    nameindent = wayround_org.utils.text.fill(' ', len(tagname))

    attrs = []

    keys = sorted(indict.keys())

    for i in keys:

        if ret != '':
            ret += ' '

        value = ''
        if isinstance(indict[i], str):
            value = indict[i]
        else:
            raise ValueError(
                "One of attribute values (`{}') is not str".format(i)
                )

        if isinstance(ret, str):

            try:
                attrs.append(
                    '{name}={value}'.format_map(
                        {
                            'name': i,
                            'value': xml.sax.saxutils.quoteattr(value)
                            }
                        )
                    )
            except:
                ret = 1
                break

    if isinstance(ret, str):
        ind_req = False
        for i in attrs:
            if len(i) > 80:
                ind_req = True
                break

        first = True

        curr_attr_i = 0
        attrs_l = len(attrs)

        for i in attrs:
            ind = ''
            if ind_req and not first:
                ind = "\n{indent} {nameindent} ".format_map(
                    {
                        'indent': indent,
                        'nameindent': nameindent
                        }
                    )

            ret += "{ind}{new_attr}".format_map(
                {
                    'ind': ind,
                    'new_attr': i
                    }
                )

            if curr_attr_i < attrs_l - 1:
                ret += ' '

            if first:
                first = False

            curr_attr_i += 1

    return ret


def dict_tree_to_xml_render(tree):
    b = DictTreeToXMLRenderer(2, True, True)

    b.set_tree(tree)

    ret = b.render()

    b.print_log()

    return ret


class DictatorshipUnitTooDeep(Exception):
    pass


class MissingDictatorshipUnitAttribute(Exception):
    pass


class ModulesDirError(Exception):
    pass


class DictTreeToXMLRenderer:

    """
    renderer for dict structures described in this modules

    use settings on init to adjust needed parameters, set_tree() method to
    set required tree and then user method render() to get the string
    """

    def __init__(
            self,
            xml_indent_size=2,
            generate_css=False,
            generate_js=False,
            log_size=100,
            space_before_closing_slash=False,
            css_and_js_holder=None
            ):

        # here linedup units are listed. key is path
        self.units = {}

        # here will be stored
        self.tree_dict = {}

        # those four attributes are for code formatting
        # purposes
        self.xml_indent_size = xml_indent_size
        self.xml_indent = wayround_org.utils.text.fill(' ', xml_indent_size)

        self.css_and_js_holder = css_and_js_holder

        self.css_placeables = []
        self.js_placeables = []

        self.log = []

        self.log_size = log_size

        self.generate_css = generate_css
        self.generate_js = generate_js
        self.space_before_closing_slash = space_before_closing_slash

        return

    def do_log(self, text):

        log_l = len(self.log)

        if log_l >= self.log_size:
            self.log = self.log[-self.log_size:]

        self.log.append(text)

    def print_log(self):
        for i in self.log:
            print(i)

    def set_tree(self, indict):
        self.tree_dict = indict

    def _lineup_tree(self, indict, already_added, path=[]):

        logging.debug("_lineup_tree path {}".format('/'.join(path)))

        ret = 0

        if not isinstance(indict, (dict, list)):
            raise TypeError("This method accepts only dict or list")

        if self.check_range(indict) != 0:
            self.do_log(
                "_lineup_tree wrong input data at path `{}'".format(
                    '/'.join(path)
                    )
                )

            ret = 1
        else:

            index = -1

            if isinstance(indict, dict):
                keys = sorted(indict.keys())
            else:
                keys = indict

            for i in keys:

                index += 1

                if isinstance(indict, dict):
                    unit = indict[i]
                elif isinstance(indict, list):
                    unit = i

                if isinstance(indict, dict):
                    path_name = i
                elif isinstance(indict, list):
                    path_name = str(index)

                if not id(unit) in already_added:

                    try:
                        tmp = '/'.join(path + [path_name])
                    except:
                        raise

                    if not tmp in self.units:
                        self.units[tmp] = unit

                    del(tmp)

                    already_added.add(id(unit))

                if 'content' in unit:
                    if isinstance(unit['content'], (dict, list)):

                        if self._lineup_tree(
                                unit['content'],
                                already_added,
                                path=path + [path_name]
                                ) != 0:
                            ret = 2

        return ret

    def lineup_tree(self):
        self.units = {}
        already_added = set()
        ret = self._lineup_tree(
            self.tree_dict, already_added, path=[]
            )

        return ret

    def check_tree(self):
        ret = 0

        keys = sorted(self.units.keys())

        for i in keys:
            try:
                check_unit(
                    self.units[i], i.split('/')
                    )
            except:
                self.do_log(
                    "-e- Error while checking `{path}'\n{exc_info}".format_map(
                        {
                            'path': i,
                            'exc_info':
                                wayround_org.utils.error.return_exception_info(
                                    sys.exc_info(),
                                    tb=True
                                    )
                            }
                        )
                    )
                ret = 1
                break

        return ret

    def find_required_css_and_js(self):

        self.css_placeables = []
        self.js_placeables = []

        keys = sorted(self.units.keys())

        for i in keys:

            if not self.generate_css and not self.generate_js:
                break

            if not 'module' in self.units[i] \
                    or not 'uid' in self.units[i]:
                continue

            if self.generate_css:
                if 'required_css' in self.units[i]:
                    for j in self.units[i]['required_css']:
                        placeable_name = \
                            "{module}/{uid}/{required}".format_map(
                                {
                                    'module': self.units[i]['module'],
                                    'uid': self.units[i]['uid'],
                                    'required': j,
                                    }
                                )
                        if not placeable_name in self.css_placeables:
                            self.css_placeables.append(placeable_name)

            if self.generate_js:
                if 'required_js' in self.units[i]:
                    for j in self.units[i]['required_js']:
                        placeable_name = \
                            "{module}/{uid}/{required}".format_map(
                                {
                                    'module': self.units[i]['module'],
                                    'uid': self.units[i]['uid'],
                                    'required': j,
                                    }
                                )
                        if not placeable_name in self.js_placeables:
                            self.js_placeables.append(placeable_name)

        return

    def _place_found_css_or_js(
            self,
            i,
            placement_i,
            typ,
            css_path_renderer=css_path_renderer,
            js_path_renderer=js_path_renderer
            ):

        if not typ in ['css', 'js']:
            raise ValueError("Wrong `typ' parameter value")

        if typ == 'css':
            new_val = tag(
                'link',
                closed=True,
                attributes={
                    'type': 'text/css',
                    'href': css_path_renderer(i),
                    'rel': 'stylesheet'
                    }
                )

        elif typ == 'js':
            new_val = tag(
                'script',
                attributes={
                    'type': 'text/javascript',
                    'src': js_path_renderer(i),
                    }
                )
        else:
            raise Exception("Wrong programming")

        check_unit(new_val)

        if isinstance(self.css_and_js_holder['content'], dict):
            wayround_org.utils.dict.append(
                self.css_and_js_holder['content'],
                new_val
                )

        elif isinstance(self.css_and_js_holder['content'], list):
            self.css_and_js_holder['content'].append(new_val)

    def place_found_css_and_js(
            self,
            css_path_renderer=css_path_renderer,
            js_path_renderer=js_path_renderer
            ):

        if not isinstance(self.css_and_js_holder, dict):
            raise ValueError("Wrong self.css_and_js_holder")

        if not isinstance(self.css_and_js_holder['content'], (dict, list)):
            raise TypeError(
                "self.css_and_js_holder['content'] can be only list or dict"
                )

        placement_i = 0

        if self.generate_css:
            for i in self.css_placeables:

                self._place_found_css_or_js(
                    i,
                    placement_i,
                    'css',
                    css_path_renderer=css_path_renderer,
                    js_path_renderer=js_path_renderer
                    )

                placement_i += 1

        if self.generate_js:
            for i in self.js_placeables:

                self._place_found_css_or_js(
                    i,
                    placement_i,
                    'js',
                    css_path_renderer=css_path_renderer,
                    js_path_renderer=js_path_renderer
                    )

                placement_i += 1

        return

    def _render_unit(self, root, unit, path, path_name, indent):

        if isinstance(unit, str):
            return xml.sax.saxutils.escape(unit)

        new_line_before_start = ''
        if unit['new_line_before_start']:
            new_line_before_start = '\n{}'.format(indent)

        new_line_before_content = ''
        if unit['new_line_before_content']:
            new_line_before_content = '\n'

        new_line_after_content = ''
        if unit['new_line_after_content']:
            new_line_after_content = '\n{}'.format(indent)

        new_line_after_end = ''
        if unit['new_line_after_end']:
            new_line_after_end = '\n'

        start = ''
        content = ''
        end = ''

        if unit['type'] == 'comment':
            start = '<!-- '

            content = str(unit['content'])

            content = content.replace('--', '-')

            end = ' -->'

        elif unit['type'] == 'pi':
            start = '<?'
            content = str(unit['content'])
            end = '?>'

        elif unit['type'] == 'dtd':
            start = '<!DOCTYPE '
            content = str(unit['content'])
            end = '>'

        elif unit['type'] == 'cdata':
            start = '<![CDATA['
            content = str(unit['content']).replace(']]>', '')
            end = ']]>'

        elif unit['type'] == 'char':
            start = ''
            content = xml.sax.saxutils.escape(str(unit['content']))
            end = ''

        elif unit['type'] == 'static':
            start = ''
            content = str(unit['content'])
            end = ''

        elif unit['type'] == 'tag':

            if (('module' in unit)
                    and ('uid' in unit)
                    and (isinstance(unit['module'], str))
                    and (isinstance(unit['uid'], str))
                ):
                class_list = list()

                if (
                        ('class' in unit['tag_info']['attributes'])
                        and
                        (isinstance(
                            unit['tag_info']['attributes']['class'], str))
                        ):
                    class_list += \
                        (unit['tag_info']['attributes']['class']).split(' ')

                class_list.append(unit['module'] + '---' + unit['uid'])

                class_list = sorted(set(class_list))

                unit['tag_info']['attributes']['class'] = ' '.join(class_list)

                class_list = []

            attributes = ''
            if unit['tag_info']['attributes'] is not None:
                attributes = render_attributes(
                    unit['tag_info']['attributes'],
                    path,
                    tagname=unit['tag_info']['name'],
                    xml_indent_size=self.xml_indent_size
                    )

            closing_slash = ''
            if unit['tag_info']['closed']:
                closing_slash = '/'

            space_before_attributes = ''
            if attributes != '':
                space_before_attributes = ' '

            space_before_closing_slash = ''
            if closing_slash != '':
                if self.space_before_closing_slash:
                    space_before_closing_slash = ' '
                else:
                    space_before_closing_slash = ''

            start = (
                '<{tagname}{space_before_attributes}{attributes}'
                '{space_before_closing_slash}{closing_slash}>'
                ).format_map(
                    {
                        'tagname': unit['tag_info']['name'],
                        'space_before_attributes': space_before_attributes,
                        'attributes': attributes,
                        'space_before_closing_slash':
                        space_before_closing_slash,
                        'closing_slash': closing_slash
                        }
                    )

            if not unit['tag_info']['closed']:

                if isinstance(unit['content'], str):
                    content = xml.sax.saxutils.escape(unit['content'])
                elif isinstance(unit['content'], (dict, list)):

                    content = self._render(
                        root, unit['content'], path=path + [path_name]
                        )
                elif unit['content'] is None:
                    content = ''

                else:
                    content = str(unit['content'])

                end = '</{}>'.format(unit['tag_info']['name'])
            else:
                content = ''
                end = ''

        else:
            raise ValueError("Wrong type at `{}'".format('/'.join(path)))

        ret = (""
               + "{new_line_before_start}"
               + "{start}"
               + "{new_line_before_content}"
               + "{content}"
               + "{new_line_after_content}"
               + "{end}"
               + "{new_line_after_end}").format_map(
            {
                'new_line_before_start': new_line_before_start,
                'new_line_before_content': new_line_before_content,
                'new_line_after_content': new_line_after_content,
                'new_line_after_end': new_line_after_end,
                'start': start,
                'content': content,
                'end': end
                }
            )

        return ret

    def _render(self, root, indict, path=[]):

        ret = ''

        inaddr_l = len(path)

        indent = wayround_org.utils.text.fill(
            ' ',
            inaddr_l * self.xml_indent_size
            )

        index = -1

        if isinstance(indict, dict):
            keys = sorted(indict.keys())
        elif isinstance(indict, list):
            keys = indict
        else:
            raise TypeError("This method accepts only dict or list")

        for i in keys:
            index += 1

            unit = None

            if isinstance(indict, dict):
                unit = indict[i]
            elif isinstance(indict, list):
                unit = i
            else:
                raise TypeError("This method accepts only dict or list")

            if isinstance(indict, dict):
                path_name = i
            elif isinstance(indict, list):
                path_name = str(index)

            ret += self._render_unit(root, unit, path, path_name, indent)

        return ret

    def render(
            self,
            css_path_renderer=css_path_renderer,
            js_path_renderer=js_path_renderer
            ):

        ret = ''

        if self.lineup_tree() != 0:
            self.do_log("-e- Some errors liningup dict tree")
            ret = 1

        if isinstance(ret, str):
            if self.check_tree() != 0:
                ret = 2

        if isinstance(ret, str):

            if self.css_and_js_holder:
                self.find_required_css_and_js()
                self.place_found_css_and_js(
                    css_path_renderer=css_path_renderer,
                    js_path_renderer=js_path_renderer
                    )

        if isinstance(ret, str):
            ret = self._render(self.tree_dict, self.tree_dict, path=[])

        return ret

    def check_range(self, indict):
        ret = 0

        if not isinstance(indict, (dict, list)):
            self.do_log(
                "-e- Supplied data is not a dict and not list: {}".format(
                    repr(indict)
                    )
                )
            ret = 1

        else:

            for i in indict:

                if isinstance(indict, dict):
                    unit = indict[i]
                elif isinstance(indict, list):
                    unit = i
                else:
                    raise TypeError("This method accepts only dict or list")

                if not isinstance(unit, (dict, str)):
                    self.do_log(
                        "-e- Dictatorship `{}' element value "
                        "is not a dict and not str".format(str(unit))
                        )

                    ret = 2
                    break

        return ret


def css_path_renderer(inname):
    module, uid, file = inname.split('/')[0:3]

    return "css?module={module}&uid={uid}&file={file}".format_map(
        {
            'module': urllib.parse.quote(
                module, encoding='utf-8', errors='strict'
                ),
            'uid': urllib.parse.quote(
                uid, encoding='utf-8', errors='strict'
                ),
            'file': urllib.parse.quote(
                file, encoding='utf-8', errors='strict'
                )
            }
        )


def js_path_renderer(inname):
    module, uid, file = inname.split('/')[0:3]

    return "js?module={module}&uid={uid}&file={file}".format_map(
        {
            'module': urllib.parse.quote(
                module, encoding='utf-8', errors='strict'
                ),
            'uid': urllib.parse.quote(
                uid, encoding='utf-8', errors='strict'
                ),
            'file': urllib.parse.quote(
                file, encoding='utf-8', errors='strict'
                )
            }
        )


def test():
    # Upper dict element with names (like following) is called
    # `dictatorship range'.
    # Dictatorship range's keys must point only on dict-s,
    # otherwise it is an error.

    logging.basicConfig(level='DEBUG')

    a = {
        '000_xml_pi': {
            'type': 'pi',
            'content': 'xml version="1.1" encoding="UTF-8"',
            },
        '010_xhtml_doctype': {
            'type': 'dtd',
            'content':
                'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
                '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
            },
        '100_html_tag': {
            # Dictatorship gange pointet dicts (like this)
            # is called `dictatorship unit'

            # Any dict can be one of folloving types:
            # 'tag', 'dtd', 'comment', 'cdata', 'static', 'char'
            # 'pi' (Processing instructions).
            # If type is 'tag',then 'tag_info' subdict is required
            'type': 'tag',

            # inserts new lines
            # 'new_line_before_start': False,
            # 'new_line_before_content': False,
            # 'new_line_after_content': False,
            # 'new_line_after_end': False,

            # 'tag_info' required to present if type is 'tag'.
            # 'tag_info' must be a dict.
            'tag_info': {
                # any valid tag name
                'name': 'html',

                # None or dict
                # dict values must be strings
                'attributes': {
                    'version': '-//W3C//DTD XHTML 1.1//EN',
                    'xmlns': 'http://www.w3.org/1999/xhtml',
                    'xml:lang': 'en',
                    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                    'xsi:schemaLocation':
                        'http://www.w3.org/1999/xhtml '
                        'http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd'
                    },

                # (bool) if True - no contents is
                # passible and any info supplied in 'contents'
                # will be omited. Default is False.
                'closed': False
                },

            # str, dict, None, callable
            # None - exchenged to empty string
            # string - used as is
            # dict - assumed tobe new
            # `dictatorship range'
            # callable - must return string
            'content': {
                '10_head': {
                    'type': 'tag',
                    'tag_info': {
                        'name': 'head'
                        },
                    'content': {
                        'title': {
                            'type': 'tag',
                            'tag_info': {
                                'name': 'title'
                                },
                            'content': 'Page Title'
                            }
                        }
                    },
                '20_body': {
                    'type': 'tag',
                    'tag_info': {
                        'name': 'body'
                        },
                    'module': 'core',
                    'uid': 'body',
                    'required_css': ['main.css', 'body.css'],
                    'required_js': ['main.js'],
                    }
                }

            }
        }

    print("Dictator test #1")
    b = DictTreeToXMLRenderer(2, True, True)
    b.set_tree(a)
    ret = b.render()
    print(repr(b.units))
    b.print_log()
    print(ret)
    return


def test2():
    logging.basicConfig(level='DEBUG')
    print("Dictator test #2")
    b = DictTreeToXMLRenderer(2, True, True)
    b.set_tree(html5())
    ret = b.render()
    print(repr(b.units))
    b.print_log()
    print(ret)
