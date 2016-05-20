from io import BytesIO

from ..core import ExternalCommandTask
from ..utils import write_to_tmp_dir
from .basics import walk


class optipng(ExternalCommandTask):
    """Optimize PNG files with optipng (lossless compression)."""

    def __init__(self, *, level=None):
        self.level = level

    def process(self, inputs):
        tmp_dir, paths = write_to_tmp_dir(inputs)

        cmd = ['optipng']
        if self.level:
            cmd += ['-o{}'.format(self.level)]
        cmd += [str(f) for f in paths]

        self.run_external(cmd, cwd=tmp_dir)

        return walk(tmp_dir)


class pngquant(ExternalCommandTask):
    """Optimize PNG files with pngquant (lossy compression)."""

    def __init__(self, *, quality):
        self.quality = '{}'.format(quality)

    def process(self, inputs):
        for t, c, m in inputs:
            cmd = ['pngquant']
            if self.quality:
                cmd += ['--quality', self.quality]
            cmd += ['--', '-']
            c2 = self.run_external(cmd, input=b''.join(c))
            yield t, BytesIO(c2), m
