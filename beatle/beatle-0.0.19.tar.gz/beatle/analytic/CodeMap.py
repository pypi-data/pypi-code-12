# -*- coding: utf-8 -*-
import wx
import re

class CodeMap(object):
    """Class for analysis of code. The main target
    for this method is to make the analysis of the
    method code previous to any editor point. The
    analyser, for that reason, dont expect correct
    code."""
    def __init__(self, macrodef={}):
        """initialize codemap"""
        self._language = "C++"
        self._version = "03"
        self.no_for_scope = False
        self.strmap = {}
        self.macrodef = macrodef

        #regexpr
        self._forexpr = re.compile(r'\bfor\b\s*\(([^;\)]*);([^;\)]*);([^;\)]*)\)')
        self._whilexpr = re.compile(r'\bwhile\b\s*\([^\)]*\)')

        #setup
        self.inString = False
        self.inLineComment = False
        self.inTextComment = False
        # clean macros
        for macro in self.macrodef:
            self.macrodef[macro] = self.join_splits(self.macrodef[macro])

        super(CodeMap, self).__init__()

    def remove_comments(self, code):
        """Return code without comments"""
        left = ''
        right = code.strip()
        while len(right):
            starts = [right.find(s) for s in ['//', '/*', '"']]
            i = 0
            v = 0
            try:
                v = min([x for x in starts if x > -1])
            except:
                #there are no comments
                return left + right
            i = starts.index(v)
            if i == 0:
                #is a C++ line comment
                left += right[:v]
                right = right[v:]
                ends = [right.find(s) for s in ['\r', '\n']]
                try:
                    v = min([x for x in ends if x > -1])
                except:
                    # is the last line, no continuation
                    self.inLineComment = True
                    return left
                if v + 1 < len(right):
                    if right[v + 1] in '\r\n':
                        v += 1
                right = right[v + 1:]
                continue
            if i == 1:
                #is a C compound line comment
                left += right[:v]
                right = right[v:]
                v = right.find('*/')
                if v == wx.NOT_FOUND:
                    #be patient ...
                    #raise SyntaxError("unclosed comment ...{}".format(left[-10:]))
                    self.inTextComment = True
                    return left
                right = right[v + 2:]
            else:
                #It's a string
                #v = v + 1
                # replace string by @str<num>
                si = '@str{}'.format(len(self.strmap) + 1)
                left += right[:v]
                left += si
                right = right[v + 1:]
                v = right.find('"')
                if v == wx.NOT_FOUND:
                    self.strmap[si] = right
                    #we are analysing incomplete code,
                    #keep that in mind ...
                    #raise SyntaxError("unclosed string ...{}".format(left[-10:]))
                    self.inString = True
                    return left
                self.strmap[si] = right[:v]
                v = v + 1
                #left += right[:v]
                right = right[v:]
        return left + right

    def remove_macro_alternative(self, code):
        """
        Remove inactive by macro. When we are coding something
        and we are inside the #else part of macro condition, we can
        completely discard all the code inside the #if block.
        Also, if we have completed #if/#else/#endif sections inside
        the analysed code, the variables defined with the same name
        in both of the blocks will be in conflict if his types are
        not compatibles, or downgraded to the common base class for
        the declarations.
        So, when analysing macro conditions not only we do the removal
        of #if sections from open #else's, but also check the conflicts
        and base types for matching name vars.
        In resume,
            for complete #if/#else/#endif
                - downgrade of matching name vars to high common base
                - warn unmatching vars
                - warn missing vars in some counterpart
            for incomplete #else
                - check of already declared vars with #if counterpart
                - removal of #if code
                - warn missing vars"""

        left = ''
        right = code
        count = 0
        kpos = {}
        while len(right) > 0:
            # find delimitters
            d = [right.find(x) for x in ['#if', '#endif']]
            try:
                v = min([x for x in d if x > -1])
            except:
                # there are not more conditions
                # check about the else presence
                if count:
                    d = right.find('#else')
                    if d > -1:
                        left += right[:d]
                        right = right[d:]
                        #remove macro
                        d = right.find('\n') + 1
                        if d > 0:
                            right = right[d:]
                        else:
                            right = right[5:]
                        #we can discard the inner #if:

                return left + right
            left += right[:v]
            right = right[v:]
            i = d.index(v)
            if i == 0:
                count += 1
                kpos[count] = len(left)
                left += "#if"
                right = right[3:]
            elif i == 1:
                left += "#endif"
                right = right[6:]
                count -= 1

    def remove_control(self, code):
        """Remove control sentences from text"""
        # 1º for(<init>;<cond>;<iter>){ will be transformed into
        #    <init>;{ or {<init>; depending on no_for_scope
        it = self._forexpr.finditer(code)
        matches = []
        initializers = []
        remove = []
        for match in it:
            span = match.span()
            #if this is a single line statement, ignore it
            k = code[span[1]:].strip()
            remove.append(len(k) == 0 or k[0] != '{')
            matches.append(span)
            initializers.append(match.group(1))
        # Ok, proceed to reemplace code
        s = ''
        last = len(code)
        for i in range(len(matches) - 1, -1, -1):
            span = matches[i]
            if not remove[i]:
                s = code[span[1]:last] + s
                if self.no_for_scope:
                    s = '{};'.format(initializers[i]) + s
                else:
                    #search pos
                    k = s.find('{')
                    s = '{{{};'.format(initializers[i]) + s[k + 1:]
            else:
                # move last to skip line
                k = code.find(';', span[1])
                if k > -1:
                    s = code[k + 1:last] + s
            last = span[0]
        code = code[:last] + s
        # 2º Ok, now we will remove while sentences
        matches = [x.span() for x in self._whilexpr.finditer(code)]
        s = ''
        last = len(code)
        for i in range(len(matches) - 1, -1, -1):
            s = code[matches[i][1]:last] + s
            last = matches[i][0]
        code = code[:last] + s
        return code

    def remove_closed_statements(self, code):
        """Each closed statement dont contribute for context variables"""
        o = code.split('{')
        s = 0
        for i in range(0, len(o)):
            v = o[i + s].split('}')
            for j in range(1, len(v)):
                if i + s < 0:
                    continue
                    #strictly speaking is an error, but we need
                    #to be rude people here ...
                    #raise SyntaxError("unbalanced statements")
                del o[i + s]
                s = s - 1
        #ok, recompose and return
        s = ""
        for i in range(0, len(o)):
            s += o[i] + "{"
        return s[:-1]

    def join_splits(self, code):
        """remove linesplits (ie. end line with '\' character) by
        joining that lines"""
        code = code.replace('\\\r\n', '')
        code = code.replace('\\\r', '')
        code = code.replace('\\\n', '')
        return code

    def apply_macrodef(self, macro, code):
        """Apply any macro to code"""
        if macro in code and macro in self.macrodef:
            code = code.replace(macro, self.macrodef[macro])
            code = self.remove_comments(code)
        return code

    def capture_vars(self, code):
        """Get variables in the code, with type"""
        # The input code only holds active statements
        # so his structure is <code>{<code>{...
        # without closed statement. The process now
        # is easy. First, replace remaining open statements
        # with ;
        code = code.replace('{', ';')
        # now, split in stements and process each one
        statements = code.split(';')
        for s in statements:
            self.process_statement(s)

    def process_statement(self, statement):
        """Process an statement and extract variables"""
        s = statement.strip()
        if len(s) == 0:
            return
        #remove macros
        while s[0] == '#':
            i = s.find('\n')
            if i < 0:
                return
            s = s[i + 1:]
            if not len(s):
                return
        #we dont accept embedded typedef's
        #classes or struct's for now.
        if re.match('\btypedef\b.*'):
            return
        if re.match('\bclass\b.*'):
            return
        if re.match('\bstruct\b.*'):
            return

        # process enums




    def body_analyse(self, code):
        """Analyse body of method"""
        # remove line splits
        code = self.join_splits(code)
        # remove comments and extract strings for simplify
        code = self.remove_comments(code)
        # remove macro counterparts
        code = self.remove_macro_alternative(code)
        for macro in self.macrodef:
            code = self.apply_macrodef(macro, code)
        # remove control sentences
        code = self.remove_control(code)
        # closed statements dont contribute with declarations
        code = self.remove_closed_statements(code)
        self.capture_vars(code)
        return code

