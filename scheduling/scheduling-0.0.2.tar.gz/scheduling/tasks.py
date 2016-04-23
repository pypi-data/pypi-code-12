import abc
import itertools
import threading
import time

from scheduling import graph


class Task:
    """ Base object to create a task to be scheduled.
    """
    _ids = itertools.count(1)
    _polling_time = 0.01

    def __init__(self, name):
        self.node = graph.DependencyGraphNode(self)
        self.thread = threading.Thread(target=self._run)

        self.id = next(Task._ids)
        self.name = name
        self.scheduler = None
        self.launched = False
        self.has_started = False
        self.siblings_permission = False
        self.has_finished = False
        self.finished_at = None

    def __str__(self):
        return "Task {} [ {} ]".format(self.id, self.name)

    def __gt__(self, other):
        return self.id > other.id

    def __lt__(self, other):
        return self.id < other.id

    def wait_and_join(self, task):
        """ Given a task, waits for it until it finishes
        :param task: Task
        :return:
        """
        while not task.has_started:
            time.sleep(self._polling_time)
        task.thread.join()

    def depends(self, *tasks):
        """ Interfaces the GraphNode `depends` method """
        nodes = [x.node for x in tasks]
        self.node.depends(*nodes)
        return self

    def then(self, *tasks):
        """ Interfaces the GraphNode `then` method
        """
        nodes = [x.node for x in tasks]
        self.node.then(*nodes)
        return self

    def add(self, *tasks):
        """ Interfaces the GraphNode `add` method
        """
        nodes = [x.node for x in tasks]
        self.node.add(*nodes)
        return self

    def _run(self):
        """ Run the task respecting dependencies
        """
        for node in self.node.relatives:
            launch_node_task(node)
        for node in self.node.relatives:
            self.wait_and_join(node.task)
        if self.node.parent:
            while not self.node.parent.task.siblings_permission:
                time.sleep(self._polling_time)
        self.has_started = True
        self.main()
        self.siblings_permission = True
        for node in self.node.siblings:
            launch_node_task(node)
        for node in self.node.siblings:
            self.wait_and_join(node.task)
        self.finished_at = time.time()
        self.scheduler.notify_execution(self)
        self.has_finished = True

    @abc.abstractmethod
    def main(self):
        """ Main code for the task
        """
        print("running ", self.name)
        pass


def launch_node_task(node):
    if node.task.launched:
        return
    node.task.launched = True
    node.task.thread.start()
