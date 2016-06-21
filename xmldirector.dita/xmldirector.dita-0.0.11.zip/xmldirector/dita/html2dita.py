################################################################
# xmldirector.dita
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import tempfile
import shutil
import pkg_resources

from xmldirector.dita import util


for name in ('saxon9', 'saxon8', 'saxon7', 'saxon'):
    saxon = shutil.which(name)
    if saxon:
        break

h2d_xsl = pkg_resources.resource_filename('xmldirector.dita.converters.h2d', 'h2d.xsl')
info_types = ('topic', 'concept', 'reference', 'task')


def html2dita(html_filename, infotype, output_filename=None):

    if not infotype in info_types:
        raise ValueError('Unsupported infotype "{}"'.format(infotype))

    if not output_filename:
        output_filename = tempfile.mktemp(suffix='.dita')

    cmd = '"{saxon}" "{html_filename}" "{h2d_xsl}" infotype={infotype} >"{output_filename}"'.format(
            saxon=saxon,
            html_filename=html_filename,
            h2d_xsl=h2d_xsl,
            infotype=infotype,
            output_filename=output_filename)

    status, output = util.runcmd(cmd)
    if status != 0:
        raise RuntimeError('html2dita() failed: {}'.format(output))
    return output_filename


if __name__ == '__main__':
    import sys
    html2dita(sys.argv[-1], 'topic')
