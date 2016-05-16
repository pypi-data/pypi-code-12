"""
    Pinch

    This file was automatically generated for Pinch by APIMATIC BETA v2.0 on 05/13/2016
"""
from Pinch.Models import *
from Pinch.Controllers import *
from Pinch.Decorators import *
from Pinch.APIException import *

class PinchClient(object):

    @lazy_property
    def webhook_type_controller(self):
        return WebhookTypeController()

    @lazy_property
    def webhook_controller(self):
        return WebhookController()

    @lazy_property
    def ticket_controller(self):
        return TicketController()



