# encoding: utf-8

__author__ = u'Yonka'

# /** terminal=type **/
TERMINAL_TRADE = 0
TERMINAL_QUOTE = 1

# /*** =terminal=<>=center=proto ***/
HEARTBEAT = 0
ACK = 1
MANAGERLOGIN = 2  # terminal=login=to=center
CONNECTFRONT = 3  # quant=center=send=order
TERMINALLOGIN = 4
STRATEGYLOGIN = 5

# /******* =data=type= *******/
STRATEGY = 0

CTP_FUTURE = 1
ZX_OPTION = 2
ZX_STOCK = 3


# /*************************
# * strategy functioncode
# * *************************/
# /**request**/
REQ_ST_POTITIONDETAIL = 10000
REQ_ST_ACCOUNTETAIL = 10001
REQ_ST_POTITIONDSTATICS = 10002
REQ_ST_ORDER = 10003
REQ_ST_CANCELORDER = 10004
REQ_ST_SUBSCRIBE = 10005
REQ_ST_UNSUBSCRIBE = 10006
REQ_ST_ORDERLIST = 10007
REQ_ST_DATA = 10008

# /**response**/
RESP_ST_POTITIONDETAIL = 1100
RESP_ST_ACCOUNTETAIL = 11001
RESP_ST_POTITIONDSTATICS = 11002
RESP_ST_ORDER = 11003
RESP_ST_CANCELORDER = 11004
NOTIFY_ST_ORDERERROR = 11005
NOTIFY_ST_ORDERDETAIL = 11006
NOTIFY_ST_SUBSCRIBE = 11007
NOTIFY_ST_REQERROR = 11008
NOTITY_ST_CTPORDERID = 11009
NOTIFY_ST_UNSUBSCRIBE = 11010
RESP_ST_LOGIN = 11011
RESP_ST_SUBSCRIBE = 11012
RESP_ST_UNSUBSCRIBE = 11013
RESP_ST_ERROR = 11014

# request
REQ_ACCOUNTDETAIL = 100
REQ_POSITIONDETAIL = 101
REQ_POSITIONSTATICS = 102
REQ_ORDER = 103
REQ_CACELORDER = 104
REQ_SUBSCRIBE = 105
REQ_UNSUBSCRIBE = 106

REQ_QUOTEDATA = 107
REQ_QRYTRADE = 108
REQ_QRYORDER = 109
REQ_INSTRUMENTS = 110
REQ_QRYINSTRUMENT_COMMISSIONRATEFIELD = 111
REQ_QRYINSTRUMENT_MARGINRATEFIELD = 112

# response
RESP_ACCOUNTDETAIL = 500
RESP_POSITIONDETAIL = 501
RESP_POSITIONSTATICS = 502
RESP_ERROR = 503
RESP_ORDER = 504
RESP_CANCELORDER = 505
RESP_SUBSCRIBE = 506
RESP_UNSUBSCRIBE = 507
RESP_QUOTEDATA = 508
RESP_FINISHED = 509
RESP_QRYTRADE = 510
RESP_QRYORDER = 512
RESP_INSTRUMENTS = 513
RESP_QRYINSTRUMENT_COMMISSIONRATEFIELD = 514
RESP_QRYINSTRUMENT_MARGINRATEFIELD = 515

# notify
NOTIFY_ORDERDETAIL = 600
NOTIFY_ORDERERROR = 601
NOTIFY_TRADEDETAIL = 602
NOTIFY_CANCELERROR = 603
NOTIFY_LINKERROR = 604

