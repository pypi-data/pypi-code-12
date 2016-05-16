from pythonforandroid.toolchain import PythonRecipe

class DjangoRecipe(PythonRecipe):

    version = "1.9.6"
    url = "https://github.com/django/django/archive/{version}.tar.gz"
    depends = [("python2", "python3crystax")]

recipe = DjangoRecipe()
