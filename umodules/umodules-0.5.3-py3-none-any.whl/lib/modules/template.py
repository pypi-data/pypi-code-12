from umodules.lib.module import IModule


class Template(IModule):

    def __init__(self):
        self.name = 'template'

    def install(self, project):
        super().install(project)

    def init(self):
        super().init()
