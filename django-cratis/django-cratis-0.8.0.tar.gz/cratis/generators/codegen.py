import _ast
import ast
import os
import re
from _ast import AST


def dump_ast(node, annotate_fields=True, include_attributes=False, indent='  '):  # pragma: no cover
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, AST):
            fields = [(a, _format(b, level)) for a, b in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)


def indent_text(nr, text):
    inds = (' ' * nr)
    return inds + ('\n' + inds).join(text.splitlines())



def file_add_import(code, module, objects):
    """
    Add import to file.

    Finds last import in file by analyzing AST tree, and inserts new import after last one.

    :param filename:
    :param module:
    :param objects:
    :return:
    """

    source = ast.parse(code)
    objects = list(objects)

    last_import = 0
    for item in source.body:
        if isinstance(item, (_ast.Import, _ast.ImportFrom)):
            last_import = item.lineno

            if isinstance(item, _ast.ImportFrom):
                if item.module == module:
                    for alias in item.names:
                        if alias.name in objects and alias.asname is None:
                            objects.remove(alias.name)

    # everything imported - skipping
    if not objects:
        return code

    new_lines = ('from %s import %s' % (module, ', '.join(objects)),)

    code = insert_lines_to_code(code, last_import, new_lines)

    return code


def insert_lines_to_code(code, at_line, new_lines):
    """
    Insert set of lines into file at desired position

    :param code:
    :param at_line:
    :param new_lines:
    :return:
    """
    lines = code.splitlines()
    code = '\n'.join(tuple(lines[:at_line]) + new_lines + tuple(lines[at_line:]))
    return code


def settings_add_feature(code, package, feature, default_code=None):
    """
    Register a new feature in settings file.

    Anylyze AST tree to find FEATURE = () construction, and use regexp to carefully
    insert new feature, saving original indentation level.

    :param filename:
    :param feature:
    :return:
    """


    if default_code:
        feature_code = indent_text(4, '%s,' % default_code.strip())
    else:
        feature_code = indent_text(4, '%s(),' % feature)

    code = file_add_import(code, package, (feature,))

    source = ast.parse(code)
    for item in source.body:
        if isinstance(item, _ast.ClassDef) and item.name == 'Dev':

            for subitem in item.body:
                if isinstance(subitem, _ast.Assign) \
                        and isinstance(subitem.targets[0], _ast.Name) \
                        and subitem.targets[0].id == 'FEATURES':

                    # Skip Feature registration if it is already added
                    for val in subitem.value.elts:
                        if isinstance(val, _ast.Call) and val.func.id == feature:
                            return code

                    indent = subitem.targets[0].col_offset
                    line = subitem.targets[0].lineno - 1

                    lines = code.splitlines()

                    start = '\n'.join(lines[:line])
                    end = '\n'.join(lines[line:])

                    end = re.sub('^\s+FEATURES\s*=\s*\(',
                                 '\g<0>\n' + indent_text(indent, feature_code),
                                 end, flags=re.MULTILINE)

                    code = start + '\n' + end

                    return code

            # Seems to be there is no FEATURES = () ... add it!

            new_lines = tuple(indent_text(item.col_offset + 4, """FEATURES = (
%s
)
""" % feature_code).splitlines())

            code = insert_lines_to_code(code, item.lineno, new_lines)

            return code

    print('Nothing added -dev class not found')
    return code



def package_to_path(package_name):
    """
    Convert package name to relative directory name

    :param package_name:
    :return:
    """
    return package_name.replace('.', os.path.sep)

def generate_package(package_name, path=None):
    if not path:
        path = os.getcwd()

    if not isinstance(package_name, list):
        parts = package_name.split('.')
    else:
        parts = package_name

    if len(parts) < 2:
        return

    dirname = os.path.join(path, parts[0])

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    if not os.path.exists(os.path.join(dirname, '__init__.py')):
        with open(os.path.join(dirname, '__init__.py'), 'w+') as f:
            f.write('\n\n')

    if len(parts) > 1:
        generate_package(parts[1:], dirname)