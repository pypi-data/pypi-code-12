import logging

from pprint import pprint

from baelfire.application.commands.graph.graph import Graph
from baelfire.dependencies.dependency import AlwaysRebuild
from baelfire.dependencies.file import FileChanged
from baelfire.dependencies.file import FileDoesNotExists
from baelfire.dependencies.task import RunBefore
from baelfire.dependencies.task import TaskDependency
from baelfire.task import FileTask
from baelfire.task import Task
from baelfire.task.process import SubprocessTask
from baelfire.task.template import TemplateTask
from os import mkdir


class FirstTxt(FileTask):
    output_name = 'first'

    def phase_settings(self):
        super().phase_settings()
        self.paths[self.output_name] = 'first.txt'

    def build(self):
        print('build:', self.name)
        with open(self.output, 'w') as output:
            output.write(self.name)


class BaseDir(FileTask):
    output_name = 'base'

    def phase_settings(self):
        super().phase_settings()
        self.paths[self.output_name] = 'base'

    def build(self):
        print('build:', self.name)
        mkdir(self.output)


class SecondTxt(FileTask):
    output_name = 'second'

    def create_dependecies(self):
        super().create_dependecies()
        self.add_dependency(TaskDependency(BaseDir()))

    def phase_settings(self):
        super().phase_settings()
        self.paths.set_path(self.output_name, 'base', 'second.txt')

    def build(self):
        print('build:', self.name)
        with open(self.output, 'w') as output:
            output.write(self.name)


class ThirdTxt(FileTask):
    output_name = 'third'

    def create_dependecies(self):
        super().create_dependecies()
        self.add_dependency(TaskDependency(BaseDir()))
        self.add_dependency(FileChanged('source'))

    def phase_settings(self):
        super().phase_settings()
        self.paths.set_path(self.output_name, 'base', 'third.txt')
        self.paths['source'] = 'source.txt'

    def build(self):
        print('build:', self.name)
        with open(self.paths['source'], 'r') as source:
            with open(self.output, 'w') as output:
                for line in source:
                    output.write(line)


class Something(TemplateTask):
    source_name = 'source_template'
    output_name = 'output'

    def phase_settings(self):
        super().phase_settings()
        self.paths.set_path('source_template', 'templates', 'source.txt')
        self.paths.set_path('output', 'base', 'output.txt')


class Master(Task):

    def create_dependecies(self):
        self.add_dependency(TaskDependency(BaseDir()))
        self.add_dependency(TaskDependency(FirstTxt()))
        self.add_dependency(TaskDependency(SecondTxt()))
        self.add_dependency(RunBefore(ThirdTxt()))
        self.add_dependency(RunBefore(Something()))
        # self.add_dependency(AlwaysRebuild())

    def phase_settings(self):
        super().phase_settings()
        self.paths['base'] = 'buzu'
        self.paths.set_path('first', 'base', 'first.txt')
        self.settings['dude'] = 'the dude'
        self.paths['templates'] = 'temp'

    def build(self):
        # raise RuntimeError('xcd')
        pass

# FORMAT = ' * %(levelname)s %(name)s: %(message)s *'
# logging.basicConfig(level=logging.INFO, format=FORMAT)

# master = Master()
# try:
#     master.run()
# except:
#     pass
# pprint(master.datalog, width=150)
#     raise


class MySecondElo(SubprocessTask):

    def create_dependecies(self):
        self.add_dependency(AlwaysRebuild())
        pass

    def build(self):
        self.popen(['ls -al'])


class MyElo(SubprocessTask):

    def create_dependecies(self):
        self.add_dependency(FileDoesNotExists(raw_path='/tmp/elo'))
        self.add_dependency(TaskDependency(MySecondElo()))

    def build(self):
        # self.popen(['sleep 3'])
        pass
        with open('/tmp/elo', 'w'):
            pass

if __name__ == "__main__":
    task = MyElo()
    try:
        task.run()
    except:
        pprint(task.report, width=150)
        raise

    task.save_report()
    graph = Graph('.baelfire.report')
    graph.render()
