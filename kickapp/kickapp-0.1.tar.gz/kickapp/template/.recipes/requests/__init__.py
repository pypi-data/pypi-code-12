from pythonforandroid.toolchain import PythonRecipe

class RequestsRecipe(PythonRecipe):

    version = '2.10.0'
    url = 'https://github.com/kennethreitz/requests/archive/v{version}.tar.gz'
    depends = [("python2", "python3crystax")]

recipe = RequestsRecipe()
