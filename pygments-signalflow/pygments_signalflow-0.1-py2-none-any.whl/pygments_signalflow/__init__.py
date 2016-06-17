# Copyright (C) 2016 Maxime Petazzoni <maxime.petazzoni@bulix.org>

from pygments.lexer import RegexLexer, bygroups, combined, include, words
from pygments.token import *  # noqa


class SignalFlowLexer(RegexLexer):
    """Pygments lexer for SignalFx SignalFlow streaming analytics language.

    Some of the patterns here were taken from Pygments' Python lexer, since
    SignalFlow's syntax is inspired by Python.
    """

    name = 'SignalFlow'
    aliases = ['signalflow', 'flow']
    filenames = ['*.flow']

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            (r'[^\\\'"%\n]+', ttype),
            (r'[\'"\\]', ttype),
            (r'%', ttype),
        ]

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'#.*$', Comment.Single),
            (r'[(),.:]', Punctuation),
            (r'!=|[-*+%/<>=]', Operator),
            (r'(?<=[(,])\w+(?=[\s=])', Keyword),
            include('builtins'),
            include('name'),
            include('numbers'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
        ],

        'name': [
            (r'@[\w.]+', Name.Decorator),
            ('[a-zA-Z_]\w*', Name),
        ],

        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+', Number.Float),
            (r'\d+(M|w|d|h|m|s|ms)', Number),
            (r'\d+', Number.Integer),
        ],

        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],

        'builtins': [
            (words(('abs', 'accumulator', 'bottom', 'ciel', 'const', 'count',
                    'data', 'delta', 'detect', 'dimensionalize', 'events',
                    'extrapolate', 'fetch', 'filter', 'find', 'floor',
                    'graphite', 'groupby', 'id', 'integrate', 'log', 'log10',
                    'map', 'math', 'max', 'mean', 'mean_plus_stddev', 'median',
                    'min', 'newrelic', 'percentile', 'pow', 'print', 'publish',
                    'random', 'rateofchange', 'sample', 'sample_stddev',
                    'sample_variance', 'select', 'size', 'split', 'sqrt',
                    'stats', 'stddev', 'sum', 'threshold', 'timeshift', 'top',
                    'variance', 'when', 'window'),
                   suffix=r'(?=\()'),
                Name.Builtin),
            (words(('_collector', '_random', '_seq', '_turnstile'),
                   suffix=r'\b'),
                Name.Function.Magic),
            (words(('lambda'), suffix=r'(?=\s)'), Keyword.Reserved),
            ],
    }
