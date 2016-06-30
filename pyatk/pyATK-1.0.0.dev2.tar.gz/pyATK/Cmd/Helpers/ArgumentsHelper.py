
class ArgumentsHelper:
    def __init__(self, input_):
        self.input = input_

    @classmethod
    def arguments(cls):
        pass

    def getOptionCouples(self):
        result = []
        for opt in self.input.options:
            result.append(["-" + opt.shortForm, "--" + opt.longForm])
        return result

    def option(self, name):
        while name[0] == '-':
            name = name[1:]

        for option in self.input.options:
            if name in [option.shortForm, option.longForm]:
                return option
        raise Exception("Option " + name + " was not found")

    def argument(self, name):
        for argument in self.input.arguments:
            if name in argument.name:
                return argument
        raise Exception("Argument " + name + " was not found")

