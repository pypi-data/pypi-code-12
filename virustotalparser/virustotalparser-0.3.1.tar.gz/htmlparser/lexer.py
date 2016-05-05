import ply.lex as lex


class Lexer:
    states = (
        ('script', 'exclusive'),
        ('quotes', 'exclusive'),
    )

    tokens = (
        'OPEN',
        'CLOSE',
        'ASSIGN',
        'QUOTE',
        'WORD',
        'OPEN_DASH',
        'ESCAPE',
        'WHITESPACE'
    )

    def t_ANY_WHITESPACE(self, t):
        r'\s'
        pass

    def t_script_OPEN_DASH(self, t):
        r'</'
        t.lexer.pop_state()
        return t

    def t_script_QUOTE(self, t):
        r'"'
        t.lexer.push_state('quotes')
        t.type = "WORD"
        return t

    def t_script_WORD(self, t):
        r'[^ ]+'
        return t

    def t_quotes_ESCAPE(self, t):
        r'\[^ ]'
        t.type = "WORD"
        return t

    def t_quotes_QUOTE(self, t):
        r'"'
        t.lexer.pop_state()
        t.type = "WORD"
        return t


    def t_quotes_WORD(self, t):
        r'[^" ]+'
        return t

    def t_OPEN_DASH(self, t):
        r'</'
        return t

    def t_OPEN(self, t):
        r'<'
        return t

    def t_CLOSE(self, t):
        r'>'
        return t

    def t_ASSIGN(self,t ):
        r'='
        return t

    def t_QUOTE(self, t):
        r'"'
        return t

    def t_WORD(self, t):
        r'[^><"= ]+'
        return t

    def t_ANY_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        t = t.lexer.token()
        return t

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        self.lexer.input(data)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
