import json
import subprocess

from pathlib import Path

from ..core import Task


class ng_annotate(Task):
    """Annotates static dependency injections for Angular source files."""

    def process(self, inputs):
        for t, c, m in inputs:
            cmd = ['ng-annotate', '-a', '-']
            output = subprocess.check_output(cmd, input=b''.join(c))
            yield t, [output], m


class ng_min(Task):
    """
    Rewrites Angular source files to be safe for minification.

    .. warning::
       ``ngmin`` does the same thing as ``ng-annotate`` tool, but the latter
       is much faster.  You can simply use ``ng_annotate()`` wherever you were
       using ``ng_min()``.
    """

    def process(self, inputs):
        for t, c, m in inputs:
            cmd = ['ngmin']
            output = subprocess.check_output(cmd, input=b''.join(c))
            yield t, [output], m


class ng_template_cache(Task):
    def __init__(self, target, module, create_module=False):
        self.module = module
        self.target = Path(target)
        self.create_module = create_module

    def lazy_template_cache(self, inputs):
        yield b'angular.module('
        yield json.dumps(self.module).encode('utf-8')
        if self.create_module:
            yield b', []'
        yield b').run(["$templateCache", function ($templateCache) {\n\n'

        for t, c, _ in inputs:
            yield b'    $templateCache.put('
            yield json.dumps(str(t)).encode('utf-8')
            yield b',\n'
            yield b'          '
            yield json.dumps(b''.join(c).decode('utf-8')).encode('utf-8')
            yield b');\n\n'

        yield b"\n}]);\n"

    def process(self, inputs):
        yield self.target, self.lazy_template_cache(inputs), {}
