from errorpro.parsing.generated import DatParser
from grako.buffering import Buffer
import re
import os.path as path
import os


IMPORT_RE = '^\s*import\s*\(\s*"(.*)"\s*\)\s*$'
EOL_COMMENTS_RE = "#.*$"

def get_code(filename, from_dir):
    f = open(path.join(from_dir, filename))
    code = f.read()
    code = re.sub(IMPORT_RE, lambda match: get_code(match.group(1), path.dirname(path.abspath(filename))), code, 0, re.MULTILINE)
    return code

def parse_file(filename):
    code = get_code(filename, os.getcwd())
    return parse(code)

def parse(code):
    p = DatParser(
        whitespace=" \t",
        eol_comments_re=EOL_COMMENTS_RE
    )
    ast = p.parse(
        code,
        'program',
        parseinfo=True,
        semantics = DatSemantics()
    )
    return ast

class DatSemantics(object):
    def subformula(self, ast):
        if ast is None:
            return ast
        else:
            return ''.join(ast)

    def longname(self, ast):
        if ast is None:
            return ast
        else:
            if isinstance(ast, list):
                ast = (x for y in ast for x in y) #flatten array
            return ''.join(ast).strip()

    def _default(self, ast):
        return ast
