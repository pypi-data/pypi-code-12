import time
import logging
from uliweb.utils.workers import *

logging.basicConfig(level=logging.INFO)

# class NewWorker(Worker):
#     def init(self):
#         self.log = make_log(self.log, 'new_worker.log')
#         super(NewWorker, self).init()
#
#     def run(self):
#         s = []
#         for i in range(50000):
#             s.append(str(i))
#         self.log.info ('result= %d ' % len(s))
#         time.sleep(1)
#         return True
#
# workers = [Worker(max_requests=2),
#            NewWorker(max_requests=2, timeout=5, name='NewWorker',
#                      soft_memory_limit=5, hard_memory_limit=10)]
# manager = Manager(workers, check_point=1)
# manager.start()

# import redis
#
# class NewWorker(Worker):
#     def init(self):
#         super(NewWorker, self).init()
#         self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
#
#     def run(self):
#
#         message = self.redis.brpop('redis_queue', 10)
#         if message:
#             self.log.info(message[1])
#
#             return True
#
# workers = [NewWorker(max_requests=2, name='Redis Worker')]
# manager = Manager(workers, check_point=5)
# manager.start()

import redis

class NewWorker(Worker):
    def init(self):
        super(NewWorker, self).init()
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.queue = self.kwargs['queue']

    def get_message(self):
        message = self.redis.lindex(self.queue, 0)
        if not message:
            message = self.redis.brpoplpush('redis_queue', self.queue, 10)

        return message

    def run(self):

        message = self.get_message()
        if message:
            self.log.info(message)
            self.redis.lpop(self.queue)

            return True

workers = [NewWorker(max_requests=2, name='Redis Worker', queue='worker')]
manager = Manager(workers, check_point=5)
manager.start()
