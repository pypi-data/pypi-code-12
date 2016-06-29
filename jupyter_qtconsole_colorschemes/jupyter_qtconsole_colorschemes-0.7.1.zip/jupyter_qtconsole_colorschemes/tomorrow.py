"""
A Pygments_ style based on the dark background variant of Tomorrow_.

.. _Pygments: http://pygments.org/
.. _Tomorrow: https://github.com/ChrisKempson/Tomorrow-Theme
"""
from pygments.style import Style
from pygments.token import Token, Comment, Name, Keyword, Generic, Number, Operator, String

BACKGROUND = '#fafafa'
CURRENTLINE = '#efefef'
SELECTION = '#d6d6d6'
FOREGROUND = '#4d4d4c'
COMMENT = '#8e908c'
RED = '#c82829'
ORANGE = '#f5871f'
YELLOW = '#eab700'
GREEN = '#718c00'
CYAN = '#3e999f'
BLUE = '#4271ae'
PURPLE = '#8959a8'

class TomorrowStyle(Style):

    background_color = BACKGROUND
    highlight_color = SELECTION

    styles = {
        Keyword: PURPLE,
        Keyword.Constant: ORANGE,
        Keyword.Declaration: BLUE,
        #Keyword.Namespace
        #Keyword.Pseudo
        Keyword.Reserved: BLUE,
        Keyword.Type: RED,

        #Name
        Name.Attribute: FOREGROUND,
        Name.Builtin: YELLOW,
        Name.Builtin.Pseudo: BLUE,
        Name.Class: BLUE,
        Name.Constant: ORANGE,
        Name.Decorator: BLUE,
        Name.Entity: ORANGE,
        Name.Exception: ORANGE,
        Name.Function: BLUE,
        #Name.Label
        #Name.Namespace
        #Name.Other
        Name.Tag: BLUE,
        Name.Variable: BLUE,
        #Name.Variable.Class
        #Name.Variable.Global
        #Name.Variable.Instance

        #Literal
        #Literal.Date
        String: GREEN,
        String.Backtick: FOREGROUND,
        String.Char: GREEN,
        String.Doc: FOREGROUND,
        #String.Double
        String.Escape: ORANGE,
        String.Heredoc: FOREGROUND,
        #String.Interpol
        #String.Other
        String.Regex: RED,
        #String.Single
        #String.Symbol
        Number: ORANGE,
        #Number.Float
        #Number.Hex
        #Number.Integer
        #Number.Integer.Long
        #Number.Oct

        Operator: CYAN,
        #Operator.Word

        #Punctuation: ORANGE,

        Comment: COMMENT,
        #Comment.Multiline
        Comment.Preproc: GREEN,
        #Comment.Single
        Comment.Special: GREEN,

        #Generic
        Generic.Deleted: CYAN,
        Generic.Emph: 'italic',
        Generic.Error: RED,
        Generic.Heading: ORANGE,
        Generic.Inserted: GREEN,
        #Generic.Output
        #Generic.Prompt
        Generic.Strong: 'bold',
        Generic.Subheading: ORANGE,
        #Generic.Traceback

        Token: FOREGROUND,
        Token.Other: ORANGE,
    }
