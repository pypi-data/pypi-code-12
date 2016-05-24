from distutils.core import setup

setup(
    name = 'sapl',
    packages = ['sapl'],
    version = '1.0.1',
    description = 'Some tweets preprocessing for sentiment analysis.',
    author='Alex Pascault',
    author_email='alxndr.psclt@gmmail.com',
    license='MIT',
    url='http://sentiment-analysis-preprocessing-library.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
    
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
    
        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',
    
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    #packages=find_packages(),
    include_package_data = True,
    install_requires=['langdetect', 'unidecode']
)


