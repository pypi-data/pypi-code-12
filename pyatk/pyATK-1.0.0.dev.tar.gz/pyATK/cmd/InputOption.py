from pyATK.utils.misc import if_else


class InputOption:
    OPTION_REQUIRED = 0x0
    OPTION_OPTIONAL = 0x1
    OPTION_NONE = 0x2
    OFFSET = 35
    MAX_LENGTH_PER_LINE = 80

    def __init__(self, short_form, long_form=None, description=None, value_required=None):
        self.shortForm = short_form
        self.longForm = long_form
        self.description = description
        self.valueRequired = value_required
        self.value = None

    def __str__(self):
        ret_string = "-" + self.shortForm + if_else(self.longForm is not None, ", --" + self.longForm, "")
        if self.valueRequired == InputOption.OPTION_REQUIRED:
            ret_string += "=<VALUE>"
        elif self.valueRequired == InputOption.OPTION_OPTIONAL:
            ret_string += "=[VALUE]"
        else:
            pass

        ret_string = ret_string.ljust(InputOption.OFFSET)
        if self.description is not None:
            if len(self.description) > InputOption.MAX_LENGTH_PER_LINE:
                ret_string += self.description[:InputOption.MAX_LENGTH_PER_LINE] + "\n"
                ret_string += self.description[InputOption.MAX_LENGTH_PER_LINE:].rjust(InputOption.OFFSET +
                                                                                       len(self.description) -
                                                                                       InputOption.MAX_LENGTH_PER_LINE)
            else:
                ret_string += self.description

        return ret_string

    def __repr__(self):
        return self.__str__()
