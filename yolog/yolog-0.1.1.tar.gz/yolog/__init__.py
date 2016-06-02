__author__ = "Karan Desai"
__email__ = "karandesai281196@gmail.com"
__version__ = "0.1.1"
__license__ = "MIT"


from generate import YologGenerator


def configure():
    yolog_gen = YologGenerator()
    yolog_gen.set_gitconfig_alias()
