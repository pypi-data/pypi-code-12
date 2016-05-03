__author__ = 'dcortes'

from setuptools import setup

setup(name='dexcell_api_v3',
      version='0.3.6',
      packages=['dexma_api_v3',
                'dexma_api_v3.repositories',
                'dexma_api_v3.factory',
                'dexma_api_v3.factory.custom_types',
                'dexma_api_v3.factory.readings_factory',
                'dexma_api_v3.factory.location_factory',
                'dexma_api_v3.factory.location_factory.location_info_factory',
                'dexma_api_v3.factory.cost_electrical_factory',
                'dexma_api_v3.factory.cost_electrical_factory.consumption',
                'dexma_api_v3.factory.cost_electrical_factory.demand',
                'dexma_api_v3.factory.cost_electrical_factory.periods',
                'dexma_api_v3.factory.cost_electrical_factory.price_change',
                'dexma_api_v3.factory.cost_electrical_factory.values',
                'dexma_api_v3.factory.utilities',
                'dexma_api_v3.factory.bases',
                'dexma_api_v3.gateway'],
      install_requires=[
          'arrow==0.7.0',
          'schematics',
          'dexma_drivers==0.1.8'
      ],
      description="DEXCell Energy Manager HTTP/JSON REST API v3 for python",
      author='David Cortes',
      author_email="dcortes@dexmatetch.com",
      url="https://bitbucket.org/dexmatech/dexcell_api_v3/",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3'
                     ],
      license="BSD"
      )
