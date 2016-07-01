from setuptools import setup, find_packages


def description():
    return """
    """

setup(
    name="todo_app",
    version="0.0.1",
    author="Felipe Volpone",
    author_email="felipevolpone@gmail.com",
    description=description(),
    license="MIT",
    keywords="python todo list cli todoapp",
    url="http://github.com/felipevolpone/cli_todo",
    packages=find_packages(exclude=['tests']),
    install_requires=['click'],
    long_description="Check on github: http://github.com/felipevolpone/cli_todo",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points='''
        [console_scripts]
        todo=todo.commandline:interface
    '''
)
