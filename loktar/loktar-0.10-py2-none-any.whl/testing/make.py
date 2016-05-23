from loktar.cmd import exe
from loktar.testing.plugin import ComplexPlugin


class Make(ComplexPlugin):
        def __init__(self, package_info):
            ComplexPlugin.__init__(self, package_info,
                                   {
                                       "command": {
                                           "run": "make ci",
                                           "clean": "make clean"
                                       }
                                   })
            self.timeline = {
                60: self.get_results,
            }

        def run(self):
            self._run(self.timeline)

        def get_results(self):
            print 'ToDo'

