from __future__ import unicode_literals

from pathlib import Path
import pytoml as toml

from .models import *
from . import utils
from . import exceptions

UNIT_GLOB = 'unit-*'
LESSON_GLOB = 'lesson-*'
DOT_RMOTR_FILE_NAME = '.rmotr'
README_FILE_NAME = 'README.md'
MAIN_PY_NAME = 'main.py'
TEST_PY_NAME = 'tests.py'
SOLUTIONS_DIR_NAME = 'solutions'

def read_dot_rmotr_file(path):
    dot_rmotr_path = path / DOT_RMOTR_FILE_NAME
    with dot_rmotr_path.open('r') as fp:
        dot_rmotr_content = toml.loads(fp.read())
    return dot_rmotr_content


def get_lesson_class_from_type(_type):
    if _type == READING:
        return ReadingLesson
    elif _type == ASSIGNMENT:
        return AssignmentLesson

    raise exceptions.InvalidLessonTypeException(
        '{} is not a valid lesson type'.format(_type))


def read_lesson(unit, lesson_path):
    order = utils.get_order_from_numbered_object_directory_name(
        lesson_path.name)
    dot_rmotr = read_dot_rmotr_file(lesson_path)

    LessonClass = get_lesson_class_from_type(dot_rmotr['type'])

    readme_path = lesson_path / README_FILE_NAME
    with readme_path.open(mode='r') as fp:
        readme_content = fp.read()

    lesson = LessonClass(
        unit=unit,
        directory_path=lesson_path,
        uuid=dot_rmotr['uuid'],
        name=dot_rmotr['name'],
        order=order,
        readme_path=readme_path,
        readme_content=readme_content
    )

    return lesson


def read_lessons(unit):
    lessons_glob = unit.directory_path.glob(LESSON_GLOB)
    return [read_lesson(unit, lesson_path) for lesson_path in lessons_glob]


def read_unit(course, unit_path):
    order = utils.get_order_from_numbered_object_directory_name(unit_path.name)
    dot_rmotr = read_dot_rmotr_file(unit_path)
    unit = Unit(
        course=course,
        directory_path=unit_path,
        uuid=dot_rmotr['uuid'],
        name=dot_rmotr['name'],
        order=order
    )
    unit._lessons = read_lessons(unit)
    return unit


def read_units(course):
    units_glob = course.directory_path.glob(UNIT_GLOB)
    return [read_unit(course, unit_path) for unit_path in units_glob]


def read_course_from_path(course_directory_path):
    if not isinstance(course_directory_path, Path):
        course_directory_path = Path(course_directory_path)

    dot_rmotr = read_dot_rmotr_file(course_directory_path)

    course = Course(
        directory_path=course_directory_path,
        uuid=dot_rmotr['uuid'],
        name=dot_rmotr['name'],
        track=dot_rmotr['track']
    )
    course._units = read_units(course)

    return course


def read_unit_from_path(unit_directory_path):

    unit_dot_rmotr = read_dot_rmotr_file(unit_directory_path)
    unit_uuid = unit_dot_rmotr['uuid']
    course = read_course_from_path(unit_directory_path.parent)
    for unit in course.iter_units():
        if unit.uuid == unit_uuid:
            return unit


def read_lesson_from_path(lesson_directory_path):
    unit = read_unit_from_path(lesson_directory_path.parent)

    dot_rmotr = read_dot_rmotr_file(lesson_directory_path)
    uuid = dot_rmotr['uuid']

    for lesson in unit.iter_lessons():
        if lesson.uuid == uuid:
            return lesson


def _create_assignment_files(lesson_directory_path):
    main_py_path = lesson_directory_path / MAIN_PY_NAME
    test_py_path = lesson_directory_path / TEST_PY_NAME
    solutions_path = lesson_directory_path / SOLUTIONS_DIR_NAME
    for file_path in [main_py_path, test_py_path]:
        with file_path.open(mode='w') as fp:
            fp.write('# empty')

    solutions_path.mkdir()

