# encoding: utf-8
import logging
import signal
import sys

from gevent.threadpool import ThreadPool
from kombu import Connection, Queue, Producer
from kombu.exceptions import MessageStateError
from kombu.mixins import ConsumerMixin

from models.worker_message import WorkerMessage

reload(sys)
sys.setdefaultencoding('utf-8')

CONSUME_SUCCESS = 0
CONSUME_REDELIVER = 1
CONSUME_REJECT = 2


class Consumer(ConsumerMixin):
    def __init__(self, amqp_url, queue, logger=None, prefetch_count=30, thread_num=5, heart_interval=30,
                 consumer_tag=None, is_rpc=False):
        """
        初始化Consumer
        :param amqp_url: 队列amqp地址
        :param queue: 队列名称
        :param logger: logger对象
        :param prefetch_count: 一次拉取消息数量，默认30
        :param thread_num: 线程或进程数量，默认5
        :param heart_interval: 心跳间隔，默认30秒
        :param consumer_tag: Consumer标签
        :param is_rpc: 是否为RPC服务，默认为False
        :return:
        """
        self.logger = logging if logger is None else logger
        try:
            import librabbitmq
            self.connection = Connection(amqp_url, transport='librabbitmq', heartbeat=heart_interval)
        except ImportError:
            self.logger.warn('librabbmq is not installed!')
            self.connection = Connection(amqp_url, heartbeat=heart_interval)
        self.consumers = []
        self.pool = ThreadPool(thread_num)
        self.queue = queue
        self.handle_message_worker = None
        # 限制单个channel可同时拉取的消息数量
        self.prefetch_count = prefetch_count
        self.consumer_tag = consumer_tag
        self.is_rpc = is_rpc

    def get_consumers(self, consumer_cls, channel):
        consumer = consumer_cls(Queue(self.queue), callbacks=[self.on_message], tag_prefix=self.consumer_tag,
                                auto_declare=False)
        consumer.qos(prefetch_count=self.prefetch_count)
        self.consumers.append(consumer)
        return self.consumers

    def on_message(self, body, message):
        self.logger.debug("Received message: %s" % body)
        self.pool.spawn(self.message_worker, WorkerMessage(message), message)

    def stop(self, sig_number, stack_frame):
        """
        停止
        :param stack_frame: the current stack frame
        :param sig_number: the signal number
        :return:
        """
        self.logger.info('Stopping')
        for consumer in self.consumers:
            consumer.close()
        # 关闭线程池
        self.pool.kill()
        self.pool.join()
        self.connection.release()
        self.logger.info('Stopped')

    def register_worker(self, worker):
        """
        注册实际处理消息的worker
        :param worker: 处理消息方法
        :return:
        """
        self.logger.info("Start register message worker")
        self.handle_message_worker = worker

    def message_worker(self, worker_message, message):
        """
        处理消息方法
        :param worker_message: 消息对象
        :param message: Message对象
        :return:
        """
        self.logger.debug('Start processing message,delivery_tag = %s', worker_message.delivery_tag)
        result = self.handle_message_worker(worker_message)
        if isinstance(result, tuple):
            result_code = result[0]
            result_msg = result[1]
        else:
            result_code = result
            result_msg = None
        self.logger.debug('Message have been processed. Result code = %s; Result Msg = %s', result_code, result_msg)
        try:
            if result_code == CONSUME_SUCCESS:
                message.ack()
            elif result_code == CONSUME_REDELIVER:
                message.requeue()
            elif result_code == CONSUME_REJECT:
                self.logger.warn('The message will be rejected! Body = %s', worker_message.body)
                message.reject()
            else:
                self.logger.warn(
                        'Return code must be CONSUME_SUCCESS/CONSUME_REDELIVER/CONSUME_REJECT. Current code is %s',
                        result_code)
            # 判断是否为rpc服务
            if self.is_rpc:
                Producer(message.channel).publish(body=str(result_msg), routing_key=message.properties['reply_to'],
                                                  **{'correlation_id': message.properties['correlation_id']})
        except MessageStateError:
            self.logger.error('The message has already been acknowledged/requeued/rejected!')

    def run(self, _tokens=1):
        if self.handle_message_worker is None:
            raise Exception('未注册消息处理方法！')
        else:
            # 增加信号
            signal.signal(signal.SIGTERM, self.stop)
            signal.signal(signal.SIGINT, self.stop)
            super(Consumer, self).run()
