# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import tcell_agent
from tcell_agent.agent import TCellAgent, PolicyTypes
import os
from tcell_agent.sensor_events import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events import RedirectSensorEvent
from tcell_agent.sensor_events import ServerAgentDetailsEvent

_started = False

import logging
import tcell_agent.tcell_logger
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

def instrument_gunicorn():
    from gunicorn.arbiter import Arbiter
    old_func = Arbiter.start
    def start(self):
        if (tcell_agent.instrumentation.gunicorn_tcell._started == False):
            LOGGER.info("Staring (gunicorn) agent")
            tcell_agent.instrumentation.gunicorn_tcell._started = True
            TCellAgent.get_agent().ensure_polling_thread_running()
        return old_func(self)
    Arbiter.start = start
try:
    instrument_gunicorn()
except Exception as e:
    LOGGER.debug("Gunicorn not found")
    LOGGER.debug(e)
