
class TemplateError(Exception):
    """Exception raised during parsing of a template

    Attributes:
        line_number: line number of the error
        position: position of the error
        value: value when the error occured
    """

    def __init__(self, line_number, position, value, message=None):

        self.line_number = line_number
        self.position = position
        self.value = value

        if not message:
            if line_number != 0:
                error_mask = "Template error at line {ln}, position {p} at: {v}"
                message = error_mask.format(ln=line_number,
                                            p=position,
                                            v=value)
            else:
                message = "Unknown template error. Have you closed all open tags? e.g. {% endif %}"

        super(TemplateError, self).__init__(message)
