from io import BytesIO

from pathlib import Path

from ..core import ExternalCommandTask
from ..io import lazy_read
from ..utils import write_to_tmp_dir
from .basics import walk


class autoprefixer(ExternalCommandTask):
    def __init__(self, browsers=None):
        self.browsers = browsers

    def lazy_prefix(self, contents):
        cmd = ['postcss', '--use', 'autoprefixer']
        if self.browsers:
            cmd += ['--autoprefixer.browsers', self.browsers]

        output = self.run_external(cmd, input=b''.join(contents))
        yield output

    def process(self, inputs):
        for t, c, m in inputs:
            yield t, self.lazy_prefix(c), m


class cleancss(ExternalCommandTask):
    """Minifies CSS input files."""

    def __init__(self, *, s0=None, s1=None, keep_line_breaks=None):
        self.s0 = s0
        self.s1 = s1
        self.keep_line_breaks = keep_line_breaks

    def lazy_clean(self, c):
        cmd = ['cleancss']
        if self.s0:
            cmd += ['--s0']
        if self.s1:
            cmd += ['--s1']
        if self.keep_line_breaks:
            cmd += ['--keep-line-breaks']
        yield self.run_external(cmd, input=b''.join(c))

    def process(self, inputs):
        for t, c, m in inputs:
            if t.suffix != '.css':
                yield t, c, m
                continue

            yield t, self.lazy_clean(c), m


class lessc(ExternalCommandTask):
    """
    Compile LESS files to CSS.

    There are two modes to invoke the LESS compiler.

    The default mode passes the input .less files to lessc's stdin.  This
    method has the advantage of being slightly quicker, as no temporary files
    have to be created.

    The second method writes the input files to a temporary directory before
    invoking the less compiler, meaning you can use @import statements in the
    .less files.
    """

    def __init__(self, *files, line_numbers=None, source_map=False, extra_options=None):
        self.files = files
        self.line_numbers = line_numbers
        self.source_map = source_map
        self.extra_options = extra_options

    def process_via_stdin(self, inputs):
        for t, c, m in inputs:
            if t.suffix != '.less':
                yield t, c, m
                continue

            t2 = t.with_suffix('.css')
            t2_smap = t2.with_name(t2.name + '.map')

            cmd = ['lessc']
            if self.source_map:
                # TODO: Change this to write to a safer temporary directory
                cmd += ['--source-map=/tmp/_sm.map',
                        '--source-map-url=' + str(t2_smap.name)]
            if self.line_numbers:
                cmd += ['--line-numbers=' + self.line_numbers]
            if self.extra_options:
                cmd += self.extra_options

            cmd += ['-']

            output = self.run_external(cmd, input=b''.join(c))
            yield t2, BytesIO(output), m
            if self.source_map:
                yield t2_smap, lazy_read('/tmp/_sm.map'), m

    def process_via_tmp_dir(self, inputs):
        tmp_dir, paths = write_to_tmp_dir(inputs)

        base_cmd = ['lessc']
        if self.line_numbers:
            base_cmd += ['--line-numbers=' + self.line_numbers]

        if self.source_map:
            base_cmd += ['--source-map-less-inline',
                         '--source-map-map-inline']

        if self.extra_options:
            base_cmd += self.extra_options

        for f in self.files:
            output_path = Path(f).with_suffix('.css')

            self.run_external(base_cmd + [str(f), str(output_path)],
                              cwd=tmp_dir)

        for t, c, m in walk(tmp_dir):
            if t not in paths:  # filter out any input files, returning only the new files
                yield t, c, m

    def process(self, inputs):
        if self.files:
            return self.process_via_tmp_dir(inputs)
        else:
            return self.process_via_stdin(inputs)
