from distutils.core import setup

setup(
    name='bbgateway',
    version='0.0.3',
    description="Python 3 package for Bankcard Brokers Payment Gateway integration.",

    author="Alejandro Otero Ortiz de Cosca",
    author_email="otero.alx@gmail.com",
    url="https://github.com/lexotero/bbgateway.git",

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords="gateway bankcard brokers integration",
    packages=['bbgateway'],
)
