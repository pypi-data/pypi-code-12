# -*- coding: utf-8 -*-
import mmap
import contextlib
import re

context_parser = None


class symbol(object):
    """This class represents a symbol for use in the
    parser generator. May be a terminal or not terminal
    symbol."""
    def __init__(self, name, parser=context_parser):
        """Initialize symbol"""
        self.name = name
        parser.AppendSymbol(self)
        super(symbol, self).__init__()


class terminal(symbol):
    """This class represents a terminal symbol"""
    def __init__(self, name, parser=context_parser):
        """Initialize a terminal symbol"""
        super(terminal, self).__init__(name, parser)


class literal(terminal):
    """This class represents a literal terminal simbol"""
    def __init__(self, charsequence, parser=context_parser):
        """Initialize a literal symbol"""
        name = 'LITERAL{}'.format(len(parser.literal) + 1)
        self.literal = charsequence
        super(literal, self).__init__(name, parser)


class nonterminal(symbol):
    """This class represents a non terminal symbol"""
    def __init__(self, name, parser=context_parser):
        """Initialize a non terminal symbol"""
        self._rules = []
        super(nonterminal, self).__init__(name, parser)

    def __ior__(self, rules, parser=context_parser):
        """Append rules"""
        rs = rules.split('|')
        # clean rules
        for r in rs:
            #analyze each rule
            rule = []
            ss = r.strip().split(' ')
            for s in ss:
                #analyze symbol: find it on parser
                assert(s in parser.symbol)
                rule.append(parser.symbol[s])
            self._rules.append(rule)

    def equivalent(self, other):
        """Check if the rules are the same for different symbols"""
        if self is other or type(other) != type(self):
            return False
        n = len(self._rules)
        if n != len(other._rules):
            return False
        return len([x for x in self._rules if x not in other._rules]) == 0

    def setRules(self, rules, parser=context_parser):
        """auxiliar method for assigning rules"""
        # The rules that we can handle can contain literal
        # symbols so we need to extract these symbols and
        # replace it by literal terminal symbols
        match = re.search(r"\'(((?<!\\)\\\'|[^\'])*)\'", rules)
        while match is not None:
            # get the literal text
            l = match.group(1)
            # find the literal in the parser
            if l not in parser.literal:
                #create a new literal
                lo = literal(l, parser)
                print("created new literal {l.name} = '{l.literal}'\n".format(l=lo))
            # ok, now, replace the literal
            rules = rules[:match.start(0)] + parser.literal[l].name + rules[match.end(0):]
            # and do next search
            match = re.search(r"\'(((?<!\\)\\\'|[^\'])*)\'", rules)
        # Ok, now, we need to parse each one of the rules but,
        # before doing so, we need to check the existence of subrules
        # embedded in the expressions. The possibilities are:
        # ...[subrule]... ...(subrule)...  and ...{subrule}...
        # These subrules are mapped to special symbols we called
        # option, subsymbol or sequence
        mapmatch = {
            'opt': (r"\[([^\]]*)\]", option),
            'sub': (r"\(([^\)]*)\)", subsymbol),
            'seq': (r"\{([^\}]*)\}", sequence)}
        for match_type in mapmatch:
            expr = mapmatch[match_type][0]
            hand = mapmatch[match_type][1]
            match = re.search(expr, rules)
            count = 0
            while match is not None:
                # get the rule text
                l = match.group(1)
                # ok, we create a subsymbol
                name = '{self.name}.{type}{count}'.format(self=self,
                    type=match_type, count=count)
                o = hand(name, parser)
                o.setRules(l, parser)
                count = count + 1
                # search in parser for equivalent symbol
                for sn in parser.symbol:
                    s = parser.symbol[sn]
                    if o.equivalent(s):
                        print("removed {o.name} by coincidence with {s.name}\n".format(
                            o=o, s=s))
                        del o
                        o = s
                        count = count - 1
                        break
                # replace the symbol
                rules = rules[:match.start(0)] + o.name + rules[match.end(0):]
                # do next search
                match = re.search(expr, rules)
                # Ok, now we find for subrules
        #Ok, now, we have pure rules and we separate it and process
        rs = rules.split('|')
        # clean rules
        self._rules = []
        for r in rs:
            #analyze each rule
            rule = []
            ss = r.strip().split(' ')
            for s in ss:
                if s not in parser.symbol:
                    print('Missing symbol {s}. Assumming terminal\n'.format(s=s))
                    terminal(s, parser)
                rule.append(parser.symbol[s])
            self._rules.append(rule)


