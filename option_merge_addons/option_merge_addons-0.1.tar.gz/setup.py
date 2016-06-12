from setuptools import setup, find_packages

setup(
      name = "option_merge_addons"
    , version = "0.1"
    , py_modules = ["option_merge_addons"]

    , install_requires =
      [ 'six'
      , "layerz==0.5"
      , "delfick_error>=1.7"
      , "input_algorithms>=0.5"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.4.9"
        , "nose"
        , "mock"
        ]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/option_merge_addons"
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "Addons for option_merge"
    , license = "WTFPL"
    )
