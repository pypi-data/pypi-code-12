# @Author: BingWu Yang <detailyang>
# @Date:   2016-03-29T17:47:44+08:00
# @Email:  detailyang@gmail.com
# @Last modified by:   detailyang
# @Last modified time: 2016-04-10T16:54:56+08:00
# @License: The MIT License (MIT)


import ply.yacc as yacc
import eslast as ast

from esllexer import ESLLexer


tokens = ESLLexer.tokens


def p_request(p):
    '''request : URL
           | URL METHOD
           | URL METHOD OPTIONS'''
    if len(p) == 2:
        p[0] = ast.RequestNode(ast.MethodNode('GET'), ast.URLNode(p[1]), None)
    elif len(p) == 3:
        p[0] = ast.RequestNode(ast.MethodNode(p[2]), ast.URLNode(p[1]), None)
    else:
        p[0] = ast.RequestNode(ast.MethodNode(p[2]), ast.URLNode(p[1]), p[3])

def p_options(p):
    '''OPTIONS :
              | OPTION
              | OPTIONS OPTION'''
    if len(p)  == 2:
        p[0] = ast.OptionListNode([p[1]])
    else:
        p[0] = p[1].append(p[2])

def p_option_empty(p):
    ' OPTION :   empty '
    p[0] = p[1]

def p_option_header(p):
    ' OPTION :   HEADERVALUE '
    p[0] = p[1]

def p_option_querystring(p):
    ' OPTION :  QUERYSTRINGVALUE '
    p[0] = p[1]

def p_option_body(p):
    ' OPTION : BODYVALUE '
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []

def p_querystring_value(p):
    '''QUERYSTRINGVALUE : QUERYSTRING VALUE '''
    p[0] = ast.OptionNode(ast.QueryStringNode(p[1]), ast.ValueNode(p[2]))

def p_querystring_shell(p):
    '''QUERYSTRINGVALUE : QUERYSTRING SHELL '''
    p[0] = ast.OptionNode(ast.QueryStringNode(p[1]), ast.ShellNode(p[2]))

def p_header_value(p):
    '''HEADERVALUE : HEADER VALUE '''
    p[0] = ast.OptionNode(ast.HeaderNode(p[1]), ast.ValueNode(p[2]))

def p_header_shell(p):
    '''HEADERVALUE : HEADER SHELL '''
    p[0] = ast.OptionNode(ast.HeaderNode(p[1]), ast.ShellNode(p[2]))

def p_body_value(p):
    '''BODYVALUE : BODY VALUE '''
    p[0] = ast.OptionNode(ast.BodyNode(p[1]), ast.ValueNode(p[2]))

def p_body_shell(p):
    '''BODYVALUE : BODY SHELL '''
    p[0] = ast.OptionNode(ast.BodyNode(p[1]), ast.ShellNode(p[2]))

def p_error(p):
    print("Syntax Error")
    print("ESL format: {URL} {METHOD} {OPTIONS}")
    print("{URL}: https://example.com|examples.com|/api/endpoints")
    print("{METHOD}: GET|get|POST|post|DELETE|delete|PUT|put")
    print("{OPTIONS}: --hContent-Type=application/json")
    print("{OPTIONS}: --qper_page=1")
    print("{OPTIONS}: --busername=xxxx")

def parse(text):
    parser = yacc.yacc(debug=True)
    ast = parser.parse(text, ESLLexer().build())
    return ast

if __name__ == '__main__':
    ast = parse("/api/cmdb/peoples/ get --qhost_ip=!(ifconfig eth0) --qhost_name=bj-sdf --hContent-Type=abcd --bslkjsdf=123")     # Test it
    print(ast.left)
    print(ast.method)
    for option in ast.right.options:
        key = option.key
        value = option.value
