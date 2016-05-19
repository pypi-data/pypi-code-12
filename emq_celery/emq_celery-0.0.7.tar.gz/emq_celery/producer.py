#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'bac'

import uuid, base64, json

from rpc.auth.ttypes import Credential, UserType
from emq.client.clientfactory import ClientFactory
from emq.message.ttypes import SendMessageRequest, SendMessageBatchRequest, SendMessageBatchRequestEntry
from emq.queue.ttypes import QueueAttribute, CreateQueueRequest, ListQueueRequest
import transport


class Producer(object):
    default_delay_seconds = 0
    default_limit_seconds = 12 * 3600  # 默认 12 hours,因为emq最大支持12小时

    queue_client = None
    message_client = None

    def __init__(self, emq_key, emq_secret, emq_endpoint):
        credential = Credential(UserType.APP_SECRET, emq_key, emq_secret)
        client_factory = ClientFactory(credential)
        self.queue_client = client_factory.queue_client(emq_endpoint)
        self.message_client = client_factory.message_client(emq_endpoint)
        pass

    def _get_emq_quene_name(self, queue):
        queue = transport._format_name(queue)
        req = ListQueueRequest(queueNamePrefix=queue)
        res = self.queue_client.listQueue(req)
        if not res.queueName:
            queue_attribute = QueueAttribute()
            create_request = CreateQueueRequest(queueName=queue, queueAttribute=queue_attribute)
            create_queue_response = self.queue_client.createQueue(create_request)
            queue_name = create_queue_response.queueName
        else:
            queue_name = res.queueName[0]
        return queue_name

    def _send(self, queue, message, delay_seconds, invisible_seconds):
        """
        发消息
        :param queue: (字符串)queue名称(或者queue名称的前缀)
        :param message:(字符串)消息内容
        :param invisible_seconds:(int)emq invisible_seconds
        :param delay_seconds:(int)emq invisible_seconds
        :return:
        """
        queue_name = self._get_emq_quene_name(queue)
        req = SendMessageRequest(queue_name, message, delay_seconds if delay_seconds else self.default_delay_seconds,
                                 invisible_seconds if invisible_seconds else self.default_limit_seconds)
        self.message_client.sendMessage(req)

    def _batch_send(self, queue, messages):
        """
        批量发消息
        :param queue: (字符串)queue名称(或者queue名称的前缀)
        :param messages:(list) 元素为tuple(message,delaySeconds,invisibilitySeconds)
        :return:
        """
        entries = list()
        index = 1
        for msg in messages:
            entries.append(
                SendMessageBatchRequestEntry(str(index), msg[0], msg[1] if msg[1] else self.default_delay_seconds,
                                             msg[2] if msg[2] else self.default_limit_seconds))
            index += 1

        queue_name = self._get_emq_quene_name(queue)
        req = SendMessageBatchRequest(queue_name, entries)
        self.message_client.sendMessageBatch(req)

    def _pack_message(self, task, limit_seconds, *args, **kwargs):
        """
        打包消息
        :param task:
        :param limit_seconds:
        :param args:
        :param kwargs:
        :return:
        """

        if limit_seconds > 12 * 3600:
            raise Exception("EMQ的visibility_timeout最大支持为12小时")

        task_id = uuid.uuid4().hex
        reply_to = uuid.uuid4().hex
        delivery_tag = uuid.uuid4().hex
        msg = dict()
        msg["content-type"] = 'application/json'
        msg["content-encoding"] = 'utf-8'
        msg["properties"] = {
            'body_encoding': 'base64',
            'correlation_id': task_id,
            'reply_to': reply_to,
            'delivery_info': {
                'priority': 0
            },
            'delivery_mode': 2,
            'delivery_tag': delivery_tag
        }
        msg["body"] = base64.b64encode(json.dumps({
            "expires": None,
            "utc": True,
            "args": args,
            "kwargs": kwargs,
            "chord": None,
            "callbacks": None,
            "errbacks": None,
            "taskset": None,
            "id": task_id,
            "retries": 0,
            "task": task,
            "timelimit": [limit_seconds, None],
            "eta": None
        }).encode('utf-8'))
        return json.dumps(msg)

    def basic_publish(self, queue, task, *args, **kwargs):
        """
        发送消息到任务
        :param queue: emq队列名称
        :param task: celery 任务名
        :param args: celery 任务参数*
        :param kwargs: celery 任务参数**
        :return:
        """
        self.publish(queue, task, self.default_delay_seconds, self.default_limit_seconds, *args,
                     **kwargs)

    def publish(self, queue, task, delay_seconds=default_delay_seconds, limit_seconds=default_limit_seconds, *args,
                **kwargs):
        """
        发布任务
        :param queue: (字符串)emq queue名称
        :param task:  (字符串)celery task
        :param args:  (list)task的参数
        :param kwargs: (dict)task的参数
        :param limit_seconds: (int) 任务的执行时间 单位:秒
        :param delay_seconds: (int) 发送完成后延迟交付任务的时间 单位:秒
        :return:
        """
        self._send(queue, self._pack_message(task, None, *args, **kwargs), delay_seconds, limit_seconds)

    def batch_publish(self, queue, tasks):
        """
        批量发送任务
        :param queue: (字符串)emq queue名称
        :param tasks: (list)任务列表
                        元素为长度为3或5的tuple
                            (task,[args],{kwargs},delay_seconds,limit_seconds)
                        如果元素tuple长度为3时,表示使用默认的delay_seconds和limit_seconds
        :return:
        """
        messages = list()
        for task in tasks:
            if len(task) == 5:
                delay_seconds = task[3]
                limit_seconds = task[4]
            else:
                delay_seconds = self.default_delay_seconds
                limit_seconds = self.default_limit_seconds
            args = task[1]
            kwargs = task[2]
            if not args:
                args = []
            if not kwargs:
                kwargs = {}
            messages.append(
                (self._pack_message(task[0], None, *args, **kwargs), delay_seconds, limit_seconds))

        self._batch_send(queue, messages)
