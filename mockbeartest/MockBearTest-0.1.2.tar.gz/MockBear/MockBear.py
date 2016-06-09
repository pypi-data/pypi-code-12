from coalib.bearlib.abstractions.Linter import linter
from coalib.bears.requirements.PythonRequirement import PythonRequirement


@linter(executable='cppclean',
        output_format='regex',
        output_regex=r'.+:(?P<line>\d+):(?P<message>.*)')
class MockBear:
    """
    Find problems in C++ source code that slow down development in large code
    bases. This includes finding unused code, among other features.

    Read more about available routines at
    <https://github.com/myint/cppclean#features>.
    """

    LANGUAGES = "C++"
    REQUIREMENTS = (PythonRequirement('cppclean', '0.9.*'),)

    @staticmethod
    def create_arguments(filename, file, config_file):
        return filename,
