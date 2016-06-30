#!/usr/bin/env python3
#   Copyright 2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

import pgtask_worker


class TestWorker(pgtask_worker.Worker):
    description = "Test worker"
    events = ['pgtask_row_changed in table public.t1']
    provide_database_connection = False

    def process_tasks(self, tasks):
        tasks.set_progress(0)

        logging.info('working...')

        tasks.set_progress(100)

        tasks.set_status('completed')

if __name__ == '__main__':
    TestWorker().run()
