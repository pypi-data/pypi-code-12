from intmaniac.output.base import GenericOutput

import importlib


output = None


def init_output(otype):
    global output
    module_name = "intmaniac.output.%s" % otype
    i = importlib.import_module(module_name)
    output = i.get()


if True:
    # "if True" kills the "overwrite without use" warning in pycharm
    output = GenericOutput()


if __name__ == "__main__":
    print("Don't do this :)")
