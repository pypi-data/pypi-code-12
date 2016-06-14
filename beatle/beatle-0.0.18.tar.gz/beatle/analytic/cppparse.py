# -*- coding: utf-8 -*-

"""
Some utilities for c++ parsing
"""

import re


def clean_code(text):
    """This method removes comments and closed statements."""
    delimiters = [('/*', '*/'), ('{', '}')]
    for delimiter in delimiters:
        test = True
        while test:
            test = False
            right_pos = text.find(delimiter[1])
            if right_pos > 0:
                left_pos = text.rfind(delimiter[0], 0, right_pos)
                if left_pos >= 0:
                    text = text[:left_pos] + '0' + text[right_pos + 1:]
                    test = True
    #quit newlines and line comments
    return ''.join((x + ' ')[0:x.find('//')] for x in text.splitlines())

# some definitions
TYPE_KEYWORD = r"bool|char|char16_t|char32_t|double|float|int|long|short|signed|unsigned|void|wchar_t"
OTHER_KEYWORD = r"alignas|alignof|and|and_eq|asm|auto|"\
          r"bitand|bitor|break|case|catch|class|"\
          r"compl|const|constexpr|const_cast|continue|decltype|default|"\
          r"delete|do|dynamic_cast|else|enum|explicit|export|extern|"\
          r"false|for|final|friend|goto|if|inline|mutable|namespace|"\
          r"new|noexcept|not|not_eq|nullptr|operator|or|or_eq|private|"\
          r"protected|public|register|reinterpret_cast|return|signed|"\
          r"sizeof|static|static_assert|static_cast|struct|switch|template|"\
          r"this|thread_local|throw|true|try|typedef|typeid|typename|"\
          r"union|unsigned|using|virtual|volatile|while|xor|xor_eq"

KEYWORD = r'{TYPE_KEYWORD}|{OTHER_KEYWORD}'.format(
    TYPE_KEYWORD=TYPE_KEYWORD, OTHER_KEYWORD=OTHER_KEYWORD)
FIRST_ID_CHAR = r'[_A-Za-z]'
OTHER_ID_CHAR = r'[_A-Za-z0-9]'
IDENTIFIER = r'(?<!{OTHER_ID_CHAR}){FIRST_ID_CHAR}+{OTHER_ID_CHAR}*'.format(FIRST_ID_CHAR=FIRST_ID_CHAR, OTHER_ID_CHAR=OTHER_ID_CHAR)
UNSIGNED = r'[0-9]+'
INTEGER = r'[\+-]?{UNSIGNED}'.format(UNSIGNED=UNSIGNED)
POSITIVE = r'\+?{UNSIGNED}'.format(UNSIGNED=UNSIGNED)
FLOAT = r'{INTEGER}\.{UNSIGNED}'.format(INTEGER=INTEGER, UNSIGNED=UNSIGNED)
NUMBER = r'{INTEGER}|{FLOAT}'.format(INTEGER=INTEGER, FLOAT=FLOAT)
STRING = r'"[^"]*"'
CHAR = r'\'[^\']*\''
ARRAY = r'\{[^\}]*\}'
CONSTANT = r'{CHAR}|{STRING}|{NUMBER}|{ARRAY}'.format(CHAR=CHAR,
    STRING=STRING, NUMBER=NUMBER, ARRAY=ARRAY)
NAMESPACE = '(?!{KEYWORD}){IDENTIFIER}'.format(KEYWORD=KEYWORD, IDENTIFIER=IDENTIFIER)
TYPENAME = '(?!{OTHER_KEYWORD}){IDENTIFIER}'.format(OTHER_KEYWORD=OTHER_KEYWORD, IDENTIFIER=IDENTIFIER)
VARNAME = '(?!{KEYWORD}){IDENTIFIER}'.format(KEYWORD=KEYWORD, IDENTIFIER=IDENTIFIER)
MEMBERNAME = '(?!{KEYWORD}){IDENTIFIER}'.format(KEYWORD=KEYWORD, IDENTIFIER=IDENTIFIER)
AMBIT = r'({NAMESPACE}::)*'.format(NAMESPACE=NAMESPACE)
TYPE = r'{AMBIT}{TYPENAME}'.format(AMBIT=AMBIT, TYPENAME=TYPENAME)
VARIABLE = r'{AMBIT}{VARNAME}'.format(AMBIT=AMBIT, VARNAME=VARNAME)
ACCESSOR = r'\.|-\>'
MEMBER = r'{VARIABLE}{ACCESSOR}{MEMBERNAME}'.format(
    VARIABLE=VARIABLE, ACCESSOR=ACCESSOR, MEMBERNAME=MEMBERNAME)
FUNCTION = VARIABLE
MEMBER_FUNCTION = r'{VARIABLE}{ACCESSOR}{MEMBERNAME}'.format(
    VARIABLE=VARIABLE, ACCESSOR=ACCESSOR, MEMBERNAME=MEMBERNAME)
ARGLIST = r'([^,]*(,[^,]*)*)?'
FUNCTION_CALL = r'({FUNCTION}|{MEMBER_FUNCTION})\s*\({ARGLIST}\s*\)'.format(
    FUNCTION=FUNCTION, MEMBER_FUNCTION=MEMBER_FUNCTION, ARGLIST=ARGLIST)
REFERENCE_SPECIFIER = r'&'
POINTER_SPECIFIER = r'\*'
SIZE_SPECIFIER = r'{POSITIVE}|{VARIABLE}|{MEMBER}|{FUNCTION_CALL}'.format(POSITIVE=POSITIVE,
    VARIABLE=VARIABLE, MEMBER=MEMBER, FUNCTION_CALL=FUNCTION_CALL)
