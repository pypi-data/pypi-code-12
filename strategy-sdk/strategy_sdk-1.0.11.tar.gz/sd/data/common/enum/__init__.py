# encoding: utf-8
from __future__ import absolute_import
import unittest

from sd.utils.enum import EnumMetaCls, CommonNameValueEnum, can_not_init

__author__ = u'yonka'


class EntrustBS(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"EntrustBS(%d)" % self.v


EntrustBS.ENTRUST_BUY = EntrustBS(48)
EntrustBS.ENTRUST_SELL = EntrustBS(49)

EntrustBS.__init__ = can_not_init


class HedgeFlagType(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"HedgeFlagType(%d)" % self.v


HedgeFlagType.HEDGE_FLAG_SPECULATION = HedgeFlagType(49)
HedgeFlagType.HEDGE_FLAG_ARBITRAGE = HedgeFlagType(50)
HedgeFlagType.HEDGE_FLAG_HEDGE = HedgeFlagType(51)

HedgeFlagType.__init__ = can_not_init


class OffsetFlagType(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"OffsetFlagType(%d)" % self.v


OffsetFlagType.EOFF_THOST_FTDC_OF_INVALID = OffsetFlagType(-1)
OffsetFlagType.EOFF_THOST_FTDC_OF_Open = OffsetFlagType(48)
OffsetFlagType.EOFF_THOST_FTDC_OF_Close = OffsetFlagType(49)
OffsetFlagType.EOFF_THOST_FTDC_OF_ForceClose = OffsetFlagType(50)
OffsetFlagType.EOFF_THOST_FTDC_OF_CloseToday = OffsetFlagType(51)
OffsetFlagType.EOFF_THOST_FTDC_OF_CloseYesterday = OffsetFlagType(52)
OffsetFlagType.EOFF_THOST_FTDC_OF_ForceOff = OffsetFlagType(53)
OffsetFlagType.EOFF_THOST_FTDC_OF_LocalForceClose = OffsetFlagType(54)

OffsetFlagType.__init__ = can_not_init


class EntrustSubmitStatus(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"EntrustSubmitStatus(%d)" % self.v


EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_InsertSubmitted = EntrustSubmitStatus(48)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_CancelSubmitted = EntrustSubmitStatus(49)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_ModifySubmitted = EntrustSubmitStatus(50)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_OSS_Accepted = EntrustSubmitStatus(51)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_InsertRejected = EntrustSubmitStatus(52)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_CancelRejected = EntrustSubmitStatus(53)
EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_ModifyRejected = EntrustSubmitStatus(54)

EntrustSubmitStatus.__init__ = can_not_init


class EntrustStatus(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"EntrustSubmitStatus(%d)" % self.v


EntrustStatus.ENTRUST_STATUS_CREATED = EntrustStatus(10)
EntrustStatus.ENTRUST_STATUS_UNREPORTED = EntrustStatus(13)
EntrustStatus.ENTRUST_STATUS_REPORTED = EntrustStatus(15)
EntrustStatus.ENTRUST_STATUS_NOT_TRADE = EntrustStatus(16)
EntrustStatus.ENTRUST_STATUS_PART_SUCC = EntrustStatus(17)
EntrustStatus.ENTRUST_STATUS_SUCCEEDED = EntrustStatus(19)
EntrustStatus.ENTRUST_STATUS_UNREPORTED_CANCEL = EntrustStatus(20)
EntrustStatus.ENTRUST_STATUS_REPORTED_CANCEL = EntrustStatus(23)
EntrustStatus.ENTRUST_STATUS_CANCELED = EntrustStatus(54)
EntrustStatus.ENTRUST_STATUS_NOT_FUND = EntrustStatus(100)

EntrustStatus.__init__ = can_not_init


class TestEnum(unittest.TestCase):
    def test_init_entrust_bs(self):
        print EntrustBS.ENTRUST_BUY
        res = False
        try:
            EntrustBS(48)
        except AssertionError:
            res = True
        assert res

    def test_init_hedge_flag_type(self):
        print HedgeFlagType.HEDGE_FLAG_SPECULATION
        res = False
        try:
            HedgeFlagType(49)
        except AssertionError:
            res = True
        assert res

    def test_init_offset_flag_type(self):
        print OffsetFlagType.EOFF_THOST_FTDC_OF_INVALID
        res = False
        try:
            OffsetFlagType(49)
        except AssertionError:
            res = True
        assert res

    def test_init_entrust_submit_status(self):
        print EntrustSubmitStatus.ENTRUST_SUBMIT_STATUS_InsertSubmitted
        res = False
        try:
            EntrustSubmitStatus(49)
        except AssertionError:
            res = True
        assert res

    def test_init_entrust_status(self):
        print EntrustStatus.ENTRUST_STATUS_CREATED
        res = False
        try:
            EntrustStatus(100)
        except AssertionError:
            res = True
        assert res
