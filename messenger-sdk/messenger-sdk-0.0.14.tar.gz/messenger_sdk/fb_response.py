class FbResponse:
    def __init__(self, template=None):
        self._templates = list()
        if template:
            self.add_template(template)

    def add_template(self, template):
        self._templates.append(template)

    @property
    def templates(self):
        return self._templates
