# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from async_tasks.utils import consume_task_queue
import time


class Command(BaseCommand):

    def handle(self, *args, **options):

        timeout = 60
        end_time = time.time() + timeout
        while end_time > time.time():

            consume_task_queue()
            time.sleep(1)