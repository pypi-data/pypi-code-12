from setuptools import setup

setup(
        name='worklogmd',
        version=0.2,
        author='Samuel Taylor',
        url='https://github.com/ssaamm/worklog.md',
        description='Text-based work habit tracker',
        license='MIT',
        packages=['worklog'],
        install_requires=['antlr4-python3-runtime'],
        entry_points={
            'console_scripts': ['processWorklog = worklog.process:run'],
        },
)
