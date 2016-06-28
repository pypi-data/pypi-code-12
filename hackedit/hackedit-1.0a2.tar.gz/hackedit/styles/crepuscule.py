"""
This module contains the darcula pygments theme.
"""
from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, \
    Operator, Text, Punctuation


class CrepusculeStyle(Style):
    """
    A dark theme for hackedit inspired by the Tomorrow Night theme from
    fish shell, adapted to look when using the Breeze Dark Theme (KDE) or the
    dark stylesheet (all platforms).
    """
    background_color = '#232629'
    highlight_color = '#1D2124'

    styles = {
        Comment.Multiline: '#6c7380',
        Comment.Preproc: '#81A2BE',
        Comment.Single: '#6c7380',
        Comment.Special: 'bold #81A2BE',
        Comment: '#6c7380',
        Error: '#e06c75',
        Generic.Deleted: '#CC4040',
        Generic.Emph: ' #c0d0e2',
        Generic.Error: '#aa0000',
        Generic.Heading: '#999999',
        Generic.Inserted: '#40CC40',
        Generic.Output: '#888888',
        Generic.Prompt: '#555555',
        Generic.Strong: 'bold',
        Generic.Subheading: '#aaaaaa',
        Generic.Traceback: '#aa0000',
        Keyword.Constant: '#DE935F',
        Keyword.Declaration: '#DE935F',
        Keyword.Namespace: '#DE935F',
        Keyword.Pseudo: '#DE935F',
        Keyword.Reserved: '#DE935F',
        Keyword.Type: '#af81bd bold',
        Keyword: '#DE935F bold',
        Literal.Number: '#6897B3',
        Literal.String: '#BDBD68',
        Literal.String.Doc: '#61AFEF',
        Name.Attribute: '#DE935F',
        Name.Builtin.Pseudo: '#fcb5c6',
        Name.Builtin: '#c678dd',
        Name.Class: '#e06c75 bold underline',
        Name.Constant: '#87feb9',
        Name.Decorator: '#f5f069',
        Name.Entity: '#e06c75',
        Name.Exception: '#e06c75 bold',
        Name.Function: '#e06c75 bold',
        Name.Label: '#c0d0e2 bold',
        Name.Namespace: '#c0d0e2',
        Name.Tag: '#af81bd bold',
        Name.Variable.Class: '#c0d0e2 bold',
        Name.Variable.Global: '#c0d0e2 bold',
        Name.Variable.Instance: '#c0d0e2',
        Name.Variable: '#c0d0e2',
        Operator: '#c0d0e2 bold',
        Operator.Word: '#DE935F bold',
        Text: '#c0d0e2',
        Text.Whitespace: '#656565',
        Punctuation: '#c0d0e2'
    }
