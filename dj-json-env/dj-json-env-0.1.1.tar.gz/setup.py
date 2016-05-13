from setuptools import setup

setup(
    name='dj-json-env',
    version='0.1.1',
    url='https://github.com/vijayendra/dj-json-env',
    license='MIT',
    author='Vijayendra Bapte',
    author_email='vijayendra.bapte@gmail.com',
    description='Use env to read local settings for django app',
    py_modules=['dj_json_env'],
    scripts=["scripts/export_json"],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
