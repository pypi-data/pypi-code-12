from distutils.core import setup

f = open("README.rst")
try:
    try:
        readme = f.read()
    except:
        readme = ""
finally:
    f.close()

setup(
    name='bottoku',
    version='0.1.3',
    packages=['bottoku', 'bottoku.api.line', 'bottoku.api.slack', 'bottoku.api.facebook',
              'bottoku.renderer', 'bottoku.repository'],
    url='https://github.com/yamitzky/bottoku',
    license='The MIT License (MIT)',
    author='Mitsuki Ogasahara',
    author_email='negiga@gmail.com',
    description='Microframework for Chat/Messenger Bots',
    long_description=readme,
    install_requires=[
        'requests>=2.9.1',
        'simplejson>=3.8.2'
    ],
    extras_require={
        'test': ['pytest']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
