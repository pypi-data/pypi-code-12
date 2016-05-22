from setuptools import setup

setup(
    name='lektor-feed',
    version='0.1',
    author=u'Detlef Kreuz',
    author_email='mail-python.org@yodod.de',
    license='MIT',
    py_modules=['lektor_feed'],
    install_requires=['MarkupSafe', 'Lektor'],
    tests_require=['lxml', 'pytest'],
    url='https://yoyod.de/p/lektor-feed',
    entry_points={
        'lektor.plugins': [
            'feed = lektor_feed:FeedPlugin',
        ]
    }
)
