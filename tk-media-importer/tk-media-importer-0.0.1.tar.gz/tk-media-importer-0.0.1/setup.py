from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='tk-media-importer',
    version='0.0.1',
    description='',
    long_description=readme(),
    url='http://github.com/tomreitsma/tk_media_importer',
    author='Tom Reitsma',
    author_email='reitsma.tom@gmail.com',
    license='MIT',
    packages=['tk_media_importer'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)
