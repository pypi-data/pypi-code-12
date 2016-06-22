################################################################
# xmldirector.dita
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import plac
import shutil
import tempfile
import pkg_resources
import lxml.etree
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
    converter=('Converter to be used (saxon or lxml', 'option', 'c', str),
    infotype=("DITA type (topic, concept, reference, task)", "option", 'f', str))
def html2dita(html_filename, infotype='topic', output_filename=None, converter='saxon'):

    if converter not in ('saxon', 'lxml'):
        raise ValueError('Unsupported converter (use "lxml" or "saxon")')

    if not infotype in info_types:
        raise ValueError('Unsupported infotype "{}"'.format(infotype))

    if not output_filename:
        output_filename = tempfile.mktemp(suffix='.dita')

    if not html_filename:
        raise ValueError('No HTML input filename given')

    if not os.path.exists(html_filename):
        raise ValueError('No HTML input filename {} does not exist'.format(html_filename))

    if converter == 'saxon':
        return html2dita_saxon(html_filename, infotype, output_filename)
    elif converter == 'lxml':
        return html2dita_lxml(html_filename, infotype, output_filename)


def html2dita_lxml(html_filename, infotype='topic', output_filename=None):

    with open(h2d_xsl, 'rb') as fp:
        xslt_root = lxml.etree.XML(fp.read())
        transform = lxml.etree.XSLT(xslt_root)

    with open(html_filename, 'rb') as fp:
        html_out, errors = tidylib.tidy_document(
        fp.read(),
        options={
            'doctype': 'omit',
            'output_xhtml': 1,
            })
        html_out = html_out.replace(b' xmlns="http://www.w3.org/1999/xhtml"', b'')

    root = lxml.etree.fromstring(html_out)
    transform_result= transform(root)
    if transform.error_log:
        raise RuntimeError('XSLT transformation failed: {}'.format(transform.error_log))

    with open(output_filename, 'wb') as fp:
        fp.write(lxml.etree.tostring(transform_result, pretty_print=True))
    return output_filename


def html2dita_saxon(html_filename, infotype='topic', output_filename=None):

    with open(html_filename, 'rb') as fp:
        html_out, errors = tidylib.tidy_document(
        fp.read(),
        options={
            'doctype': 'omit',
            'output_xhtml': 1,
            })
        html_out = html_out.replace(b' xmlns="http://www.w3.org/1999/xhtml"', b'')

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
    os.unlink(html_tmp)
    if status != 0:
        raise RuntimeError('html2dita() failed: {}'.format(output))
    return output_filename


def main():
    import plac; plac.call(html2dita)


if __name__ == '__main__':
    main()
