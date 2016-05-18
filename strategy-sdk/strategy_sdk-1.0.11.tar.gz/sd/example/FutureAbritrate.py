# -*- coding:utf-8 -*-
from sd.strategy.stragety import SimpleStrategy
from sd.configuration.defaultconfig import logging

__author__ = 'patronfeng'


class FutureArbitrate(SimpleStrategy):
    def __init__(self, quote_config, trader_config):
        super(FutureArbitrate, self).__init__(quote_config, trader_config)
        self.symbol_near = ""
        self.symbol_remote = ""
        self.buy_ratio = 1.5
        self.close_profit = 3.5
        self.stop_loss = 2.0
        self.target_volume = 1
        self.direction = 0
        self.symbol_near_price = None
        self.symbol_remote_price = None

    def init(self):
        # 初始化历史数据或者当前持仓情况
        ret = self.req_subscribe(self.symbol_near)
        if ret.errorId != 0:
            logging.error("Failed to subscribe %s because of %s; exit", self.symbol_near, ret.to_json())
            exit(1)
        ret = self.req_subscribe(self.symbol_remote)
        if ret.errorId != 0:
            logging.error("Failed to subscribe %s because of %s", self.symbol_remote, ret.to_json())
            exit(1)

    def on_notify_quote(self, dataType, data):
        pass