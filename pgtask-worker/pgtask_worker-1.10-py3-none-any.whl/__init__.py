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

import argparse
import collections
import configparser
import datetime
import logging
import os
import select
import signal
import sys

import psycopg2
import psycopg2.extras

try:
    from trivial_remote_semaphore.client import Client as TRSClient
except ImportError:
    TRSClient = None

STDERR_LOG_FORMAT = "%(asctime)s\t%(levelname)s\t%(message)s"
DB_LOG_FORMAT = "%(message)s"

VALID_DB_LEVEL_NAMES = ('ERROR', 'WARNING', 'INFO', 'DEBUG')

LIBRARY_FALLBACK_APPLICATION_NAME = "pgtask_worker {consumer_name} (library)"
FALLBACK_APPLICATION_NAME = "pgtask_worker {consumer_name}"

CONSUMER_STARTED_CHANNEL = "pgtask:consumer_{consumer_id}_started"
CONSUMER_TASK_CHANNEL = "pgtask:consumer_{consumer_id}_task"

REGISTER_CONSUMER_SQL = (
    "SELECT pgtask.register_consumer(%(consumer_name)s) AS consumer_id")
SET_CONSUMER_SUBSCRIPTIONS_SQL = (
    "SELECT pgtask.update_subscriptions(%(consumer_id)s, %(events)s)")
START_CONSUMER_SQL = "SELECT pgtask.start_consumer(%(consumer_id)s)"

GATHER_PENDING_TASKS_SQL = (
    "WITH processing_tasks AS (UPDATE pgtask.task SET status='processing' "
    "WHERE consumer_id=%(consumer_id)s AND status='pending' AND "
    "embargo <= statement_timestamp() "
    "RETURNING id, created, embargo, event, event_data) SELECT * FROM "
    "processing_tasks ORDER BY embargo ASC, created ASC")
GET_NEXT_TASK_INTERVAL_SQL = (
    "SELECT min(embargo)-statement_timestamp() AS embargo_interval FROM "
    "pgtask.task WHERE consumer_id=%(consumer_id)s AND status='pending'")

UPDATE_TASKSET_STATUS_SQL = (
    "UPDATE pgtask.task SET status=%(status)s WHERE id = ANY(%(ids)s)")
UPDATE_TASKSET_PROGRESS_SQL = (
    "UPDATE pgtask.task SET progress=%(progress)s WHERE id = ANY(%(ids)s)")
INSERT_TASK_LOG_MESSAGE_SQL = (
    "INSERT INTO pgtask.task_log (task_id, level, message) VALUES "
    "(%(task_id)s, %(level)s, %(message)s)")

REQUEUE_TASKSET_ABSOLUTE_EMBARGO_SQL = (
    "UPDATE pgtask.task SET status='pending', embargo=%(embargo)s WHERE "
    "id = ANY(%(ids)s)")
REQUEUE_TASKSET_RELATIVE_EMBARGO_SQL = (
    "UPDATE pgtask.task SET status='pending', "
    "embargo=statement_timestamp() + %(embargo)s WHERE id = ANY(%(ids)s)")

PUBLISH_EVENT_ABSOLUTE_EMBARGO_SQL = (
    "SELECT pgtask.publish_event(%(event)s, %(event_data)s, %(embargo)s)")
PUBLISH_EVENT_RELATIVE_EMBARGO_SQL = (
    "SELECT pgtask.publish_event(%(event)s, %(event_data)s, "
    "statement_timestamp() + %(embargo)s)")

PUBLISH_TASK_ABSOLUTE_EMBARGO_SQL = (
    "SELECT pgtask.publish_task(%(consumer_id)s, %(event)s, %(event_data)s, "
    "%(embargo)s)")
PUBLISH_TASK_RELATIVE_EMBARGO_SQL = (
    "SELECT pgtask.publish_task(%(consumer_id)s, %(event)s, %(event_data)s, "
    "statement_timestamp() + %(embargo)s)")