class option(nonterminal):
    """Special nonterminal symbols"""
    def __init__(self, name, parser=context_parser):
        """Initialize """
        super(option, self).__init__(name, parser)


class subsymbol(nonterminal):
    """Special nonterminal symbols"""
    def __init__(self, name, parser=context_parser):
        """Initialize """
        super(subsymbol, self).__init__(name, parser)


class sequence(nonterminal):
    """Special nonterminal symbols"""
    def __init__(self, name, parser=context_parser):
        """Initialize """
        super(sequence, self).__init__(name, parser)


class parser(object):
    """This class defines a general parser generator.
    The generator analizes a sequence of terminal symbols
    for constructing the parser.

    Symbol kinds:

        * Terminal : output from scanner.
        * NonTerminal : expressed by semantic

    declaring rules:

        nonterminals = [
            nonterminal(parser,'const_expr'),
            nonterminal(parser,'mutable_expr'), ...]


        parser.const_expr = <expr1>|<expr2>|...|<exprN>

        each expression  is

            expression = "symbol"| "symbol expression"




    """
    def __init__(self, **kwargs):
        """Initialize parser"""
        global context_parser
        self.symbol = {}
        self.literal = {}
        context_parser = self
        super(parser, self).__init__()
        f = kwargs.get('file', None)
        if f:
            self.ReadFile(f)

    def AppendSymbol(self, symbol):
        """Appends the symbol"""
        self.symbol[symbol.name] = symbol
        if isinstance(symbol, terminal):
            setattr(self, symbol.name, property(
                lambda s: symbol,
                lambda s, v: eval("raise ValueError('terminal symbols are readonly')")))
            if type(symbol) is literal:
                self.literal[symbol.literal] = symbol
        elif isinstance(symbol, nonterminal):
            setattr(self, symbol.name, property(
                lambda s: symbol,
                lambda s, v: symbol.setRules(v, self)))

    def ReadFile(self, fname):
        """Read the parser definition from the file"""
        with open(fname, 'r') as f:
            with contextlib.closing(mmap.mmap(f.fileno(),
                0, access=mmap.ACCESS_READ)) as m:
                self.ReadString(m[:])

    def ReadString(self, sdef):
        """Read the parser definition from the string.
        The parser definition is written in the format:
            .<non-terminal> = rule 1|rule 2|

        The point character at beginning of each line
        is determinning the start of new non-terminal.
        """
        # split the string in non-terminal expressions
        expr = re.split(r'^\.', sdef, flags=re.M)

        #ok, create a map non-terminal -> definition
        nta = {}
        for k in expr:
            s = k.strip()
            if not len(s):
                continue
            i = s.find(':')
            if i < 1:
                print('invalid expression {}\n'.format(s))
                continue
            nts = s[:i].strip()
            rts = s[i + 1:].strip()
            if not re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', nts):
                print('invalid non terminal identifier {}\n'.format(nts))
                continue
            if nts in nta:
                print('duplicated symbol {}\n'.format(nts))
            nta[nts] = rts
        #ok, first create the symbols
        vsy = {}
        for nts in nta:
            vsy[nts] = nonterminal(nts, parser=self)
            print('registered non terminal symbol {}'.format(nts))
            #now, we need to analize each entry: first, extract
            #literals
        #now, assign rules
        for nts in nta:
            vsy[nts].setRules(nta[nts], self)
        return