ARRAY_SPECIFIER = r'\[\s*({SIZE_SPECIFIER})?\s*\]'.format(SIZE_SPECIFIER=SIZE_SPECIFIER)
VARNAME_PREFIX = r'({REFERENCE_SPECIFIER}|{POINTER_SPECIFIER})'.format(
    REFERENCE_SPECIFIER=REFERENCE_SPECIFIER, POINTER_SPECIFIER=POINTER_SPECIFIER)
VARNAME_SUFFIX = ARRAY_SPECIFIER
TYPE_MODIFIER = r'volatile|const|static|register|signed|unsigned|long|short'

MODIFIED_TYPE = r'(({TYPE_MODIFIER})\s+)*{TYPE}'.format(TYPE_MODIFIER=TYPE_MODIFIER, TYPE=TYPE)
G_MODIFIED_TYPE = r'(?P<modifiers>(({TYPE_MODIFIER})\s+)*)(?P<type>{TYPE})'.format(TYPE_MODIFIER=TYPE_MODIFIER, TYPE=TYPE)
reMODIFIED_TYPE = re.compile(G_MODIFIED_TYPE)

VALUE = r'{CONSTANT}|{VARIABLE}|{MEMBER}|{FUNCTION_CALL}'.format(
    CONSTANT=CONSTANT, VARIABLE=VARIABLE, MEMBER=MEMBER, FUNCTION_CALL=FUNCTION_CALL)

NEW_CAST = r'(dynamic_cast|const_cast|reinterpret_cast)\s*\<\s*{MODIFIED_TYPE}\s*(\*\s*)*\>\s*\(.*\)'.format(
    MODIFIED_TYPE=MODIFIED_TYPE)
OLD_CAST = r'\(\s*{MODIFIED_TYPE}\s*(\*\s*)*\)({VALUE})'.format(MODIFIED_TYPE=MODIFIED_TYPE, VALUE=VALUE)

CAST = r'({NEW_CAST})|({OLD_CAST})'.format(NEW_CAST=NEW_CAST, OLD_CAST=OLD_CAST)

RVALUE = r'{VALUE}|{CAST}|'.format(VALUE=VALUE, CAST=CAST)

VARINIT = '(({VARNAME_PREFIX}\s*)+|\s+)({VARNAME})\s*({VARNAME_SUFFIX})?(\s*=\s*({RVALUE}))?'.format(
    VARNAME_PREFIX=VARNAME_PREFIX, VARNAME=VARNAME, VARNAME_SUFFIX=VARNAME_SUFFIX, RVALUE=RVALUE)

G_VARINIT = '((?P<prefix>({VARNAME_PREFIX}\s*)+)|\s+)(?P<name>{VARNAME})\s*(?P<suffix>{VARNAME_SUFFIX})?(\s*=\s*({VALUE}))?'.format(
    VARNAME_PREFIX=VARNAME_PREFIX, VARNAME=VARNAME, VARNAME_SUFFIX=VARNAME_SUFFIX, VALUE=VALUE)
reVARINIT = re.compile(G_VARINIT)

VARDECL = r'(?P<modified_type>{MODIFIED_TYPE})\s*(?P<varlist>{VARINIT}(,{VARINIT})*)\s*;'.format(
    MODIFIED_TYPE=MODIFIED_TYPE, VARINIT=VARINIT)
reVARDECL = re.compile(VARDECL)


def gather_vars(code, types=None):
    """This method analizes the code and returns either false if something is wrong
    or a dictionnaire with the structure:
        varname:{type:(typename), ptr:(boolean),  const:(boolean), array:(boolean)}
    if types is specified, it must be a dicctionary typename:<type object>. This case,
    varname:type is translated to <type object> and ignored if not present
    """
    code = clean_code(code)
    if not code:
        return False
    _vars = {}
    for match in reVARDECL.finditer(code):
        modified_type = match.group('modified_type')
        varlist = match.group('varlist')
        match_modified_type = reMODIFIED_TYPE.match(modified_type)
        if not match_modified_type:
            print "Error: modified_type {modified_type} can't be analised\n".format(modified_type=modified_type)
            continue
        modifiers = match_modified_type.group('modifiers')
        _type = match_modified_type.group('type')
        if types:
            if _type not in types:
                continue
            _type = types[_type]
        if modifiers:
            _volatile = 'volatile' in modifiers
            _const = 'const' in modifiers
            _static = 'static' in modifiers
            _register = 'register' in modifiers
            if 'long' in modifiers:
                _type = 'long {}'.format(_type)
            if 'short' in modifiers:
                _type = 'short {}'.format(_type)
            if 'signed' in modifiers:
                _type = 'signed {}'.format(_type)
            if 'unsigned' in modifiers:
                _type = 'unsigned {}'.format(_type)
        else:
            _volatile = False
            _const = False
            _static = False
            _register = False
        count = 0
        for match_varinit in reVARINIT.finditer(varlist):
            count = count + 1
            _prefix = match_varinit.group('prefix')
            _name = match_varinit.group('name')
            _suffix = match_varinit.group('suffix')
            if len(_name) == 0:
                print "Error: name in {varinit} can't be extracted\n".format(varinit=match.expand(G_VARINIT))
                continue
            if _prefix:
                _ptr = '*' in _prefix
                _ref = '&' in _prefix
            else:
                _ptr = False
                _ref = False
            if _suffix:
                _array = '[' in _suffix
            else:
                _array = False
            _vars.update({_name: {
                'type': _type,
                'static': _static,
                'volatile': _volatile,
                'const': _const,
                'register': _register,
                'ptr': _ptr,
                'ref': _ref,
                'array': _array
                }})
        if count == 0:
            print "Error : failed to parse varlist {varlist}\n".format(varlist=varlist)
    return _vars

