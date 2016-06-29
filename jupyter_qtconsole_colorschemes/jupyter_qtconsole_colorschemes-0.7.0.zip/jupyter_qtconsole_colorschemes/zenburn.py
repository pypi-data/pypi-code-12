"""
A Pygments_ style based on the dark background variant of Zenburn_. Originally
from https://github.com/litzomatic/MyVim

.. _Pygments: http://pygments.org/
.. _Zenburn: http://kippura.org/zenburnpage/
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

class ZenburnStyle(Style):
    """
    This style mimics the Zenburn color scheme.
    """

    background_color = "#3f3f3f"
    highlight_color = "#838383"

    styles = {
        # No corresponding class for the following:
        Text:                      "#dcdccc",
        # Whitespace:                "#000000",
        Error:                     "#80d4aa bg:#2f2f2f",
        # Other:                     "#000000",

        Keyword:                   "bold #f0dfaf",
        Keyword.Constant:          "#dca3a3",
        # Keyword.Declaration:       "#000000",
        Keyword.Namespace:         "bold #dfaf8f",
        # Keyword.Pseudo:            "#000000",
        Keyword.Reserved:          "bold #dfaf8f",
        Keyword.Type:              "bold #dfaf8f",

        Name:                      "#dcdccc",
        # Name.Attribute:            "#000000",
        Name.Builtin:              "#efef8f",
        Name.Builtin.Pseudo:       "#efef8f",
        Name.Class:                "#efef8f",
        # Name.Constant:             "#000000",
        Name.Decorator:            "#efefef",
        # Name.Entity:               "#000000",
        Name.Exception:            "bold #c3bf9f",
        Name.Function:             "#efef8f",
        # Name.Label:                "#000000",
        Name.Namespace:            "#8fbede",
        # Name.Other:                "#000000",
        # Name.Tag:                  "#000000",
        Name.Variable:             "bold #ffcfaf",
        Name.Variable.Class:       "#efef8f",
        # Name.Variable.Global:      "#000000",
        # Name.Variable.Instance:    "#000000",

        # Literal:                   "#000000",
        # Literal.Date:              "#000000",

        String:                    "#cc9393",
        # String.Backtick:           "#000000",
        String.Char:               "bold #dca3a3",
        # String.Doc:                "italic #7f9f7f",
        # String.Double:             "#000000",
        # String.Escape:             "#000000",
        # String.Heredoc:            "#000000",
        # String.Interpol:           "#000000",
        # String.Other:              "#000000",
        # String.Regex:              "#000000",
        # String.Single:             "#000000",
        # String.Symbol:             "#000000",

        Number:                    "#8cd0d3",
        #Number.Float:              "#000000",
        #Number.Hex:                "#000000",
        #Number.Integer:            "#000000",
        #Number.Integer.Long:       "#000000",
        #Number.Oct:                "#000000",

        Operator:                  "#f0efd0",
        Operator.Word:             "#f0efd0",

        Punctuation:               "#8f8f8f",

        Comment:                   "italic #7f9f7f",
        Comment.Hashbang:          "italic #7f9f7f",
        # Comment.Multiline:         "#000000",
        Comment.Preproc:           "bold #ffcfaf",
        # Comment.Single:            "#000000",
        # Comment.Special:           "#000000",

        # Generic:                   "#000000",
        Generic.Deleted:           "#333333",
        # Generic.Emph:              "#000000",
        # Generic.Error:             "#000000",
        Generic.Heading:           "bold #efefef",
        Generic.Inserted:          "bold #709080",
        # Generic.Output:            "#000000",
        # Generic.Prompt:            "#000000",
        # Generic.Strong:            "#000000",
        Generic.Subheading:        "#e3ceab",
        # Generic.Traceback:         "#000000",
    }
