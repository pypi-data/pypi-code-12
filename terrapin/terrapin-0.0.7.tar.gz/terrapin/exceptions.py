
class TemplateError(Exception):
    """Exception raised during parsing of a template

    Attributes:
        line_number: line number of the error
        position: position of the error
        value: value when the error occured
    """

    def __init__(self, line_number, position, value, message=None):
        if not message:
            message = "Syntax Error"
        super(TemplateError, self).__init__(message)
        self.line_number = line_number
        self.position = position
        self.value = value
