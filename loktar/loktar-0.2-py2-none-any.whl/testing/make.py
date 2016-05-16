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
                90: self.clean_env
            }

        def run(self):
            self._run(self.timeline)

        def get_results(self):
            print 'ToDo'
            
        def clean_env(self):
            exe("make clean", remote=False)

if __name__ == "__main__":
    test = Make({"pkg_name": "connect"}, 'connect')
    test.run()
