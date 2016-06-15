from setuptools import setup, find_packages
from komodo import VERSION

setup(
      name = "komodo"
    , version = VERSION
    , packages = find_packages(exclude=['tests'])
    , package_data =
      { 'komodo.widgets': [ 'bundles/*.js' ]
      , 'komodo.server':
        [ 'templates/*.html'
        , 'static/*.js'
        ]
      }

    , install_requires =
      [ "six"
      , "croniter"
      , "requests"
      , "slumber"
      , "input_algorithms==0.4.5.4"
      , "delfick_app==0.7.3"
      , "option-merge==0.9.9.4"

      , "Flask==0.10.1"
      , "tornado==4.3"
      , "pyYaml==3.10"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.5.0"
        , "nose"
        , "mock==1.0.1"
        , "tox"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'komodo = komodo.executor:main'
        ]
      }

    # metadata for upload to PyPI
    , url = "https://github.com/mic159/komodo"
    , author = "Michael Cooper"
    , author_email = "mic159@gmail.com"
    , description = "Application that reads yaml and serves up a pretty dashboard"
    , license = "MIT"
    , keywords = "dashboard"
    )

