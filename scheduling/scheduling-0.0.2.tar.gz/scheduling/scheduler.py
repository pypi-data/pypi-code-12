#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Authors:
#   Alex Vinyals <alevinval@gmail.com> - 2015
#
from scheduling import graph


class Scheduler:
    """
    Manager capable of running an schedule of
    tasks respecting the relatives and granting
    the correctness of the execution order.
    """

    def __init__(self, task):
        """ Accepts a main ( global ) task, explores
        subtasks linked to that task and checks for
        correctness of the schedule.
        :param task: Task
        """
        self.main_task = task
        self.nodes = graph.explore(self.main_task.node)
        graph.reset_visits(self.nodes)
        graph.detect_cycles(self.nodes)
        self.tasks = [node.task for node in self.nodes]

        self.execution_order = []
        for t in self.tasks:
            t.thread.setDaemon(True)
            t.scheduler = self

    def notify_execution(self, task):
        """
        Called by an Task to notify the his execution finished.
        :param task: Task
        """
        self.execution_order.append(task)

    def run(self):
        """
        Run the schedule
        """
        self.main_task.thread.start()
        self.main_task.thread.join()
