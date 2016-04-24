from baelfire.dependencies import AlwaysRebuild
from baelfire.dependencies import LinkTask
from baelfire.dependencies import NeverRebuild
from baelfire.dependencies import TaskDependency
from baelfire.task import Task
from pprint import pprint


class First(Task):

    def create_dependecies(self):
        self.add_dependency(NeverRebuild())

    def make(self):
        print('v', self.name)


class Second(Task):

    def create_dependecies(self):
        self.add_dependency(AlwaysRebuild())

    def make(self):
        print('v', self.name)

    def validate_dependecies(self):
        return super().validate_dependecies()


class Third(Task):

    def create_dependecies(self):
        self.add_dependency(TaskDependency(First()))

    def make(self):
        print(self.name)


class Four(Third):

    def create_dependecies(self):
        super().create_dependecies()
        self.add_dependency(TaskDependency(Second()))


class Five(Third):

    def create_dependecies(self):
        super().create_dependecies()
        self.add_dependency(LinkTask(Second()))

print('--- First')
First().run()
Second().run()

print('--- Second')
Third().run()

print('--- Third')
Four().run()

print('--- Four')
five = Five()
five.run()

pprint(five.datalog)
