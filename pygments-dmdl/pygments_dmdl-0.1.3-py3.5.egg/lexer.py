# -*- coding: utf-8 -*-

"""
 Copyright 2016 cocoatomo

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from pygments.lexer import RegexLexer, include, default, bygroups
from pygments.token import Text, Whitespace, Keyword, Name, Literal, String, Number, Operator, Punctuation, Comment

class DmdlLexer(RegexLexer):
    name = 'Dmdl'
    aliases = ['dmdl']
    filenames = ['*.dmdl']

    tokens = {
        'root': [
            # <skip>:
            include('skip'),
            # <literal>:
            #      <string>
            #      <integer>
            #      <decimal>
            #      <boolean>
            (r'"', String.Double, 'string-literal'),
            include('integer-literal'),
            include('decimal-literal'),
            include('boolean-literal'),
            # keyword
            include('keyword'),
            # aggregator
            include('aggregator'),
            # <name>:
            include('name'),
            # symbol
            include('symbol'),
            # (basic-)type
            include('type'),
        ],

        # words to be skipped
        # used only from include
        'skip': [
            (r'[ \t\r\n]', Whitespace),
            (r'/\*', Comment.Multiline, 'block-comment'),
            (r'//.*?$', Comment.Singleline),
            (r'--.*?$', Comment.Singleline),
        ],
        'block-comment': [
            (r'[^*/]', Comment.Multiline),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        # <literal>:
        #      <string>
        #      <integer>
        #      <decimal>
        #      <boolean>
        'literal': [
            include('skip'),
            (r'"', String.Double, ('#pop', 'string-literal')),
            include('integer-literal'),
            include('decimal-literal'),
            include('boolean-literal'),
        ],
        # <string-literal>:
        #      '"' <string-char>* '"'
        # <string-char>:
        #      ~['"', '\']
        #      '\' ['b', 't', 'n', 'f', 'r', '\', '"']
        #      '\' 'u' ['0'-'9', 'A'-'F', 'a'-'f']{4}
        #      '\' '0' ['0'-'3']? ['0'-'7']? ['0'-'7']
        'string-literal': [
            # (r'.+', Text, '#pop'),
            (r'[^"\\]', String.Double),
            (r'\\[btnfr\\"]', String.Double),
            (r'\\u[0-9A-Fa-f]{4}', String.Double),
            (r'\\0[0-3]?[0-7]?[0-7]', String.Double),
            (r'"', String.Double, '#pop'),
        ],
        # <integer-literal>:
        #      '0'
        #      ['1'-'9']['0'-'9']*
        'integer-literal': [
            (r'0', Number.Integer),
            (r'[1-9][0-9]*', Number.Integer),
        ],
        # <decimal-literal>:
        #      '.' ['0'-'9']+
        #      '0.' ['0'-'9']*
        #      ['1'-'9']['0'-'9']* '.' ['0'-'9']*
        'decimal-literal': [
            (r'\.[0-9]+', Number.Float),
            (r'0\.[0-9]*', Number.Float),
            (r'[1-9][0-9]*\.[0-9]*', Number.Float),
        ],
        # <boolean-literal>:
        #      'TRUE'
        #      'FALSE'
        'boolean-literal': [
            (r'TRUE', Literal),
            (r'FALSE', Literal),
        ],
        # <keyword>:
        #      'projective'
        #      'joined'
        #      'summarized'
        'keyword': [
            # ensuring these are not a substring of a name
            (r'projective[^a-z0-9_]', Keyword.Type),
            (r'joined[^a-z0-9_]', Keyword.Type),
            (r'summarized[^a-z0-9_]', Keyword.Type),
        ],
        # <aggregator>:
        #      'any'
        #      'sum'
        #      'max'
        #      'min'
        #      'count'
        'aggregator': [
            # ensuring these are not a substring of a name
            (r'any[^a-z0-9_]', Name.Function),
            (r'sum[^a-z0-9_]', Name.Function),
            (r'max[^a-z0-9_]', Name.Function),
            (r'min[^a-z0-9_]', Name.Function),
            (r'count[^a-z0-9_]', Name.Function),
        ],
        # <name>:
        #      <first-word>
        #      <name> '_' <word>
        # <first-word>:
        #      ['a'-'z'] ['a'-'z', '0'-'9']*
        # <word>:
        #      ['a'-'z', '0'-'9']+
        'name': [
            (r'[a-z]([a-z0-9])*(_[a-z0-9]+)*', Name),
        ],
        # <symbol>:
        #      '@'
        #      '='
        #      ','
        #      '.'
        #      '+'
        #      '*'
        #      '&'
        #      '%'
        #      ':'
        #      ';'
        #      '->'
        #      '=>'
        #      '{'
        #      '}'
        #      '['
        #      ']'
        #      '('
        #      ')'
        'symbol': [
            (r'@', Name.Attribute, 'attribute-name'),
            (r'=[^>]', Operator),
            (r',', Punctuation),
            (r'\.', Name),
            (r'\+', Operator),
            (r'\*', Operator),
            (r'&', Operator),
            (r'%', Operator),
            (r':', Punctuation),
            (r';', Punctuation),
            (r'->', Operator),
            (r'=>', Operator),
            (r'\{', Punctuation),
            (r'\}', Punctuation),
            (r'\[', Punctuation),
            (r'\]', Punctuation),
            (r'\(', Punctuation),
            (r'\)', Punctuation),
        ],
        # <qname>:
        #      <qname> '.' <name>
        #      <name>
        'attribute-name': [
            include('skip'),
            (r'\.', Name.Attribute),
            (r'[a-z]([a-z0-9])*(_[a-z0-9]+)*', Name.Attribute),
            default('#pop'),
        ],
        # <type>:
        #      <basic-type>
        #      <reference-type>
        #      <sequence-type>
        # 
        # <sequence-type>:
        #     <type> '*'
        # <reference-type>:
        #      <name>
        # <basic-type>:
        #      'INT'
        #      'LONG'
        #      'BYTE'
        #      'SHORT'
        #      'DECIMAL'
        #      'FLOAT'
        #      'DOUBLE'
        #      'TEXT'
        #      'BOOLEAN'
        #      'DATE'
        #      'DATETIME'
        'type': [
            (r'INT', Keyword.Type),
            (r'LONG', Keyword.Type),
            (r'BYTE', Keyword.Type),
            (r'SHORT', Keyword.Type),
            (r'DECIMAL', Keyword.Type),
            (r'FLOAT', Keyword.Type),
            (r'DOUBLE', Keyword.Type),
            (r'TEXT', Keyword.Type),
            (r'BOOLEAN', Keyword.Type),
            # avoid a hasty decision
            (r'DATETIME', Keyword.Type),
            (r'DATE', Keyword.Type),
        ],
    }
