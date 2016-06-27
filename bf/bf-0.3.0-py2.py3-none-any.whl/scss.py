
DEBUG = False

import os, re, sys
import sass                 # pip install sass
from unum import Unum       # pip install unum
from bl.dict import Dict    # ordered dict with string keys
from bl.string import String
from bf.text import Text

Unum.UNIT_FORMAT = "%s"
Unum.UNIT_INDENT = ""
Unum.VALUE_FORMAT = "%s"

pt = Unum.unit('pt')
px = Unum.unit('px', 0.75*pt)
em = Unum.unit('em', 12.*pt)
en = Unum.unit('en', 6.*pt)
inch = Unum.unit('in', 72.*pt)
pi = Unum.unit('pi', 12.*pt)
percent = Unum.unit('%', 0.01*em)
    
class Styles(Dict):
    def keys(self):
        """Sort the keys: Alphabetical, except if a rule @extend a base rule, the base rule is earlier."""
        alpha_keys = Dict.keys(self)    # Dict.keys() does alphabetical sort
        sorted_keys = []
        while len(alpha_keys) > 0:
            key = alpha_keys[0]
            style = self[key]
            if DEBUG==True: print(key, end=' ')
            while style.get('@extend') is not None:
                next_key = style.get('@extend').strip(' ;')
                if next_key in sorted_keys: break
                key = next_key
                style = self[key]
                if DEBUG==True: print('@extend', key, end=' ')
            sorted_keys.append(key)
            _ = alpha_keys.pop(alpha_keys.index(key))
            if DEBUG==True: print()
        return sorted_keys

class SCSS(Text):
    # the style rules are keys in the "styles" dict. This is limiting, but it works --  
    # it happens to result in things being ordered correctly (with @-rules first), and 
    # it allows us to effectively query and manipulate the contents of the stylesheet at any time.

    def __init__(self, **args):
        # TODO: add parsing of text input into self.styles
        Text.__init__(self, **args)
        if self.styles is None:
            self.styles = Styles()

    def write(self, fn=None, text=None, **args):
        Text.write(self, fn=fn, text=text, **args)

    def render_css(self, fn=None, text=None):
        """output css using the Sass processor"""
        from bl.css import CSS
        c = CSS(fn=fn or os.path.splitext(self.fn)[0]+'.css')
        if not os.path.exists(os.path.dirname(c.fn)):
            os.makedirs(os.path.dirname(c.fn))
        # the following is necessary in order for scss to relative @import
        os.chdir(os.path.dirname(c.fn)) 
        # grumble about the use of bytes rather than unicode.
        b = bytes(text or self.text or self.render(self.styles), 'utf-8') 
        if len(b)==0: 
            c.text = ''
        else: 
            try:
                c.text = sass.compile(string=b)
            except:
                c.text = sass.compile_string(b).decode('utf-8')
        return c
    
    @classmethod    
    def render(c, styles, margin="", indent="\t"):
        """output scss text from styles. 
        margin is what to put at the beginning of every line in the output.
        indent is how much to indent indented lines (such as inside braces)."""
        
        def render_dict(d):
            return ('{\n' 
                    + c.render(styles[k], 
                        margin=margin+indent,   # add indent to margin
                        indent=indent) 
                    + '}')

        # render the scss text
        s = ""
        for k in styles.keys():
            if DEBUG==True: print(margin, k, styles[k])
            s += margin + k + ' '
            if type(styles[k]) in [str, String]:
                s += styles[k] + ';'
            elif type(styles[k])==Unum:
                s += str(styles[k]) + ';'
            elif type(styles[k]) in [dict, Dict]:
                s += render_dict(styles[k])
            elif type(styles[k]) in [tuple, list]:
                for i in styles[k]:
                    if type(i) in [str, String]:
                        s += i + ' '
                    if type(i) == bytes:
                        s += str(i, 'utf-8') + ' '
                    elif type(i) in [dict, Dict]:
                        s += render_dict(i)
            else:
                print(margin, type(styles[k]), k, styles[k], file=sys.stderr)
                s += ';'
            s += '\n'
        return s
