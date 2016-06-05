from distutils.core import setup


setup(
    name='twads',
    packages=['twads'],
    version='0.1.7',
    description='A wrapper for the Twitter Ads API',
    author='Jacob Gillespie',
    author_email='jdgillespie91@gmail.com',
    url='https://github.com/jdgillespie91/twads',
    install_requires=[
        'requests',
        'requests_oauthlib'
    ]
)