class Task:
    def __init__(self, worker, task_id, event, event_data):
        self._worker = worker

        self._task_id = task_id
        self.event = event
        self.event_data = event_data

    def __repr__(self):
        msg = "<Task task_id={task_id} event={event} event_data={event_data}>"
        return msg.format(
            task_id=self._task_id, event=self.event,
            event_data=self.event_data)

    def set_status(self, status):
        assert status in ('completed', 'failed')

        self._worker._worker_cursor.execute(
            UPDATE_TASKSET_STATUS_SQL,
            {'ids': [self._task_id], 'status': status})
        self._worker._worker_connection.commit()

    def set_progress(self, progress):
        assert 0 <= progress <= 100

        self._worker._worker_cursor.execute(
            UPDATE_TASKSET_PROGRESS_SQL,
            {'ids': [self._task_id], 'progress': progress})
        self._worker._worker_connection.commit()

    def log_message(self, level, message):
        self._worker._worker_cursor.execute(
            INSERT_TASK_LOG_MESSAGE_SQL,
            {'task_id': self._task_id, 'level': level, 'message': message})
        self._worker._worker_connection.commit()

    def log_error(self, message):
        return self.log_message('ERROR', message)

    def log_warning(self, message):
        return self.log_message('WARNING', message)

    def log_info(self, message):
        return self.log_message('INFO', message)

    def log_debug(self, message):
        return self.log_message('DEBUG', message)

    def requeue(self, embargo=None):
        if embargo is None:
            embargo = datetime.timedelta()

        if isinstance(embargo, datetime.timedelta):
            sql = REQUEUE_TASKSET_RELATIVE_EMBARGO_SQL
        else:
            sql = REQUEUE_TASKSET_ABSOLUTE_EMBARGO_SQL

        self._worker._worker_cursor.execute(
            sql, {'ids': [self._task_id], 'embargo': embargo})
        self._worker._worker_connection.commit()


class TaskSet(collections.UserList):
    def _get_worker(self):
        return self.data[0]._worker

    def _get_task_ids(self):
        task_ids = [task._task_id for task in self.data]
        return task_ids

    def for_event(self, event):
        matching_tasks = TaskSet()
        for task in self.data:
            if task.event == event:
                matching_tasks.append(task)

        return matching_tasks

    def set_status(self, status):
        assert status in ('completed', 'failed')

        # Empty
        if not self.data:
            return

        worker = self._get_worker()
        task_ids = self._get_task_ids()

        worker._worker_cursor.execute(
            UPDATE_TASKSET_STATUS_SQL,
            {'ids': task_ids, 'status': status})
        worker._worker_connection.commit()

    def set_progress(self, progress):
        assert 0 <= progress <= 100

        # Empty
        if not self.data:
            return

        worker = self._get_worker()
        task_ids = self._get_task_ids()

        worker._worker_cursor.execute(
            UPDATE_TASKSET_PROGRESS_SQL,
            {'ids': task_ids, 'progress': progress})
        worker._worker_connection.commit()

    def log_message(self, level, message):
        # Empty
        if not self.data:
            return

        worker = self._get_worker()
        task_ids = self._get_task_ids()

        for task_id in task_ids:
            worker._worker_cursor.execute(
                INSERT_TASK_LOG_MESSAGE_SQL,
                {'task_id': task_id, 'level': level, 'message': message})
        worker._worker_connection.commit()

    def log_error(self, message):
        return self.log_message('ERROR', message)

    def log_warning(self, message):
        return self.log_message('WARNING', message)

    def log_info(self, message):
        return self.log_message('INFO', message)

    def log_debug(self, message):
        return self.log_message('DEBUG', message)

    def requeue(self, embargo=None):
        # Empty
        if not self.data:
            return

        worker = self._get_worker()
        task_ids = self._get_task_ids()

        if embargo is None:
            embargo = datetime.timedelta()

        if isinstance(embargo, datetime.timedelta):
            sql = REQUEUE_TASKSET_RELATIVE_EMBARGO_SQL
        else:
            sql = REQUEUE_TASKSET_ABSOLUTE_EMBARGO_SQL

        worker._worker_cursor.execute(
            sql, {'ids': task_ids, 'embargo': embargo})
        worker._worker_connection.commit()


