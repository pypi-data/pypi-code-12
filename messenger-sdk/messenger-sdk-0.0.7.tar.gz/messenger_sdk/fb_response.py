class FbResponse:
    def __init__(self, template):
        self._templates = list()
        self.add_template(template)

    def add_template(self, template):
        self._templates.append(template)

    @property
    def templates(self):
        return self._templates
