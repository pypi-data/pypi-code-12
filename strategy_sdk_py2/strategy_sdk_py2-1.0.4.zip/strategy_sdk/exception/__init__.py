# encoding: utf-8

__author__ = u'Yonka'


def can_not_init(self, v):
    raise AssertionError(u"can not initiate")


class StrategyErrorCode(object):
    _instances = {}

    def __init__(self, v):
        self.v = v
        self.__class__._instances[v] = self

    def get_value(self):
        return self.v

    def from_value(self, v):
        return self.__class__._instances.get(v)

    def __str__(self):
        return u"StrategyErrorCode(%d)" % self.v

    @classmethod
    def is_success(cls, code):
        return code == 0


StrategyErrorCode.VALIDATE_SUCCESS = StrategyErrorCode(0)
StrategyErrorCode.VALIDATE_STRATEGY_NOTEXISTS = StrategyErrorCode(10001)
StrategyErrorCode.VALIDATE_ACCOUNT_NOTEXISTS = StrategyErrorCode(10002)
StrategyErrorCode.VALIDATE_ACCOUNT_WRONG_PASSWORD = StrategyErrorCode(10002)
StrategyErrorCode.SERVER_ERROR5000 = StrategyErrorCode(5000)
StrategyErrorCode.ORDER_MSG_CODE11000 = StrategyErrorCode(11000)
StrategyErrorCode.ORDER_MSG_CODE11001 = StrategyErrorCode(11001)
StrategyErrorCode.ORDER_MSG_CODE11002 = StrategyErrorCode(11002)
StrategyErrorCode.ORDER_MSG_CODE11003 = StrategyErrorCode(11003)
StrategyErrorCode.ORDER_MSG_CODE11004 = StrategyErrorCode(11004)

StrategyErrorCode.__init__ = can_not_init
