class Document(object):
    """
    Class representing stored NLP Documents
    """

    def __init__(self, id, pipeline, text, input_type, input_fields=None):
        self.id = id
        self.pipeline = pipeline
        self.text = text
        self.input_type = input_type
        self.input_fields = input_fields
