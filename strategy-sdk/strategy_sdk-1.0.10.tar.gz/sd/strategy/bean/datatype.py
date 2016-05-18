# encoding: utf-8

TICK_LEVEL_ONE_STOCK = 0  # 股票tick行情
TICK_LEVEL_ONE_FUTURE = 1  # 期货tick行情
TICK_LEVEL_ONE_OPTION = 2  # 期权tick行情
TICK_FUTURE = 6  # 期货tick行情
TICK_OPTION = 7  # 期权tick行情
TICK_STOCK = 8  # 股票tick行情
# LEVEL 2 tick级别行情
TICK_LEVEL_TWO_STOCK = 10  # //股票tick行情
TICK_LEVEL_TWO_FUTURE = 12  # ,   //期货tick行情
TICK_LEVEL_TWO_OPTION = 13  # ,   //期权tick

KLINE = 20
KLINE_ONE_MINUTE = 21       #1分钟线
KLINE_FIVE_MINUTE = 22      #5分钟线
KLINE_TEN_MINUTE = 23       #10分钟
KLINE_FIFTEEN_MINUTE = 24   #15分钟
KLINE_THIRTY_MINUTE = 25    #30分钟
KLINE_ONE_HOUR = 26         #1小时


KLINE_ONE_SECOND = 36
KLINE_FIVE_SECOND = 37
KLINE_TEN_SECOND = 38
KLINE_THIRTY_SECOND = 39

KLINE_END = 50

TRANSACTION = 60
ORDER = 70  # ,//订单成交
ORDER_QUEUE = 80  # ,//订单队列
###############以上是订阅的行情
##############以下是查询的行情
SAMPLE_DATA_BEGIN = 100  # ,
SAMPLE_DATA_SECOND = 101  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_MINUTE = 102  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_DAY = 103  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_WEEK = 104  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_MONTH = 105  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_SEASON = 106  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_YEAR = 107  # ,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
SAMPLE_DATA_END = 200