# /*----------------------------------------------------------------*/
# /******************** =1001~2000=zx=option ************************/
#  行情
REQ_OPT_PRICE_QRY = 1001  # 期权行情查询public final
#  static int public
#  final static int 395
#  交易
REQ_OPTCODE_QRY = 1002  # 期权代码信息查询=public final
#  static int 338000
REQ_OPTCODE_IQRY = 1003  # 获取期权标的证券信息=public
#  final static int
#  338001
REQ_OPTCODE_ENTER = 1004  # 期权代码输入确认public final
#  static int 338002
REQ_OPT_ENTRADE = 1005  # 期权可交易数量获取public final
#  static int 338010
REQ_OPT_ENTRUST = 1006  # 期权委托public final static
#  int public final
#  static int 338011
REQ_OPT_WITHDRAW = 1007  # 期权撤单public final
#  static int public
#  final static int
#  338012
REQ_OPT_ENTRUSTQRY = 1008  # 期权委托查询public final
#  static int public
#  final static int
#  338020
REQ_OPT_REALTIME_QRY = 1009  # 期权成交查询public final
#  static int
#  public final
#  static int 338021
REQ_OPT_ASSET_QRY = 1010  # 期权资产查询public final
#  static int public
#  final static int
#  338022
REQ_OPT_HOLD_QRY = 1011  # 期权持仓查询public final
#  static int public
#  final static int
#  338023
REQ_OPT_EXEASSIGN_QRY = 1012  # 期权行权指派查询public
#  final static int
#  338024
REQ_ASSET_OPTEXEDELIVER_QRY = 1013  # 期权行权交割信息查询public
#  final
#  static
#  int
#  338025

REQ_ASSET_DEBTINFO_QRY = 1014  # 期权行权指派欠资欠券查询
#  338026
REQ_OPT_UNDERLYAMOUNT_PROMPT = 1015  # 期权标的证券数量提示public
#  final
#  static
#  int
#  338027
REQ_OPT_OPTHOLDREAL_PROMPT = 1016  # 客户期权持仓合约信息提示
#  338028
REQ_ASSET_ASSETCOVERSTOCK_QRY = 1017  # =客户备兑证券不足查询=
#  338029

#  历史交易查询
REQ_HIS_OPTENTRUST_QRY = 1050  # 历史期权委托查询public
#  final static int
#  339800
REQ_HIS_OPTBUSINESS_QRY = 1051  # 历史期权成交查询public
#  final static
#  int 339801
REQ_HIS_OPTDELIVER_QRY = 1052  # 历史期权交割信息查询public
#  final static int
#  339803
REQ_HIS_EXEASSIGN_QRY = 1053  # 历史期权行权指派查询public
#  final static int
#  339804
REQ_HIS_OPTEXEDELIVER_QRY = 1054  # 历史期权行权交割信息查询
#  339805
REQ_HIS_OPTSTATEMENT_QRY = 1055  # 历史期权对账单查询public
#  final static
#  int 339806

#  resp
RESP_OPT_ENTRUST = 1501  # 下单返回
RESP_OPT_ENTRUST_QRY = 1502  # 期权委托查询返回
RESP_OPT_REALTIME_QRY = 1503  # 期权成交查询返回
RESP_OPT_ASSET_QRY = 1504  # 期权资产查询返回
RESP_OPT_HOLD_QRY = 1505  # 持仓查询返回
RESP_OPT_WITHDRAW = 1506  # 撤单返回
RESP_OPT_ENTRADE = 1507  # 获取可交易数量返回
RESP_OPTCODE_ENTER = 1508  # 期权代码输入确认返回

NOTIFY_REALTIME = 1600  # 成交notify


# /**********以下为期货属性常量值**************/
#  下单类型
PRTP_FIX = 11  # 限价单
PRTP_MARKET = 12  # 市价单

#  操作指令常量
OPT_OPEN_LONG = 0
OPT_CLOSE_LONG_HISTORY = 1
OPT_CLOSE_LONG_TODAY = 2
OPT_OPEN_SHORT = 3
OPT_CLOSE_SHORT_HISTORY = 4
OPT_CLOSE_SHORT_TODAY = 5
OPT_CLOSE_LONG_TODAY_FIRST = 6
OPT_CLOSE_LONG_HISTORY_FIRST = 7
OPT_CLOSE_SHORT_TODAY_FIRST = 8
OPT_CLOSE_SHORT_HISTORY_FIRST = 9
OPT_CLOSE_LONG_TODAY_HISTORY_THEN_OPEN_SHORT = 10
OPT_CLOSE_LONG_HISTORY_TODAY_THEN_OPEN_SHORT = 11
OPT_CLOSE_SHORT_TODAY_HISTORY_THEN_OPEN_LONG = 12
OPT_CLOSE_SHORT_HISTORY_TODAY_THEN_OPEN_LONG = 13
OPT_CLOSE_LONG = 14
OPT_CLOSE_SHORT = 15
OPT_OPEN = 16
OPT_CLOSE = 17
OPT_BUY = 18
OPT_SELL = 19
OPT_FIN_BUY = 20
OPT_SLO_SELL = 21
OPT_BUY_SECU_REPAY = 22
OPT_DIRECT_SECU_REPAY = 23
OPT_SELL_CASH_REPAY = 24
OPT_DIRECT_CASH_REPAY = 25

