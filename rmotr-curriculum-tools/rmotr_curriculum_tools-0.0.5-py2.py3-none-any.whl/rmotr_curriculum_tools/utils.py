import re
import uuid as uuid_module
import pytoml as toml
from bs4 import BeautifulSoup

from .exceptions import InvalidUnitNameException

try:
    unicode_type = unicode
except NameError:
    unicode_type = str

AVOID_COUNT_TAGS = ['code', 'pre']

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    result = []
    for word in _punct_re.split(text.lower()):
        result.append(word)
    return unicode_type(delim.join(result))


def generate_unit_dot_rmotr_file(name, uuid=None):
    return toml.dumps({
        'uuid': str(uuid or uuid_module.uuid4()),
        'name': name
    })


def generate_lesson_dot_rmotr_file(name, _type, uuid=None):
    return toml.dumps({
        'uuid': str(uuid or uuid_module.uuid4()),
        'name': name,
        'type': _type
    })


def get_order_from_numbered_object_directory_name(dir_name):
    try:
        return int(dir_name.split('-')[1])
    except ValueError:
        raise InvalidUnitNameException(
            '{} is not a valid numbered name'.format(dir_name))


def _generate_directory_name(name, order, _type, include_human_name=True):
    return '{type}-{order}{human_name}'.format(
        type=_type,
        order=order,
        human_name=(
            (include_human_name or '') and ('-' + slugify(name))
        )
    )


def generate_model_object_directory_name(name, order, _type,
                                         include_human_name=True):
    return _generate_directory_name(
        name, order, _type, include_human_name)


def generate_lesson_directory_name(name, order, include_human_name=True):
    return _generate_directory_name(name, order, 'lesson', include_human_name)


def generate_unit_directory_name(name, order, include_human_name=True):
    return _generate_directory_name(name, order, 'unit', include_human_name)


def count_words(markdown_content):
    count = 0
    for tag in BeautifulSoup(markdown_content, "html.parser").find_all():
        if tag.name not in AVOID_COUNT_TAGS:
            count += len([w for w in tag.text.split(" ") if w])
    return count
