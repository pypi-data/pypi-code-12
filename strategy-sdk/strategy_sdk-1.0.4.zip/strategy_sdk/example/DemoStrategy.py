# encoding: utf-8

__author__ = 'fzh89'

from strategy.stragety import SimpleStrategy
from example.config import logging


class DemoStrategy(SimpleStrategy):
    def __init__(self, quote_config, trader_config):
        super(DemoStrategy, self).__init__(quote_config, trader_config)

    def on_notify_quote(self, data):
        logging("%s", data)


if __name__ == "__main__":
    from example.config import quote_config, trader_config

    simple_strategy = DemoStrategy(quote_config, trader_config)
    if not simple_strategy.init():
        logging.error("Failed to login,exit")
        exit(1)

    # 查询用户的帐号详情
    print
    simple_strategy.req_account_detail()[1].to_json()
    # 查询用户的持仓详情
    print
    simple_strategy.req_position_statics()[1].to_json()
    # 查询用户在某个策略上的持仓详情
    print
    simple_strategy.req_position_statics(trader_config.strategyConnectionInfo.strategyId)[1].to_json()
    #查询用户的委托的订单列表
    order = simple_strategy.req_order_list()
    #查询用户在某个策略上委托的订单列表
    order = simple_strategy.req_order_list(trader_config.strategyConnectionInfo.strategyId)
    print
    order.to_json()
    # simple_strategy.req_subscribe("SHFE.rb1610.TICK_FIVE_LEVEL")
    # simple_strategy.req_unsubscribe("SHFE.rb1610.TICK_FIVE_LEVEL")
    # simple_strategy.req_unsubscribe("SHFE.rb1605.TICK_FIVE_LEVEL")
    # order_info = StrategyRequestOrder(
    #         account_id=u"test",
    #         hedge_flag=HedgeFlagType.HEDGE_FLAG_HEDGE,
    #         market=u"SHFE",
    #         product=u"rb",
    #         price=2300,
    #         volume=1,
    #         instrument=u"rb1605",
    #         strategy_id=u"1",
    #         price_type=PriceType.PRTP_FIX,
    #         interface_type=InterfaceType.INTERFACE_FUTURE,
    #         order_operation_type=OperationType.OPT_OPEN_LONG
    # )
    #
    #     # try:
    # data = simple_strategy.req_order(order_info)
    simple_strategy.run()
