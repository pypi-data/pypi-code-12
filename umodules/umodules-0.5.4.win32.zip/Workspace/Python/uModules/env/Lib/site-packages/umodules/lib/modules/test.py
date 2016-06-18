from umodules.lib.module import IModule


class TestModule(IModule):

    def __init__(self):
        self.name = 'test'

    def install(self, project):
        super().install(project)

    def activate(self):
        super().activate()

