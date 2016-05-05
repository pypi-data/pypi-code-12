from setuptools import setup


def get_requirements(path):
    with open(path) as f:
        return f.readlines()

install_requires = get_requirements('requirements.txt')

version = '0.1'

setup(
    name='rssmailer',
    version=version,
    description="RSS Digest Emailer",
    author='Arun S',
    author_email='arun@indeliblestamp.com',
    url='https://tools.indeliblestamp.com',
    license='GPL',
    install_requires=install_requires,
    scripts=['rssmailer/rss_mailer.py'],
    packages=['rssmailer'],
    package_data={
        'sample': ['rssmailer/rssemailer.json.sample'],
        'reqs': ['requirements.txt'],
     },
)
#    include_package_data=True,
#    zip_safe=False,
