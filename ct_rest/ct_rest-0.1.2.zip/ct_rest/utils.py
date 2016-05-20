# -*- coding:utf-8 -*-
import datetime, time, django


def to_dict(target):
    '''
    turn models object to dict
    Args:
        target:

    Returns:

    '''
    def _to_dict(modelIns):
        temp = modelIns.__dict__
        for k,v in temp.items():
            if k[0] == "_":
                del temp[k]
            elif type(v) == datetime.datetime:
                temp[k] = time.mktime(datetime.datetime.timetuple(v))
        return temp

    if type(target) == django.db.models.query.QuerySet:
        resp = []
        for ins in target:
            resp.append(_to_dict(ins))
        return resp
    else:
        return _to_dict(target)