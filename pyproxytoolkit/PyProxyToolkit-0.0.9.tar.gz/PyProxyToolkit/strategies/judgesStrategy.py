"""
Copyright (C) 2016 Garry Lachman garry@lachman.co under GNU LGPL
https://github.com/garrylachman/PyProxyToolkit
https://rev.proxies.online

This library is free software; you can redistribute it and/or modify it under the terms of the
GNU Lesser General Public License version 2.1, as published by the Free Software Foundation.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.
"""

from .strategyAbstract import StrategyAbstract
from .judges import Jugdes
from ..proxy import Proxy
import json
import sys
import random

class JudgesStrategy(StrategyAbstract):
    def __init__(self):
        super(JudgesStrategy, self).__init__()
        self.judges_list = []
        self._url = 'http://httpbin.org/ip'

    @property
    def url(self):
        return random.choice(self.judges_list)

    def testJudges(self):
        for judge in self.judges_list:
            print(judge)

    def match(self, response, proxy: Proxy):
        json_response = json.loads(response)
        try:
            return str(json_response['origin']).find(proxy.host) > -1
        except:
            self.logger.error(sys.exc_info()[0])

        return False