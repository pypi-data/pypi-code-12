#!/usr/bin/env python
# -*- coding: utf-8 -*-
#{{v}}
import datetime
import json
import decimal
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__str__()
        elif isinstance(obj,decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
if __name__ == '__main__':
    data={
        "date":datetime.datetime.now(),
        "price":decimal.Decimal("100.3"),
        "id":100L
    }
    print json.dumps(data, cls=JsonEncoder)
