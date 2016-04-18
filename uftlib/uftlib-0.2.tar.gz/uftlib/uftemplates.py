#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging
import linecache
import copy

from string import Template
logger = logging.getLogger(__name__)


class ExtraDict(dict):
    """ Creates a dict-like structure where we can store the new values of
    variables, while keeping the old (initial) ones as well. This is useful
    for a local-style context for running code with exec.
    """
    def __init__(self, d, extra):
        """
        :param d: base dictionary
        :param extra: extra dictionary where we keep the modifications
        """
        self.d = d
        self.extra = extra
        self._extrabackup = copy.deepcopy(extra)

    def __getitem__(self, key):
        if key in self.extra:
            return self.extra[key]
        if key in self.d:
            return self.d[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.extra[key] = value

    def reset(self):
        """ Reset the local context to the same state as it was when it was
        created.
        """
        self.extra = copy.deepcopy(self._extrabackup)


class UFTemplate(object):
    def __init__(self, initial="", oncycle="", template="",
                 debug=False, **kwargs):
        """ Runs the code from initial once, during initialization, and then,
        run the code in oncycle and render the template using the variables
        obtainted in that context

        :param initial: valid python code which is run only once during
        UFTemplate object creation
        :param onycyle: valid python code which is run before rendering the
        template
        :param template: a string used with string.Template to render the
        output. The variables are obtained from either initial or oncycle
        or submitted as kwargs during object creation
        """
        self.debug = debug

        self.baseenv = {}
        self.initial = initial
        self.oncycle = oncycle
        self.template = template

        self.cycleenv = {}
        compiled_initial = compile(self.initial, '<string-1>', 'exec')
        linecache.cache['<string-1>'] = len(self.initial), None, self.initial.split("\n"), '<string-1>'

        try:
            exec(compiled_initial, self.baseenv)
        except:
            raise

        for k, v in kwargs.items():
            if self.debug:
                logger.debug("Setting %s as %s" % (k, v))
            self.baseenv[k] = v

        if self.debug:
            logger.debug("After initial eval, we have the following values:")
            for k, v in self.baseenv.items():
                logger.debug("\tVariable %s = %s" % (k, repr(v)))

        self.compiled = compile(self.oncycle, '<string-2>', 'exec')
        linecache.cache['<string-2>'] = len(self.oncycle), None, self.oncycle.split("\n"), '<string-2>'
        self.localcontext = ExtraDict(self.baseenv, self.cycleenv)

    def render(self):
        """ Renders one template
        """
        try:
            exec(self.compiled, self.localcontext)
        except:
            raise

        if self.debug:
            logger.debug("On initial, we have the following values:")
            for k, v in self.localcontext.d.items():
                logger.debug("\t[Initial] %s = %s" % (k, repr(v)))
            logger.debug("On cycle, we have the following values:")
            for k, v in self.localcontext.extra.items():
                logger.debug("\t[Cycle] %s = %s" % (k, repr(v)))
        try:
            return Template(self.template).substitute(self.localcontext)
        except:
            logger.exception("Could not render")
            raise

    def render_many(self, howmany=1):
        """ Renders a number of templates and returns an array of strings

        :param howmany: Number of times to run the template
        and generate outputs
        """
        t0 = time.time()
        renders = []
        for _ in range(howmany):
            _sr = self.render()
            if _sr:
                renders.append(_sr)
        t1 = time.time()
        if self.debug:
            logger.debug("Rendered many: howmany=%d, took %2.2f seconds, \
speed=%5d/second" % (howmany, (t1-t0), (howmany/(t1-t0))))
        return renders

    def reset(self):
        self.localcontext.reset()

if __name__ == "__main__":
    initial = """
import datetime
def f(x):
    return x*x

def getnow():
    return str(datetime.datetime.now())

a = 0
b = 100
i = 0
"""

    oncycle = """
a += 3
i += 1
s = f(i)
b += a
now = getnow()
"""

    template = """Now = ${now}
Render nr. ${i}
f(${i}) = ${s}
b = ${b}
We live in ${where}"""

    tpl = UFTemplate(initial, oncycle, template, where="Indonezia")
    for text in tpl.render_many(3):
        print(text)

    tpl.reset()
    for text in tpl.render_many(3):
        print(text)