class Worker:
    description = "Nameless PgTask Worker"
    events = []
    provide_database_connection = True

    def run(self):
        self._parse_args_and_configure()
        self._prepare_semaphore()
        self._connect_database()
        self.prepare()
        self._process()

    def prepare(self):
        return

    def process_tasks(self, tasks):
        raise NotImplementedError()

    def _parse_args_and_configure(self):
        parser = argparse.ArgumentParser(
            description=self.__class__.description)

        parser.add_argument('config', help="Path to configuration file")
        parser.add_argument(
            '-v', '--verbose', action='store_true',
            help="include debug log entries")

        self._args = parser.parse_args()

        self.config = configparser.ConfigParser()
        with open(self._args.config) as config_file:
            self.config.read_file(config_file)

        stderr_log_handler = logging.StreamHandler()
        stderr_log_handler.setFormatter(logging.Formatter(STDERR_LOG_FORMAT))

        if self._args.verbose:
            stderr_log_handler.setLevel(logging.DEBUG)
        else:
            stderr_log_handler.setLevel(logging.INFO)

        self._db_log_handler = DatabaseLogHandler()
        self._db_log_handler.setFormatter(logging.Formatter(DB_LOG_FORMAT))
        self._db_log_handler.setLevel(logging.DEBUG)

        logging.basicConfig(
            level=logging.DEBUG,
            handlers=(stderr_log_handler, self._db_log_handler))

        self._consumer_name = self.config['pgtask']['consumer-name']

        self._running = True

        (self._wakeup_fd, wakeup_fd_w) = os.pipe2(os.O_NONBLOCK)
        signal.set_wakeup_fd(wakeup_fd_w)

        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        logging.info("Consumer {!r} initialising".format(self._consumer_name))

    def _prepare_semaphore(self):
        self._semaphore_client = None

        if 'remote-semaphore' not in self.config:
            return

        if TRSClient is None:
            msg = (
                "Remote Semaphore configuration found, but Trivial Remote "
                "Semaphore library not available")
            logging.error(msg)
            sys.exit(1)

        self._semaphore_client = TRSClient(
            self.config['remote-semaphore']['server'])

    def _acquire_semaphore(self, tasks):
        semaphore = self.config['remote-semaphore']['semaphore']
        secret = self.config['remote-semaphore']['secret']
        timeout = self.config.getint(
            'remote-semaphore', 'timeout', fallback=60)
        requeue_period = self.config.getint(
            'remote-semaphore', 'requeue-period', fallback=60)

        msg = "Attempting to acquire remote semaphore '{}'"
        logging.info(msg.format(semaphore))

        self._semaphore_lock_id = self._semaphore_client.acquire(
            semaphore=semaphore, secret=secret, timeout=timeout)
        self._semaphore_release_holddown = False

        if not self._semaphore_lock_id:
            msg = "Failed to acquire semaphore - requeueing tasks"
            logging.warning(msg)
            tasks.requeue(datetime.timedelta(seconds=requeue_period))
            return False

        logging.info("Semaphore acquired")

        return True

    def request_semaphore_release_holddown(self):
        self._semaphore_release_holddown = True

    def _release_semaphore(self):
        semaphore = self.config['remote-semaphore']['semaphore']
        holddown_period = self.config.getint(
            'remote-semaphore', 'release-holddown-period', fallback=10)
        timeout = self.config.getint(
            'remote-semaphore', 'timeout', fallback=60)

        if not self._semaphore_release_holddown:
            holddown_period = None

        if holddown_period:
            msg = "Attempting to release remote semaphore (with hold-down)"
        else:
            msg = "Attempting to release remote semaphore (no hold-down)"

        logging.info(msg)

        success = self._semaphore_client.release(
            semaphore=semaphore, lock_id=self._semaphore_lock_id,
            holddown_period=holddown_period, timeout=timeout)

        if success:
            logging.info("Semaphore released")
            return True

        logging.warning("Failed to release semaphore")
        return False

    def _connect_database(self):
        dsn = self.config['pgtask']['dsn']
        fallback_app_name = LIBRARY_FALLBACK_APPLICATION_NAME.format(
            consumer_name=self._consumer_name)
        dsn += " fallback_application_name='{}'".format(fallback_app_name)

        self._worker_connection = psycopg2.connect(dsn)
        self._worker_cursor = self._worker_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        self._worker_cursor.execute(
            REGISTER_CONSUMER_SQL, {'consumer_name': self._consumer_name})
        self._consumer_id = self._worker_cursor.fetchone()['consumer_id']

        self._worker_cursor.execute(
            SET_CONSUMER_SUBSCRIPTIONS_SQL,
            {'consumer_id': self._consumer_id, 'events': self.events})

        self._worker_cursor.execute(
            START_CONSUMER_SQL, {'consumer_id': self._consumer_id})

        self._worker_connection.commit()

        if self.provide_database_connection:
            dsn = self.config['pgtask']['dsn']
            fallback_app_name = FALLBACK_APPLICATION_NAME.format(
                consumer_name=self._consumer_name)
            dsn += " fallback_application_name='{}'".format(fallback_app_name)

            self.db_connection = psycopg2.connect(dsn)

    def _process(self):
        while self._running:
            self._process_pending_tasks()
            self._process_notifications()

    def _process_pending_tasks(self):
        tasks = self._gather_pending_tasks()
        if tasks:
            self._db_log_handler.set_tasks(tasks)
            msg = "Processing {} task{s} (task ids={!r})"
            msg = msg.format(
                len(tasks), tasks._get_task_ids(),
                s='' if len(tasks) == 1 else 's')
            logging.info(msg)

            # Acquire remote semaphore if enabled
            if self._semaphore_client:
                if not self._acquire_semaphore(tasks):
                    # Failed to acquire semaphore - tasks requeued
                    self._db_log_handler.set_tasks(None)
                    return

            try:
                self.process_tasks(tasks)
            except Exception:
                logging.exception("Exception whilst processing tasks")
                tasks.set_status('failed')
                if self.provide_database_connection:
                    self.db_connection.rollback()
            else:
                if self.provide_database_connection:
                    self.db_connection.commit()

            # Release remote semaphore if enabled
            if self._semaphore_client:
                self._release_semaphore()

            self._db_log_handler.set_tasks(None)

    def _gather_pending_tasks(self):
        self._worker_cursor.execute(
            GATHER_PENDING_TASKS_SQL, {'consumer_id': self._consumer_id})

        task_rows = self._worker_cursor.fetchall()

        tasks = TaskSet()

        for task_row in task_rows:
            task = Task(
                self, task_row['id'], task_row['event'],
                task_row['event_data'])

            tasks.append(task)

        self._worker_connection.commit()
        return tasks

    def _process_notifications(self):
        consumer_started_channel = CONSUMER_STARTED_CHANNEL.format(
            consumer_id=self._consumer_id)
        consumer_task_channel = CONSUMER_TASK_CHANNEL.format(
            consumer_id=self._consumer_id)

        next_task_at = None
        check_next_task = True

        while next_task_at is None or next_task_at > datetime.datetime.now():
            if not self._running:
                return

            if check_next_task:
                check_next_task = False

                self._worker_cursor.execute(
                    GET_NEXT_TASK_INTERVAL_SQL,
                    {'consumer_id': self._consumer_id})
                next_task_interval = (
                    self._worker_cursor.fetchone()['embargo_interval'])
                self._worker_connection.commit()

                if next_task_interval is None:
                    next_task_at = None
                else:
                    next_task_at = datetime.datetime.now() + next_task_interval

            while self._worker_connection.notifies:
                notification = self._worker_connection.notifies.pop(0)

                logging.debug("Saw notification: {!r}".format(notification))

                if notification.channel == consumer_started_channel:
                    self._process_consumer_startup(notification)
                elif notification.channel == consumer_task_channel:
                    check_next_task = True

            if check_next_task:
                continue

            if next_task_at is None:
                # infinite
                select_timeout = None
                msg = "Waiting for next notification (no tasks pending)"
            else:
                next_task_in = next_task_at - datetime.datetime.now()
                select_timeout = next_task_in.total_seconds()
                if select_timeout <= 0:
                    continue
                msg = "Waiting for next notification (next pending task in {})"
                msg = msg.format(next_task_in)

            logging.info(msg)

            in_rlist = [self._worker_connection, self._wakeup_fd]
            rlist = select.select(in_rlist, [], [], select_timeout)[0]

            # Empty the wakeup pipe if it's ready for reading
            if self._wakeup_fd in rlist:
                os.read(self._wakeup_fd, 1024)

            self._worker_connection.poll()

    def _process_consumer_startup(self, notification):
        if notification.pid == self._worker_connection.get_backend_pid():
            # Our own notification
            return

        logging.error("Another instance of this consumer has started")
        sys.exit(1)

    def _shutdown(self, signum, frame):
        self._running = False
        msg = "Shutting down due to signal {signal}"
        logging.info(msg.format(signal=signum))

    def publish_event(self, event, event_data=None, embargo=None):
        if event_data is not None:
            event_data = psycopg2.extras.Json(event_data)

        if embargo is None:
            embargo = datetime.timedelta()

        if isinstance(embargo, datetime.timedelta):
            sql = PUBLISH_EVENT_RELATIVE_EMBARGO_SQL
        else:
            sql = PUBLISH_EVENT_ABSOLUTE_EMBARGO_SQL

        self._worker_cursor.execute(
            sql,
            {'event': event, 'event_data': event_data, 'embargo': embargo})
        self._worker_connection.commit()

    def publish_task_to_self(self, event, event_data=None, embargo=None):
        if event_data is not None:
            event_data = psycopg2.extras.Json(event_data)

        if embargo is None:
            embargo = datetime.timedelta()

        if isinstance(embargo, datetime.timedelta):
            sql = PUBLISH_TASK_RELATIVE_EMBARGO_SQL
        else:
            sql = PUBLISH_TASK_ABSOLUTE_EMBARGO_SQL

        self._worker_cursor.execute(
            sql,
            {'consumer_id': self._consumer_id, 'event': event,
                'event_data': event_data, 'embargo': embargo})
        self._worker_connection.commit()


class DatabaseLogHandler(logging.Handler):
    def __init__(self):
        self._tasks = None
        super().__init__()

    def set_tasks(self, tasks):
        self._tasks = tasks

    def emit(self, record):
        if not self._tasks:
            return

        level_name = record.levelname
        if level_name not in VALID_DB_LEVEL_NAMES:
            level_name = 'ERROR'

        try:
            msg = self.format(record)
            self._tasks.log_message(level_name, msg)
        except Exception:
            self.handleError(record)
