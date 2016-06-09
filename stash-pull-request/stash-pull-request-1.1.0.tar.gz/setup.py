from setuptools import setup

setup(
    name='stash-pull-request',
    py_modules=['stashpr'],
    version='1.1.0',
    author='David Keijser',
    author_email='keijser@gmail.com',
    description='send pull request on stash',
    license='MIT',
    install_requires=[
        'autoauth',
        'requests>=1.1'
    ],
    entry_points={
        'console_scripts': [
            'pull-request = stashpr:main'
        ]
    }
)
