
import os
import tempfile
import subprocess
import shutil
import plac

from xmldirector.dita import util
from xmldirector.dita.logger import LOG
from xmldirector.dita import install


cwd = os.path.abspath(os.path.dirname(__file__))
DITA = os.path.join(cwd, 'converters', 'dita', 'bin', 'dita')
DITAC = os.path.join(cwd, 'converters', 'ditac', 'bin', 'ditac')


@plac.annotations(
    ditamap=("Path of the DITA Map file", 'option', 'd', str),
    output=("Output directory or file", 'option', 'o', str),
    converter=("DITA converter to be used: dita or ditac", "option", 'c', str),
    overwrite=("Overwrite existing output directory/file(s)", "flag", 'f', bool))
def dita2html(ditamap='', output=None, converter='dita', overwrite=False):

    if converter not in ('dita', 'ditac'):
        raise ValueError('Unknown DITA converter "{}"'.format(converter))

    if not ditamap or not os.path.exists(ditamap):
        raise IOError('DITA mapfile "{}" does not exist'.format(ditamap))

    if output and os.path.exists(output):
        if not overwrite:
            raise IOError('Output directory/file "{}" already exists (use --overwrite for cleanup)'.format(output))
        if os.path.isdir(output):
            shutil.rmtree(output)
        else:
            os.remove(output)

    if converter == 'dita':

        if not os.path.exists(DITA):
            install.install_converter('dita')

        if not output:
            output = tempfile.mkdtemp()
            output = os.path.abspath(output)
        cmd = '"{}" -f html5 -i "{}" -o "{}" -Droot-chunk-override=to-content'.format(DITA, ditamap, output)

    else:

        if not os.path.exists(DITAC):
            install.install_converter('ditac')

        if not output:
            output = tempfile.mktemp(suffix='.html')

        cmd = '"{}" -c single  -f xhtml "{}" "{}"'.format(DITAC, output, ditamap)

    LOG.info(cmd)
    status, cmd_output= util.runcmd(cmd)
    if status != 0:
        LOG.error(cmd_output)
        raise RuntimeError('Execution of "{}" failed (status {})'.format(cmd, status))

    return output


def main():
    import plac; plac.call(dita2html)


if __name__ == '__main__':
    main()
