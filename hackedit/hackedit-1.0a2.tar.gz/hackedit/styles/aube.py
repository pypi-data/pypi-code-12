"""
This module contains the darcula pygments theme.
"""
from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, \
    Operator, Text, Punctuation


class AubeStyle(Style):
    """
    A light color scheme inspired by the Tomorrow theme from fish shell.
    """
    background_color = '#ffffff'
    highlight_color = '#c7e7f9'

    styles = {
        Comment.Multiline: '#969896',
        Comment.Preproc: '#4271AE',
        Comment.Single: '#969896',
        Comment.Special: 'bold #4271AE',
        Comment: '#969896',
        Error: '#CC0000',
        Generic.Deleted: 'bg:#ffdddd #000000',
        Generic.Emph: ' #000000',
        Generic.Error: '#aa0000',
        Generic.Heading: '#999999',
        Generic.Inserted: 'bg:#ddffdd #000000',
        Generic.Output: '#888888',
        Generic.Prompt: '#555555',
        Generic.Strong: 'bold',
        Generic.Subheading: '#aaaaaa',
        Generic.Traceback: '#aa0000',
        Keyword.Constant: '#e1923f',
        Keyword.Declaration: '#e1923f',
        Keyword.Namespace: '#e1923f',
        Keyword.Pseudo: '#e1923f',
        Keyword.Reserved: '#e1923f',
        Keyword.Type: '#8959A8 bold',
        Keyword: '#e1923f bold',
        Literal.Number: '#6897B3',
        Literal.String: '#007EA1',
        Literal.String.Doc: '#1272b9',
        Name.Attribute: '#e1923f',
        Name.Builtin.Pseudo: '#705050 italic',
        Name.Builtin: '#8959A8',
        Name.Class: '#CC6666 bold underline',
        Name.Constant: '#1d6c43',
        Name.Decorator: '#a6a709',
        Name.Entity: '#8959A8',
        Name.Exception: '#CC6666 bold',
        Name.Function: '#CC6666 bold',
        Name.Label: '#000000 bold',
        Name.Namespace: '#000000',
        Name.Tag: '#8959A8 bold',
        Name.Variable.Class: '#000000 bold',
        Name.Variable.Global: '#000000 bold',
        Name.Variable.Instance: '#000000',
        Name.Variable: '#000000',
        Operator: '#000000 bold',
        Operator.Word: '#e1923f bold',
        Text: '#000000',
        Text.Whitespace: '#BFBFBF',
        Punctuation: '#000000'
    }
