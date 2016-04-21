from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='wilfred-say',
    version='3.0',
    keywords='wilfred quotes commandline',
    description='Print Wilfred quotes to the commandline',
    long_description=readme(),
    url='http://github.com/arecker/wilfred-say',
    author='Alex Recker',
    author_email='alex@reckerfamily.com',
    license='GPLv3',
    py_modules=['wilfred'],
    entry_points={'console_scripts': ['wilfred-say = wilfred:main']}
)