# /************************期权相并常量值************************/
# entrust_prop	委托属性（数据字典项1200)
ENTRUST_PROP_GFD = u"0"  # 限价GFD
ENTRUST_PROP_OPA = u"OPA"  # 限价即时全部成交否则撤单
ENTRUST_PROP_OPB = u"OPB"  # 市价即时成交剩余撤单
ENTRUST_PROP_OPC = u"OPC"  # 市价即时全部成交否则撤单
ENTRUST_PROP_OPD = u"OPD"  # 市价剩余转限价
ENTRUST_PROP_OTE = u"OTE"  # 期权行权
ENTRUST_PROP_OTU = u"OTU"  # 备兑证券划转
# option_type	期权类型（数据字典项36002)
OPTION_TYPE_C = u"C"  # 认购
OPTION_TYPE_P = u"P"  # 认沽
# entrust_oc	开平仓方向（数据字典项36300)
ENTRUST_OC_O = u"O"  # 开仓
ENTRUST_OC_C = u"C"  # 平仓
ENTRUST_OC_X = u"X"  # 行权
ENTRUST_OC_A = u"A"  # 自动行权
# covered_flag	备兑标志（数据字典项36301)
COVERED_FLAG_1 = u"1"  # 备兑
# OPTHOLD_TYPE	期权持仓类别（数据字典项36013）
OPTHOLD_TYPE_0 = u"0"  # 权利方
OPTHOLD_TYPE_1 = u"1"  # 义务方
OPTHOLD_TYPE_2 = u"2"  # 备兑方
# OPT_OPEN_STATUS	期权开仓限制（数据字典项36005）
OPT_OPEN_STATUS_0 = u"0"  # 否
OPT_OPEN_STATUS_1 = u"1"  # 是
# OPTION_FLAG	期权合约挂牌标志（数据字典项36008）
OPTION_FLAG_A = u"A"  # 当日新挂牌合约
OPTION_FLAG_E = u"E"  # 存续合约
OPTION_FLAG_D = u"D"  # 当日摘牌合约
# OPT_FINAL_STATUS	期权开仓限制（数据字典项36006）
OPT_FINAL_STATUS_0 = u"0"  # 否
OPT_FINAL_STATUS_1 = u"1"  # 是
# FINANCE_TYPE	金融品种（数据字典项1310）
FINANCE_TYPE_8 = u"8"  # 期权
# BUSINESS_STATUS	成交状态
BUSINESS_STATUS_0 = u"0"  # 成交
BUSINESS_STATUS_2 = u"2"  # 废单
BUSINESS_STATUS_4 = u"4"  # 确认
# OPTEXE_STG_KIND	自动行权策略类别（数据字典36035）
OPTEXE_STG_KIND_0 = u"0"  # 实值X元即行权
OPTEXE_STG_KIND_1 = u"1"  # 盈利X元即行权
OPTEXE_STG_KIND_2 = u"2"  # 盈利百分比即行权
OPTEXE_STG_KIND_3 = u"3"  # 亏损百分比即行权
OPTEXE_STG_KIND_4 = u"4"  # 实值百分比即行权
# ENTRUST_SRC	委托来源（数据字典36017）
ENTRUST_SRC_0 = u"0"  # 个人投资者发起
ENTRUST_SRC_1 = u"1"  # 交易所发起
ENTRUST_SRC_2 = u"2"  # 会员发起
ENTRUST_SRC_3 = u"3"  # 机构投资者发起
ENTRUST_SRC_4 = u"4"  # 自营交易发起
ENTRUST_SRC_5 = u"5"  # 流动性服务提供商发起
# OPTRIKE_TYPE	风险类别（数据字典36031）
OPTRIKE_TYPE_1 = u"1"  # 关注
OPTRIKE_TYPE_2 = u"2"  # 警告
OPTRIKE_TYPE_3 = u"3"  # 强平
# DEBT_TYPE	负债类型（数据字典36037）
DEBT_TYPE_1 = u"1"  # 欠资
DEBT_TYPE_2 = u"2"  # 欠券
