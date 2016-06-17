# Copyright (C) 2016 Maxime Petazzoni <maxime.petazzoni@bulix.org>

from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *  # noqa


class SignalFlowLexer(RegexLexer):
    """Pygments lexer for SignalFx SignalFlow streaming analytics language.

    Some of the patterns here were taken from Pygments' Python lexer, since
    SignalFlow's syntax is inspired by Python.
    """

    name = 'SignalFlow'
    aliases = ['signalflow', 'flow']
    filenames = ['*.flow']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'#.*$', Comment.Single),
            (r'[(),.:]', Punctuation),
            (r'!=|[-*+%/<>=]', Operator),
            (r'(abs|accumulator|bottom|ciel|const|count|data|delta|detect'
             '|dimensionalize|events|extrapolate|fetch|filter|find|floor'
             '|graphite|groupby|id|integrate|log|log10|map|math|max|mean'
             '|mean_plus_stddev|median|min|newrelic|percentile|pow|print'
             '|publish|random|rateofchange|sample|sample_stddev'
             '|sample_variance|select|size|split|sqrt|stats|stddev|sum'
             '|threshold|timeshift|top|variance|when|window)(\()',
             bygroups(Name.Builtin, Punctuation), 'function'),
            (r'(_collector|_random|_seq|_turnstile)(\()',
             bygroups(Name.Function.Magic, Punctuation), 'function'),
            (r'lambda(?=\s)', Keyword.Reserved),
            include('name'),
            include('numbers'),
            ('"', String.Double, 'dqs'),
            ("'", String.Single, 'sqs'),
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

        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            (r'[^"]', String.Double),
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            (r"[^']", String.Single),
        ],

        'function': [
            (r'\)', Punctuation, '#pop'),
            (r'\w+(?=[\s=])', Keyword),
            include('root'),
        ],
    }
