from setuptools import setup, find_packages

setup(
    name='simplewebshell',
    version='0.0.3',
    description='simplewebshell',
    long_description='',
    url='http://github.com/krotkiewicz/simplewebshell',
    author='Konrad Rotkiewicz',
    author_email='konrad.rotkiewicz@gmail.com',
    license='MIT',
    py_modules=['simplewebshell'],
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'simplewebshell = simplewebshell:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
