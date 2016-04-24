"""Module abstracting a Parature action. Transforms a Parature Gmail message
into the 'action' the client took.
"""


from paraturegmailfeed.paratureaction.message import ParatureGmailMessage
from paraturegmailfeed.paratureaction.parser import ParatureTextParser


class ParatureAction(object):
    """
    """
    parser = ParatureTextParser

    def __init__(self, gmail_message):
        message = ParatureGmailMessage(gmail_message)

        self.timestamp = message.timestamp
        self.ticket_number = self.parser.get_ticket_number(message.body)
        self.csr_name = self.parser.get_csr_name(message.body)
        self.action_type = self.parser.get_action_type(message.subject)
        self.assigned_from = self.parser.get_assigned_from(message.body)


    def to_dict(self):
        return {
            'actionType': self.action_type,
            'assignedTo': self.csr_name,
            'assignedFrom': self.assigned_from,
            'ticketNumber': self.ticket_number,
            'timestamp': self.timestamp
        }
