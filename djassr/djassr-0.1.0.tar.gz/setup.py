from setuptools import find_packages, setup

setup(
    name="djassr",
    version=__import__('djassr').__version__,
    author="Alexandre Varas",
    author_email="alej0varas@gmail.com",
    license='GNU Library or Lesser General Public License (LGPL)',
    description="Django AWS S3 Signed Requests API with Django Rest Framework",
    url='https://github.com/alej0varas/djassr',
    packages=('djassr', ),
    install_requires=['s3sign==0.1.1'],
    tests_require=['s3sign==0.1.1', 'django==1.9.7', 'djangorestframework==3.3.3'],
    test_suite='runtests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
