from setuptools import setup, find_packages


setup(
    name='frasco-api',
    version='0.5',
    url='http://github.com/frascoweb/frasco-api',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Create APIs and service based applications with Frasco",
    py_modules=['frasco_api'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco-models>=0.4',
        'frasco-users',
        'apispec',
        'flask-cors'
    ]
)
