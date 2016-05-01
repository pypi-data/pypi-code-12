import datetime
import json
import logging
import os
import re
import shutil
import string
import textwrap

import pypandoc
import pytz
from six import StringIO
from six.moves.urllib.parse import unquote_plus


ASSET_RE = re.compile(
    r'`(?P<display>[^<]+) <quiver\-file\-url/(?P<asset>[^>]+)>`__'
)
REFERENCE_RE = re.compile(r'\|image(?P<count>\d+)\|')
IMAGE_RE = re.compile(r'image:: quiver-image-url/(?P<path>.*)')


logger = logging.getLogger(__name__)


class Writer(StringIO):
    def writeline(self, data=u'', newline=True):
        if newline:
            data = data + u'\n'

        return super(Writer, self).write(data)


def format_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in name if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


def repair_incorrect_links(content):
    def generate_asset_url(match):
        data = match.groupdict()

        return ':download:`{name} <resources/{filename}>`'.format(
            name=data['display'],
            filename=unquote_plus(data['asset']),
        )

    def generate_image_url(match):
        data = match.groupdict()

        return 'image:: resources/{filename}'.format(
            filename=unquote_plus(data['path'])
        )

    # Convert asset references
    content = ASSET_RE.sub(generate_asset_url, content)

    # Convert image references
    content = IMAGE_RE.sub(generate_image_url, content)

    # Convert quiver-note-url/UUID entries
    # not implemented!

    return content


def repair_nonunique_references(content, reference_value):
    unacceptable_reference_numbers = []
    for match in sorted(list(set(REFERENCE_RE.findall(content)))):
        this_reference = int(match)
        if this_reference <= reference_value:
            unacceptable_reference_numbers.append(this_reference)
        elif this_reference > reference_value:
            reference_value = this_reference

    current = reference_value
    for reference_id in unacceptable_reference_numbers:
        current += 1
        content = content.replace(
            '|image{id}|'.format(id=reference_id),
            '|image{current}|'.format(current=current),
        )

    return content, current


def convert_text_cell(cell, output, reference_value, **kwargs):
    # Convert to RST
    converted, final_reference_value = repair_nonunique_references(
        pypandoc.convert(
            cell['data'],
            'rst',
            format='html',
        ),
        reference_value,
    )

    output.write(repair_incorrect_links(converted))

    return final_reference_value


def convert_markdown_cell(cell, output, reference_value, **kwargs):
    # Convert to RST
    converted, final_reference_value = repair_nonunique_references(
        pypandoc.convert(
            cell['data'],
            'rst',
            format='md',
        ),
        reference_value,
    )

    output.write(repair_incorrect_links(converted))

    return final_reference_value


def convert_code_cell(cell, output, **kwargs):
    output.writeline('.. code-block:: {lang}\n'.format(lang=cell['language']))
    lines = cell['data'].split('\n')
    for line in lines:
        output.writeline(' ' * 3 + line)


def convert_latex_cell(cell, output, **kwargs):
    output.writeline('.. math::\n')
    lines = cell['data'].split('\n')
    for line in lines:
        output.writeline(' ' * 3 + line)


def convert_diagram_cell(cell, output, **kwargs):
    logger.warning("Diagram cells are not fully-supported.")

    output.writeline('::\n')
    lines = cell['data'].split('\n')
    for line in lines:
        output.writeline(' ' * 3 + line)


def convert_note_into_rst(note_path, timezone):
    output = Writer()

    with open(os.path.join(note_path, 'content.json'), 'r') as inf:
        content = json.load(inf)
    with open(os.path.join(note_path, 'meta.json'), 'r') as inf:
        metadata = json.load(inf)

    output.writeline(
        ':created_at: ' +
        timezone.localize(
            datetime.datetime.fromtimestamp(metadata['created_at'])
        ).strftime('%Y-%m-%dT%H:%M:%S %Z')
    )
    output.writeline(
        ':updated_at: ' +
        timezone.localize(
            datetime.datetime.fromtimestamp(metadata['created_at'])
        ).strftime('%Y-%m-%dT%H:%M:%S %Z')
    )
    if metadata['tags']:
        output.writeline(':tags: ' + ', '.join(metadata['tags']))
    output.writeline(':quiver-uuid: ' + metadata['uuid'])
    output.writeline()
    output.writeline(content['title'])
    output.writeline('=' * len(content['title']))
    output.writeline()

    reference_value = 0
    for cell in content['cells']:
        new_reference_value = CONVERTERS[cell['type']](
            cell, output, reference_value=reference_value
        )
        if new_reference_value is not None:
            reference_value = new_reference_value
        output.writeline()

    return content['title'], output.getvalue()


def convert_quiver_repo_to_rst(quiver_path, output_path, timezone_name):
    zone = pytz.timezone(timezone_name)

    os.makedirs(output_path)
    resources_dir = os.path.join(output_path, 'resources')
    os.makedirs(resources_dir)

    with open(os.path.join(output_path, 'index.rst'), 'w') as out:
        out.write(
            textwrap.dedent("""\
                Converted Quiver Notes
                ======================

                .. toctree::
                   :glob:

                   **/index

            """)
        )

    with open(os.path.join(output_path, 'conf.py'), 'w') as out:
        out.write(
            textwrap.dedent("""\
                master_doc = 'index'
            """)
        )

    for notebook in os.listdir(quiver_path):
        notebook_dir = os.path.join(quiver_path, notebook)
        if not os.path.isdir(notebook_dir):
            continue

        logger.info("Opening notebook at %s", notebook_dir)

        with open(
            os.path.join(notebook_dir, 'meta.json'), 'r'
        ) as inf:
            notebook_data = json.load(inf)

        output_notebook_dir = os.path.join(
            output_path,
            format_filename(notebook_data['name']),
        )
        output_resources_dir = os.path.join(output_notebook_dir, 'resources')
        os.makedirs(output_resources_dir)

        logger.debug("Notebook output dir: %s", output_notebook_dir)

        with open(os.path.join(output_notebook_dir, 'index.rst'), 'w') as out:
            out.write(
                textwrap.dedent("""\
                    {title}
                    {underline}

                    .. toctree::
                       :glob:

                       *

                """.format(
                    title=notebook_data['name'],
                    underline='=' * len(notebook_data['name']),
                ))
            )

        for note in os.listdir(notebook_dir):
            if not os.path.isdir(os.path.join(notebook_dir, note)):
                continue
            logger.info("Opening note %s" % note)

            # Copy resources
            note_resources = os.path.join(notebook_dir, note, 'resources')
            if os.path.isdir(note_resources):
                for resource in os.listdir(note_resources):
                    shutil.copy(
                        os.path.join(note_resources, resource),
                        output_resources_dir,
                    )

            # Convert note
            title, data = convert_note_into_rst(
                os.path.join(notebook_dir, note),
                zone,
            )
            output_filename = os.path.join(
                output_notebook_dir,
                u'{filename}.rst'.format(
                    filename=format_filename(title),
                )
            )
            with open(output_filename, 'w') as out:
                out.write(data)

CONVERTERS = {
    'text': convert_text_cell,
    'markdown': convert_markdown_cell,
    'code': convert_code_cell,
    'latex': convert_latex_cell,
    'diagram': convert_diagram_cell,
}
