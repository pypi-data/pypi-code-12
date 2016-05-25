from setuptools import setup


setup(
    name="es-map-writer",
    version='1.0.0.a1',
    author='TJ Soptame',
    author_email='tj.soptame@gmail.com',
    description='A command line tool that writes an Elasticsearch index mapping for a PostgreSQL database table.',
    url='https://github.com/tuss4/es-map-writer',
    packages=['es_map_writer'],
    py_modules=['es_map_writer'],
    license='MIT',
    install_requires=[
        'click==6.6',
        'psycopg2==2.6.1',
    ],
    entry_points='''
        [console_scripts]
        mapwrtr=es_map_writer.command:cli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='python psycopg2 elasticsearch mapping'
)
