# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from bennu.externaldb import CameoMongoDb
"""
外部資料庫存取
"""
#匯率API
class ExternalDbForCurrencyApi:
    
    #建構子
    def __init__(self):
        self.mongodb = CameoMongoDb().getClient().tier
        