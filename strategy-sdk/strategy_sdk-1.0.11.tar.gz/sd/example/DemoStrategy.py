# -*- coding:utf-8 -*-


from sd.strategy.stragety import SimpleStrategy
from sd.configuration.defaultconfig import logging


class DemoStrategy(SimpleStrategy):
    def __init__(self, quote_config, trader_config):
        super(DemoStrategy, self).__init__(quote_config, trader_config)

    def on_notify_quote(self, data):
        logging("%s", data)


if __name__ == "__main__":
    from sd.configuration import quote_config, trader_config


    simple_strategy = DemoStrategy(quote_config, trader_config)
    if not simple_strategy.init():
        logging.error("Failed to login,exit")
        exit(1)

    # 查询用户的帐号详情
    (result,error)=simple_strategy.req_account_detail()
    if error.errorId!=0:
        logging.error(error.to_dict())
    else:
        for item in result:
            logging.info(item.to_dict())
    # 查询用户的持仓详情
    (result,error)=simple_strategy.req_position_detail()
    if error.errorId!=0:
        logging.error(error.to_json())
    else:
        for item in result:
            logging.info(item.to_json())
    # #查询用户在某个策略上的持仓详情
    # (result,error)=simple_strategy.req_position_statics(trader_config.strategyConnectionInfo.strategyId)
    # if error.errorId!=0:
    #     logging.error(error.to_json())
    # else:
    #     for item in result:
    #         logging.info(item.to_json())
    # #查询用户的委托的订单列表
    # (result,error)= simple_strategy.req_order_list()
    # if error.errorId!=0:
    #     logging.error(error.to_json())
    # else:
    #     for item in result:
    #         logging.info(item.to_json())
    # #查询用户在某个策略上委托的订单列表
    # (result,error) = simple_strategy.req_order_list("Medusa_ni1609_16")
    # if error.errorId!=0:
    #     logging.error(error.to_json())
    # else:
    #     for item in result:
    #         logging.info(item.to_json())    # simple_strategy.req_subscribe("SHFE.rb1610.TICK_FIVE_LEVEL")
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
