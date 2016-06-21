################################################################
# xmldirector.dita
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import plac
import shutil
import tempfile
import pkg_resources
import tidylib

from xmldirector.dita import util


for name in ('saxon9', 'saxon8', 'saxon7', 'saxon'):
    saxon = shutil.which(name)
    if saxon:
        break

h2d_xsl = pkg_resources.resource_filename('xmldirector.dita.converters.h2d', 'h2d.xsl')
info_types = ('topic', 'concept', 'reference', 'task')


@plac.annotations(
    html_filename=("Input HTML filename", 'option', 'i', str),
    output_filename=("Output DITA filename", 'option', 'o', str),
    infotype=("DITA type (topic, concept, reference, task)", "option", 'f', str))
def html2dita(html_filename, infotype='topic', output_filename=None):

    if not infotype in info_types:
        raise ValueError('Unsupported infotype "{}"'.format(infotype))

    if not output_filename:
        output_filename = tempfile.mktemp(suffix='.dita')

    if not html_filename:
        raise ValueError('No HTML input filename given')

    if not os.path.exists(html_filename):
        raise ValueError('No HTML input filename {} does not exist'.format(html_filename))

    with open(html_filename, 'rb') as fp:
        html_out, errors = tidylib.tidy_document(
        fp.read(),
        options={
            'doctype': 'omit',
            'output_xhtml': 1,
            })

    html_tmp = tempfile.mktemp(suffix='.html')
    with open(html_tmp, 'wb') as fp:
        fp.write(html_out)

    cmd = '"{saxon}" "{html_filename}" "{h2d_xsl}" infotype={infotype} >"{output_filename}"'.format(
            saxon=saxon,
            html_filename=html_tmp,
            h2d_xsl=h2d_xsl,
            infotype=infotype,
            output_filename=output_filename)

    status, output = util.runcmd(cmd)
    if status != 0:
        raise RuntimeError('html2dita() failed: {}'.format(output))
    return output_filename


def main():
    import plac; plac.call(html2dita)


if __name__ == '__main__':
    main()
