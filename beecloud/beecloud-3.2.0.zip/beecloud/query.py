# -*- coding: utf-8 -*-
"""
    beecloud.query
    ~~~~~~~~~
    This module contains query API.
    :created by xuanzhui on 2015/12/24.
    :copyright (c) 2015 BeeCloud.
    :license: MIT, see LICENSE for more details.
"""

from beecloud.entity import BCResult, BCBill, BCRefund, BCReqType, _TmpObject
from beecloud.utils import get_random_host, http_get, obj_to_quote_str, set_common_attr, \
    report_not_supported_err, attach_app_sign


class _OrderType:
    BILL = 0
    REFUND = 1


class BCQuery:
    def __init__(self):
        self.bc_app = None

    def register_app(self, bc_app):
        """
        register app, which is mandatory before calling other API
        :param bc_app: beecloud.entity.self.bc_app
        """
        self.bc_app = bc_app
    
    def _query_bills_url(self):
        if self.bc_app.is_test_mode:
            return 'rest/sandbox/bills'
        else:
            return 'rest/bills'

    def _query_refunds_url(self):
        return 'rest/refunds'

    def _query_bill_url(self):
        if self.bc_app.is_test_mode:
            return 'rest/sandbox/bill'
        else:
            return 'rest/bill'

    def _query_refund_url(self):
        return 'rest/refund'

    def _query_orders(self, query_params, query_type):
        if query_type == _OrderType.BILL:
            if query_params.refund_no:
                raise ValueError('refund_no should NOT be used to query bills')
            if query_params.need_approval:
                raise ValueError('need_approval should NOT be used to query bills')
            partial_url = get_random_host() + self._query_bills_url()
        elif query_type == _OrderType.REFUND:
            if query_params.spay_result:
                raise ValueError('spay_result should NOT be used to query refunds')
            partial_url = get_random_host() + self._query_refunds_url()
        else:
            return

        attach_app_sign(query_params, BCReqType.QUERY, self.bc_app)
        url = partial_url + '?para=' + obj_to_quote_str(query_params)

        tmp_resp = http_get(url, self.bc_app.timeout)
        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            if query_type == _OrderType.BILL:
                order_dict_arr = resp_dict.get('bills')
            else:
                order_dict_arr = resp_dict.get('refunds')

            orders = []
            if order_dict_arr:
                orders = [self._parse_dict_to_obj(order_dict, query_type)
                          for order_dict in order_dict_arr]

            bc_result.count = len(orders)

            if query_type == _OrderType.BILL:
                bc_result.bills = orders
            else:
                bc_result.refunds = orders

        return bc_result

    def query_bills(self, query_params):
        """
        query bills API
        refer to https://beecloud.cn/doc/ #5
        result contains a list(bills), its items are beecloud.entity.BCBill
        :param query_params: beecloud.entity.BCQueryReqParams
        :return: beecloud.entity.BCResult
        """
        return self._query_orders(query_params, _OrderType.BILL)

    def query_refunds(self, query_params):
        """
        query refunds API
        refer to https://beecloud.cn/doc/ #7
        result contains a list(refunds), its items are beecloud.entity.BCRefund
        :param query_params: beecloud.entity.BCQueryReqParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('query_refunds')
        return self._query_orders(query_params, _OrderType.REFUND)

    def _parse_dict_to_obj(self, bill_dict, query_type):
        if query_type == _OrderType.BILL:
            obj = BCBill()
        elif query_type == _OrderType.REFUND:
            obj = BCRefund()
        else:
            return None

        for k, v in bill_dict.items():
            obj.__dict__[k] = v

        return obj

    def _query_orders_count(self, query_params, query_type):
        if query_params.need_detail or query_params.skip or query_params.limit:
            raise ValueError('need_detail or skip or limit should NOT be used to query order count')

        if query_type == _OrderType.BILL:
            if query_params.refund_no:
                raise ValueError('refund_no should NOT be used to query bills')
            if query_params.need_approval:
                raise ValueError('need_approval should NOT be used to query bills')
            partial_url = get_random_host() + self._query_bills_url() + '/count'
        elif query_type == _OrderType.REFUND:
            if query_params.spay_result:
                raise ValueError('spay_result should NOT be used to query refunds')
            partial_url = get_random_host() + self._query_refunds_url() + '/count'
        else:
            return

        attach_app_sign(query_params, BCReqType.QUERY, self.bc_app)
        url = partial_url + '?para=' + obj_to_quote_str(query_params)
        tmp_resp = http_get(url, self.bc_app.timeout)
        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()

        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.count = resp_dict.get('count')

        return bc_result

    def query_bills_count(self, query_params):
        """
        query bills count API
        refer to https://beecloud.cn/doc/ #6
        :param query_params: beecloud.entity.BCQueryReqParams
        :return: beecloud.entity.BCResult
        """
        return self._query_orders_count(query_params, _OrderType.BILL)

    def query_refunds_count(self, query_params):
        """
        query refunds count API
        refer to https://beecloud.cn/doc/ #8
        :param query_params: beecloud.entity.BCQueryReqParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('query_refunds_count')
        return self._query_orders_count(query_params, _OrderType.REFUND)

    def _query_order_by_id(self, order_id, query_type):
        if query_type == _OrderType.BILL:
            partial_url = get_random_host() + self._query_bill_url()
        elif query_type == _OrderType.REFUND:
            partial_url = get_random_host() + self._query_refund_url()
        else:
            return

        query_params = _TmpObject()
        attach_app_sign(query_params, BCReqType.QUERY, self.bc_app)
        url = partial_url + '/' + order_id + '?para=' + obj_to_quote_str(query_params)
        tmp_resp = http_get(url, self.bc_app.timeout)
        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            if query_type == _OrderType.BILL:
                order_dict = resp_dict.get('pay')
                bc_result.pay = self._parse_dict_to_obj(order_dict, _OrderType.BILL)
            else:
                order_dict = resp_dict.get('refund')
                bc_result.refund = self._parse_dict_to_obj(order_dict, _OrderType.REFUND)

        return bc_result

    def query_bill_by_id(self, bill_id):
        """
        query bill based on id(NOT bill number)
        refer to https://beecloud.cn/doc/ #11
        result.pay is type of beecloud.entity.BCBill
        :param bill_id: string type
        :return: beecloud.entity.BCResult
        """
        return self._query_order_by_id(bill_id, _OrderType.BILL)

    def query_refund_by_id(self, refund_id):
        """
        query refund based on id(NOT refund number)
        refer to https://beecloud.cn/doc/ #10
        result.refund is type of beecloud.entity.BCRefund
        :param refund_id: string type
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('query_refunds_count')
        return self._query_order_by_id(refund_id, _OrderType.REFUND)

    def query_refund_status(self, channel, refund_no):
        """
        query refund status, it is for WX, YEE, KUAIQIAN, BD
        refer to https://beecloud.cn/doc/ #9
        :param channel: str of WX, YEE, KUAIQIAN, BD
        :param refund_no: refund number
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('query_refunds_count')

        query_params = _TmpObject()
        query_params.channel = channel
        query_params.refund_no = refund_no
        attach_app_sign(query_params, BCReqType.QUERY, self.bc_app)
        url = get_random_host() + self._query_refund_url() + '/status?para=' + obj_to_quote_str(query_params)
        tmp_resp = http_get(url, self.bc_app.timeout)
        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()

        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.refund_status = resp_dict.get('refund_status')

        return bc_result

    def query_bc_transfer_supported_banks(self, transfer_type):
        """
        query bc_transfer supported banks, used by BCCardTransferParams field: bank_fullname
        :param transfer_type: P_DE:对私借记卡, P_CR:对私信用卡, C:对公账户
        :return:
        """
        query_param = _TmpObject()
        query_param.type = transfer_type
        url = get_random_host() + 'rest/bc_transfer/banks?para=' + obj_to_quote_str(query_param)
        tmp_resp = http_get(url, self.bc_app.timeout)
        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()

        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.size = resp_dict.get('size')
            bc_result.bank_list = resp_dict.get('bank_list')

        return bc_result
