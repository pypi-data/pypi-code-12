from ply import yacc

from terrapin.lexer import Lexer
from terrapin.exceptions import TemplateError


class Parser(object):

    def __init__(self):

        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self, template, context):

        self.context = context

        if template:
            return self.parser.parse(template, lexer=self.lexer.lexer)

    def show_tokens(self, template):
        return self.lexer.tokenize(template)

    def p_output_list_1(self, p):
        """output_list : output
        """
        p[0] = ''.join([wrd for wrd in p[1:]])

    def p_output_list_2(self, p):
        """output_list : output_list output
        """
        p[0] = ''.join([wrd for wrd in p[1:]])

    def p_output(self, p):
        """output : block
                  | WS
                  | STRING
                  | WORD
                  | variable
        """
        p[0] = ''.join([wrd for wrd in p[1:]])

    def p_variable(self, p):
        'variable : LVARDELIM WORD RVARDELIM'
        p[0] = self.context.get(p[2], '')

    def p_if_else_statement(self, p):
        """block : if_result output_list else output_list end_if
        """
        p[0] = p[2] if p[1] else p[4]

    def p_empty_if_else_statement(self, p):
        """block : if_result else output_list end_if
        """
        p[0] = '' if p[1] else p[3]

    def p_if_statement(self, p):
        """block : if_result output_list end_if
        """
        p[0] = p[2] if p[1] else ''

    def p_truthy_if(self, p):
        """if_result : LCODEDELIM WS IF WS WORD WS RCODEDELIM
        """
        p[0] = True if self.context.get(p[5]) else False

    def p_equality_if(self, p):
        """if_result : LCODEDELIM WS IF WS WORD WS EQ WS QUOTEDSTRING WS RCODEDELIM
        """
        p[0] = True if self.context.get(p[5]) == p[9] else False

    def p_non_equality_if(self, p):
        """if_result : LCODEDELIM WS IF WS WORD WS NE WS QUOTEDSTRING WS RCODEDELIM
        """
        p[0] = True if not self.context.get(p[5]) == p[9] else False

    def p_else(self, p):
        """else : LCODEDELIM WS ELSE WS RCODEDELIM
        """
        p[0] = None

    def p_end_if(self, p):
        """end_if : LCODEDELIM WS ENDIF WS RCODEDELIM
        """
        p[0] = None

    def p_error(self, p):
        if p:
            raise TemplateError(p.lineno, p.lexpos, p.value)
        else:
            raise TemplateError(0, 0, '')
