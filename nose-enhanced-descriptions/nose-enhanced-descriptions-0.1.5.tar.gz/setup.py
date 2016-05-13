import setuptools

setuptools.setup(
    name="nose-enhanced-descriptions",
    version="0.1.5",
    url="https://github.com/paul-butcher/nose_enhanced_descriptions",

    author="Paul Butcher",
    author_email="paul.butcher@gmail.com",

    description="Improves nose test description output",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['nose'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License'

    ],
    entry_points={
        'nose.plugins.0.10': [
            'enhanced-descriptions=nose_enhanced_descriptions:EnhancedDescriptions'
        ]
    },
)
