# -*- coding: utf-8 -*-

# 直接gauge的
GAUGE_STAT_LIST = [
    'clients',
    'busy_workers',
    'idle_workers',
    'pending_tasks',
]

# 间隔一段时间，然后调用incr的
INCR_STAT_LIST = [
    'client_req',
    'client_rsp',
    'worker_req',
    'worker_rsp',
    'tasks_time',
]
