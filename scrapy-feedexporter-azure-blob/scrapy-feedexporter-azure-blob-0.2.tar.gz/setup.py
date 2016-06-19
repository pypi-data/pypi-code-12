from setuptools import setup, find_packages


setup(
    name='scrapy-feedexporter-azure-blob',
    version='0.2',
    url='https://github.com/undernewmanagement/scrapy-feedexporter-azure-blob',
    description=(
        'Scrapy extension Feed Exporter Storage Backend to export items to a '
        'Azure blob container'
    ),
    long_description=open('README.rst').read(),
    author='Mark Anderson',
    author_email='mark@m3b.net',
    license='MIT',
    packages=['scrapy_feedexporter_azure_blob'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
#        'Programming Language :: Python :: 3',
#        'Programming Language :: Python :: 3.4',
#        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Framework :: Scrapy',
    ],
    install_requires=['azure-storage'],
)
