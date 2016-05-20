

"""
Factory for quick constructing classes with attributes and checks

see also wayround_org.utils.lxml.checker_factory()
"""

import wayround_org.utils.types


def class_generate_attributes(class_obj, attributes):
    """
    Installs get_* and set_* functions to set or get _* values

    _* values are reset to None

    Generated methods can make use of format_* functions of same instance

    there are two cases for attributes:
    1. list of strings: names of attributes to create;
    2. list of 2-tuples:
        [0] - same as in first case;
        [1] - signal name to call on successful set operation.
    """

    case = None

    if wayround_org.utils.types.struct_check(
            attributes,
            {'t': list, '.': {'t': str}}
            ):
        case = 0

    if wayround_org.utils.types.struct_check(
            attributes,
            {'t': list, '.': {'t': tuple, '<': 2, '>': 2, '.': {'t': str}}}
            ):
        case = 1

    if case is None:
        raise ValueError(
            "`attributes' must be list of strings or list of tuple of strings"
            )

    for i in attributes:

        if isinstance(i, str):
            i = (i,)

        signal_emiter = ''

        if case == 1:
            signal_emiter = \
                "self.signal.emit('{signal_name}', self)".format(
                    signal_name=i[1]
                    )

        exec("""\
def set_{name}(self, value):
    \"""
    Assign value to self._{name} checking it with self.check_{name}() and
    formatting it with self.format_{name}() if it's exists
    \"""
    self.check_{name}(value)
    if hasattr(self, 'format_{name}') and callable(self.format_{name}):
        value = self.format_{name}(value)
    self._{name} = value

    {signal_emiter}

def get_{name}(self):
    \"""
    Retrieve value from self._{name} checking it with self.check_{name}()
    \"""
    ret = self._{name}
    self.check_{name}(ret)
    if hasattr(self, 'format_{name}') and callable(self.format_{name}):
        ret = self.format_{name}(ret)
    return ret

class_obj._{name} = None
class_obj.set_{name} = set_{name}
class_obj.get_{name} = get_{name}

del set_{name}
del get_{name}

""".format(name=i[0], signal_emiter=signal_emiter))

    return


def class_generate_check(class_obj, attributes):
    """
    Installs check function check(self, inst=None)

    New function checks each value in instance by getting them with get_*
    functions.

    New function can make use of logical_structure_check function to check
    instance sanity
    """

    if not wayround_org.utils.types.struct_check(
            attributes,
            {'t': list, '.': {'t': str}}
            ):
        raise ValueError("`attributes' must be list of strings")

    central_check = """\
def check(self, inst=None):
    if inst != None and type(self) != type(inst):
        raise ValueError("`inst' must be of same type as self")

    if inst == None:
        inst = self

"""

    for i in attributes:
        central_check += '    inst.get_{name}()\n'.format(name=i)

    central_check += """\
    if hasattr(self, 'logical_structure_check') and callable(self.logical_structure_check):
        inst.logical_structure_check()

"""

    exec("""\
{}

class_obj.check = check

del check
""".format(central_check))

    return


def class_generate_attributes_and_check(class_obj, attributes):
    class_generate_attributes(class_obj, attributes)
    class_generate_check(class_obj, attributes)
    return
