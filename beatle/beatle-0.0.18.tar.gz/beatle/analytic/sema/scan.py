# -*- coding: utf-8 -*-
import re
import mmap
import contextlib as _ctx


class scan(object):
    """
    Defines the base class for a lexical scanner.
    The scanner is composed by five logical sections:

        definitions: A list of pattern definitions that may be
        applied to rules patterns.

        lexicals: A list of output values for mached rule output.

        states: A list of scanner states.

        rules: A list of rules that may be applied secuentially
        consuming the input stream.

        methods: Set of methods applied during the work. They
        must be implemented in derived class.

    Notes:

        The scanner may be applied to file for analysis. For
        that, we must use scan.filescan(file)

        lexical values are for use into parser generator. The
        None symbol is allways a lexical value

    Adding definitions:

        We add a new definition (remember the use of raw strings)
        using the pdef method:

            pdef('alpha','[a-zA-Z]')

    Adding lexicals:

        We add lexicals for parser generator by calling plex:

            plex('identifier')

    Adding states:

        The states are inclusive or exclusive and declared with
        pstate('name',inclusive=True). As usual, the BEGIN state
        inits the scanner process and the scanner state may select
        the active rules. If the user don't defines the BEGIN
        state, it will be defined as inclusive.

    Adding rules:

        Rules are declared with the method prule specifying the
        rule name, the regexpr to match, a collection of
        start conditions (if any) and a optional method to execute
        when the rule is matched. The optional method can return
        a lexical for use in the parser generator.
        The rules follow the syntax of python regexpr module,
        but they can include single quoted definitions (and yes,
        the quotes may be now scaped for normal use). For example,

        prule('label',"'alpha'*",do=self.method)

    Conecting with parser generator:
        Pass the parser argument for conection in __init__.

    """

    def __init__(self, parser=None):
        """Initialize a lexical scanner."""
        self._defs = {}
        self._lex = [None]
        self._states = [[], []]
        self._rules = []
        self._state = None
        self._inclusive = True
        self._parser = parser
        super(scan, self).__init__()

    def pdef(self, key, value):
        """Add new definition to a lexical scanner"""
        self._defs[key] = value

    def plex(self, id):
        """Add new lexical identifier"""
        self._lex.append(id)

    def pstate(self, name, inclusive=True):
        """Add new state to scanner"""
        if inclusive:
            self._states[0].append(name)
        else:
            self._states[1].append(name)

    def prule(self, label, rule, *args, **kwargs):
        """Add a new rule to scanner"""
        s = rule
        #expand definitions
        for d in self._defs:
            s = re.sub(r"(?<!\\)'{}'".format(d),
                self._defs[d], s)
        #remove scaped quotes
        s = re.sub(r"\\'", "'", s)
        #register mask
        self._rules.append({
            'name': label,
            'pattern': re.compile(s),
            'conditions': args,
            'do': kwargs.get('do', lambda x: None)
            })

    def begin(self, state):
        """do a new state"""
        if state in self._states[0]:
            self._inclusive = True
        elif state in self._states[1]:
            self._inclusive = False
        else:
            raise ValueError('unknown state {}'.format(state))
        self._state = state

    def filescan(self, rfile):
        """do a lexical scan over a file"""
        with _ctx.closing(mmap.mmap(rfile, prot=mmap.PROT_READ)) as m:
            return scan(m[:])

    def scan(self, s):
        """do a scan. Return true if the scanner
        has matched the string, and false otherwise"""
        if None not in self._states[0] and None not in self._states[1]:
            self._state[0].append(None)
        self.begin(None)
        if self._parser:
            self._parser.reset()
        # Ok we find the next match
        pos = 0
        nxt = True
        while nxt and pos < len(s):
            nxt = False
            for rule in filter(self.active, self._rules):
                match = rule['pattern'].match(s, pos)
                if match is None:
                    continue
                value = rule['do'](match)
                if value and self._parser:
                    self._parser.put(value)
                pos += len(match.m.group(0))
                nxt = True
                break
        return nxt

    def active(self, rule):
        """Returns info about if some rule is active or not"""
        cond = rule['conditions']
        return (not len(cond) and self._inclusive) or (
                self._state in cond)


