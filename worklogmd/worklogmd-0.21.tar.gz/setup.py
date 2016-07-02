from setuptools import setup

setup(
        name='worklogmd',
        version=0.21,
        author='Samuel Taylor',
        url='https://github.com/ssaamm/worklog.md',
        description='Text-based work habit tracker',
        license='MIT',
        packages=['worklog', 'worklog.parsing'],
        install_requires=['antlr4-python3-runtime'],
        entry_points={
            'console_scripts': ['processWorklog = worklog.process:run'],
        },
)
