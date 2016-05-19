# -*- coding: utf-8 -*-

"""
读取gateway统计数据，并上报数据至statsd
"""

from stat_reader import StatReader
import constants


class StatReporter(object):

    # 需要上报gauge的
    gauge_stat_list = constants.GAUGE_STAT_LIST
    # 需要上报incr的
    incr_stat_list = constants.INCR_STAT_LIST

    stat_reader = None
    statsd_client = None
    statsd_prefix = None

    # 统计上报时的命名转化
    statsd_name_converter = None

    # 上次的stat_reader的结果
    last_stat_result = None

    def __init__(self, cmd, statsd_client, statsd_name_converter=None):
        """
        :param cmd: 统计命令
        :param statsd_client: statsd_client
        :param statsd_name_converter: statsd统计上报名字转换函数
        :return:
        """

        self.stat_reader = StatReader(cmd)
        self.statsd_client = statsd_client
        # 默认是不变
        self.statsd_name_converter = statsd_name_converter or (lambda x: x)

    def report(self):
        """
        上报
        :return:
        """

        result = self.stat_reader.read()

        for local_stat_name in self.gauge_stat_list:
            stat_data = result.get(local_stat_name)
            if stat_data is None:
                continue

            if isinstance(stat_data, dict):
                # 说明还有子数据
                for key, value in stat_data.items():
                    real_local_stat_name = '%s.%s' % (local_stat_name, key)
                    remote_stat_name = self.statsd_name_converter(real_local_stat_name)

                    self.statsd_client.gauge(remote_stat_name, value)
            else:
                remote_stat_name = self.statsd_name_converter(local_stat_name)
                self.statsd_client.gauge(remote_stat_name, stat_data)

        if self.last_stat_result is not None:
            for local_stat_name in self.incr_stat_list:
                stat_data = result.get(local_stat_name)

                if stat_data is None:
                    continue

                if isinstance(stat_data, dict):
                    # 说明还有子数据
                    for key, value in stat_data.items():
                        real_local_stat_name = '%s.%s' % (local_stat_name, key)
                        remote_stat_name = self.statsd_name_converter(real_local_stat_name)

                        value = value - self.last_stat_result.get(local_stat_name, dict()).get(key, 0)

                        self.statsd_client.gauge(remote_stat_name, value)
                else:
                    remote_stat_name = self.statsd_name_converter(local_stat_name)
                    # 上一个值默认为0
                    value = stat_data - self.last_stat_result.get(local_stat_name, 0)
                    self.statsd_client.incr(remote_stat_name, value)

        self.last_stat_result = result

