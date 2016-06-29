"""
A Pygments_ style based on the dark background variant of Spacemacs_. 

.. _Pygments: http://pygments.org/
.. _Spacemacs: https://github.com/nashamri/spacemacs-theme
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

class SpacemacsDarkStyle(Style):
    background_color = "#292b2e"
    highlight_color = "#444155"

    styles = {
        # No corresponding class for the following:
        Text:                      "#b2b2b2",
        # Whitespace:                "#000000",
        Error:                     "#f2241f",
        # Other:                     "#000000",

        Keyword:                   "bold #4f97d7",
        Keyword.Constant:          "nobold #bc6ec5",
        # Keyword.Declaration:       "#000000",
        Keyword.Namespace:         "#4f97d7",
        # Keyword.Pseudo:            "#000000",
        Keyword.Reserved:          "#4f97d7",
        Keyword.Type:              "#4f97d7",

        Name:                      "#b2b2b2",
        # Name.Attribute:            "#000000",
        Name.Builtin:              "#4f97d7",
        Name.Builtin.Pseudo:       "#4f97d7",
        Name.Class:                "bold #ce537a",
        # Name.Constant:             "#000000",
        Name.Decorator:            "bold #ce537a",
        # Name.Entity:               "#000000",
        Name.Exception:            "bold #ce537a",
        Name.Function:             "bold #bc6ec5",
        Name.Label:                "#7590db",
        Name.Namespace:            "#b2b2b2",
        # Name.Other:                "#000000",
        # Name.Tag:                  "#000000",
        Name.Variable:             "#7590db",
        Name.Variable.Class:       "#ce537a",
        # Name.Variable.Global:      "#000000",
        # Name.Variable.Instance:    "#000000",

        # Literal:                   "#000000",
        # Literal.Date:              "#000000",

        String:                    "#2d9574",
        # String.Backtick:           "#000000",
        # String.Char:               "#2d9574",
        # String.Doc:                "#000000",
        # String.Double:             "#000000",
        # String.Escape:             "#000000",
        # String.Heredoc:            "#000000",
        # String.Interpol:           "#000000",
        # String.Other:              "#000000",
        # String.Regex:              "#000000",
        # String.Single:             "#000000",
        # String.Symbol:             "#000000",

        Number:                    "#b2b2b2",
        #Number.Float:              "#000000",
        #Number.Hex:                "#000000",
        #Number.Integer:            "#000000",
        #Number.Integer.Long:       "#000000",
        #Number.Oct:                "#000000",

        Operator:                  "#b2b2b2",
        Operator.Word:             "#b2b2b2",

        Punctuation:               "#b2b2b2",

        Comment:                   "#2aa1ae",
        # Comment.Hashbang:          "#000000",
        # Comment.Multiline:         "#000000",
        # Comment.Preproc:           "#000000",
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
