# encoding: utf-8

__author__ = 'fzh89'

TICK_LEVEL_ONE_STOCK = 0  # 股票tick行情
TICK_LEVEL_ONE_FUTURE = 1  # 期货tick行情
TICK_LEVEL_ONE_OPTION = 2  # 期权tick行情
# LEVEL 2 tick级别行情
TICK_LEVEL_TWO_STOCK = 10  # //股票tick行情
TICK_LEVEL_TWO_FUTURE = 12  # ,   //期货tick行情
TICK_LEVEL_TWO_OPTION = 13  # ,   //期权tick

KLINE = 20

TRANSACTION = 30
ORDER = 40  # ,//订单成交
ORDER_QUEUE = 50  # ,//订单队列

SAMPLE_DATA_BEGIN = 100  # ,
SAMPLE_DATA_SECOND = 101  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_MINUTE = 102  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_DAY = 103  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_WEEK = 104  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_MONTH = 105  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_SEASON = 106  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_YEAR = 107  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_END = 200