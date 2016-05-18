 
defaultStyle = \
'''
QTextEdit, QPlainTextEdit, QTableView, QHeaderView {
    font-family: Courier New, monospace;
    font-size: 10pt;
}

BaseTextEdit {
    qproperty-current_line_color : white;
    qproperty-current_line_background : blue;
    qproperty-current_line_color : white;
    qproperty-current_line_background : Fuchsia;
}

QTableView {
    selection-background-color: blue;
}

QTableView::item {
    padding-right: 10px;
    padding-left: 10px;
    padding-top: 0px;
    padding-bottom: 0px;
}
        
QHeaderView::section
{
    border: 0px;
    padding-right: 10px;
    padding-left: 10px;
    padding-top: 0px;
    padding-bottom: 0px;
    margin: 0px;
}

'''


defaultCss = \
'''
.symbol {
    color : blue;
}

.sourcefile {
    color : blue;
}

.filename {
    color : blue;
}

.dir {
    color : black;
}

.error {
    color : red;
}

.current {
    background-color : fuchsia;
}

.breakpoint {
    background-color : red;
}

.selected {
    background-color : gray;
}

body {
    margin: 0;
}

pre {
    margin: 0;
}

.highlight .c { color: #008000 } /* Comment */
.highlight .err { border: 1px solid #FF0000 } /* Error */
.highlight .k { color: #0000ff } /* Keyword */
.highlight .cm { color: #008000 } /* Comment.Multiline */
.highlight .cp { color: #0000ff } /* Comment.Preproc */
.highlight .c1 { color: #008000 } /* Comment.Single */
.highlight .cs { color: #008000 } /* Comment.Special */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gh { font-weight: bold } /* Generic.Heading */
.highlight .gp { font-weight: bold } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { font-weight: bold } /* Generic.Subheading */
.highlight .kc { color: #0000ff } /* Keyword.Constant */
.highlight .kd { color: #0000ff } /* Keyword.Declaration */
.highlight .kn { color: #0000ff } /* Keyword.Namespace */
.highlight .kp { color: #0000ff } /* Keyword.Pseudo */
.highlight .kr { color: #0000ff } /* Keyword.Reserved */
.highlight .kt { color: #2b91af } /* Keyword.Type */
.highlight .s { color: #a31515 } /* Literal.String */
.highlight .nc { color: #2b91af } /* Name.Class */
.highlight .ow { color: #0000ff } /* Operator.Word */
.highlight .sb { color: #a31515 } /* Literal.String.Backtick */
.highlight .sc { color: #a31515 } /* Literal.String.Char */
.highlight .sd { color: #a31515 } /* Literal.String.Doc */
.highlight .s2 { color: #a31515 } /* Literal.String.Double */
.highlight .se { color: #a31515 } /* Literal.String.Escape */
.highlight .sh { color: #a31515 } /* Literal.String.Heredoc */
.highlight .si { color: #a31515 } /* Literal.String.Interpol */
.highlight .sx { color: #a31515 } /* Literal.String.Other */
.highlight .sr { color: #a31515 } /* Literal.String.Regex */
.highlight .s1 { color: #a31515 } /* Literal.String.Single */
.highlight .ss { color: #a31515 } /* Literal.String.Symbol */
'''