def create_unit(directory_path, name, order):
    unit_directory_path = (
        directory_path /
        utils.generate_unit_directory_name(name, order)
    )

    unit_directory_path.mkdir()
    dot_rmotr_path = unit_directory_path / DOT_RMOTR_FILE_NAME
    readme_path = unit_directory_path / README_FILE_NAME

    with dot_rmotr_path.open(mode='w') as fp:
        fp.write(utils.generate_unit_dot_rmotr_file(name=name))

    with readme_path.open(mode='w') as fp:
        fp.write('# {}\n'.format(name))

    return unit_directory_path


def create_lesson(directory_path, name, order, attrs):
    _type = attrs['type']

    lesson_directory_path = (
        directory_path /
        utils.generate_lesson_directory_name(name, order)
    )
    lesson_directory_path.mkdir()
    dot_rmotr_path = lesson_directory_path / DOT_RMOTR_FILE_NAME
    readme_path = lesson_directory_path / README_FILE_NAME

    with dot_rmotr_path.open(mode='w') as fp:
        fp.write(utils.generate_lesson_dot_rmotr_file(name=name, _type=_type))

    with readme_path.open(mode='w') as fp:
        fp.write('# {}\n'.format(name))

    if _type == ASSIGNMENT:
        _create_assignment_files(lesson_directory_path)

    return lesson_directory_path


def rename_child_object_incrementing_order(model_obj, _type):
    new_name = utils.generate_model_object_directory_name(
        model_obj.name, model_obj.order + 1, _type)
    model_obj.directory_path.rename(model_obj.parent.directory_path / new_name)
    return model_obj.directory_path


def rename_child_object_decrementing_order(model_obj, _type):
    new_name = utils.generate_model_object_directory_name(
        model_obj.name, model_obj.order - 1, _type)
    model_obj.directory_path.rename(model_obj.parent.directory_path / new_name)
    return model_obj.directory_path


def make_space_between_child_objects(model_obj, order):
    if isinstance(model_obj, Course):
        _type = 'unit'
    elif isinstance(model_obj, Unit):
        _type = 'lesson'
    else:
        raise AttributeError("Can't identify object %s" % model_obj)

    for child in model_obj.iter_children():
        if child.order >= order:
            rename_child_object_incrementing_order(child, _type)


def _rename_other_children_after_deleting_order(model_obj, order):
    if isinstance(model_obj, Course):
        _type = 'unit'
    elif isinstance(model_obj, Unit):
        _type = 'lesson'
    else:
        raise AttributeError("Can't identify object %s" % model_obj)

    for child in model_obj.iter_children():
        if child.order > order:
            rename_child_object_decrementing_order(child, _type)


def _add_object_to_parent(directory_path, name, creation_callback,
                          get_model_callback,
                          order=None,
                          creation_attributes=None):

    if not isinstance(directory_path, Path):
        directory_path = Path(directory_path)

    model_obj = get_model_callback(directory_path)
    last_object = model_obj.last_child_object
    last_object_order = (last_object and last_object.order) or 0

    if order is None:
        order = last_object_order + 1

    rename = (order <= last_object_order)
    if rename:
        make_space_between_child_objects(model_obj, order)

    creation_kwargs = {
        'directory_path': directory_path,
        'name': name,
        'order': order
    }
    if creation_attributes:
        creation_kwargs['attrs'] = creation_attributes

    return creation_callback(**creation_kwargs)


def add_unit_to_course(course_directory_path, name, order=None):
    return _add_object_to_parent(
        course_directory_path, name, create_unit,
        read_course_from_path, order)


def add_lesson_to_unit(unit_directory_path, name, _type, order=None):
    return _add_object_to_parent(
        unit_directory_path, name, create_lesson,
        read_unit_from_path,
        order, {'type': _type})


def _remove_child_from_directory(directory_path, get_model_callback):

    if not isinstance(directory_path, Path):
        directory_path = Path(directory_path)

    model_obj = get_model_callback(directory_path)
    parent = model_obj.parent

    last_object = parent.last_child_object
    if last_object.order != model_obj.order:
        _rename_other_children_after_deleting_order(parent, model_obj.order)

    import shutil
    shutil.rmtree(str(model_obj.directory_path.absolute()))


def remove_unit_from_directory(directory_path):
    return _remove_child_from_directory(directory_path, read_unit_from_path)


def remove_lesson_from_directory(directory_path):
    return _remove_child_from_directory(directory_path, read_lesson_from_path)
