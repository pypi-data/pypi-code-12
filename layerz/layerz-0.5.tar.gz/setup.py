from setuptools import setup

setup(
      name = "layerz"
    , version = "0.5"
    , py_modules = ['layerz']

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.4.9"
        , "nose"
        , "mock"
        , "delfick_error"
        ]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/layerz"
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "Module to create layers of dependencies"
    , license = "MIT"
    )
