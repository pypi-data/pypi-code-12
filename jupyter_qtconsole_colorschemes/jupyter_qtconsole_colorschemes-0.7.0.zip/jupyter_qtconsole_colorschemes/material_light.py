"""
A Pygments_ style based on the light background variant of Emacs material_ light. 

.. _Pygments: http://pygments.org/
.. _material: https://github.com/cpaulik/emacs-material-theme
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

class MaterialLightStyle(Style):
    background_color = "#fafafa"
    highlight_color = "#90a4ae"

    styles = {
        # No corresponding class for the following:
        Text:                      "#212121",
        # Whitespace:                "#000000",
        Error:                     "#b71c1c",
        # Other:                     "#000000",

        Keyword:                   "#00796b",
        Keyword.Constant:          "#689f38",  # e.g., None
        # Keyword.Declaration:       "#000000",
        Keyword.Namespace:         "#00796b",
        # Keyword.Pseudo:            "#000000",
        Keyword.Reserved:          "#00796b",
        Keyword.Type:              "#b71c1c",

        Name:                      "#212121",
        # Name.Attribute:            "#000000",
        Name.Builtin:              "#212121",
        Name.Builtin.Pseudo:       "#00796b",  # e.g., self
        Name.Class:                "#0097a7",
        # Name.Constant:             "#000000",
        Name.Decorator:            "bold #ce537a",
        # Name.Entity:               "#000000",
        Name.Exception:            "#b71c1c",
        Name.Function:             "#0097a7",
        Name.Label:                "#2196f3",
        Name.Namespace:            "#212121",
        # Name.Other:                "#000000",
        # Name.Tag:                  "#000000",
        Name.Variable:             "#ef6c00",
        # Name.Variable.Class:       "#000000",  
        # Name.Variable.Global:      "#000000",
        # Name.Variable.Instance:    "#000000",

        # Literal:                   "#000000",
        # Literal.Date:              "#000000",

        String:                    "#689f38",
        # String.Backtick:           "#000000",
        # String.Char:               "#2d9574",
        String.Doc:                "#672ab7",
        # String.Double:             "#000000",
        # String.Escape:             "#000000",
        # String.Heredoc:            "#000000",
        # String.Interpol:           "#000000",
        # String.Other:              "#000000",
        # String.Regex:              "#000000",
        # String.Single:             "#000000",
        # String.Symbol:             "#000000",

        Number:                    "#212121",
        #Number.Float:              "#000000",
        #Number.Hex:                "#000000",
        #Number.Integer:            "#000000",
        #Number.Integer.Long:       "#000000",
        #Number.Oct:                "#000000",

        Operator:                  "#212121",
        Operator.Word:             "#212121",

        Punctuation:               "#0097a7",

        Comment:                   "#607d8b",
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
