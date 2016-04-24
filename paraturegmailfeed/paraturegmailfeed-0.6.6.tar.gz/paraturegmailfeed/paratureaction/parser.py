"""Module containing methods to match/extract strings of pertintent data from
text."""


import re

from paraturegmailfeed.exceptions import MatchNotFound


class ParatureTextParser(object):
    """Class containing methods to parse/extract data from an email from Parature"""
    @staticmethod
    def get_ticket_number(body):
        """Returns int representing ticket number"""
        ticket_number_regex = '(?:Ticket Number:</b> )(.*?)(?:</p>)'

        match = re.search(ticket_number_regex, body)
        if match:
            ticket_number = int(match.group(1))
        else:
            raise MatchNotFound('ticket_number_regex did not return any matches!')

        return ticket_number

    @staticmethod
    def get_csr_name(body):
        """Returns str representing assigned CSR's name"""
        csr_name_regex = '(?:Assigned:</b> )(.*?)(?:</p>)'

        match = re.search(csr_name_regex, body)
        if match:
            csr_name = match.group(1)
        else:
            raise MatchNotFound('csr_name_regex did not return any matches!')

        return csr_name.strip()

    @staticmethod
    def get_action_type(subject):
        """Returns str representing the action type of the email"""
        action_type_regex = '(?:#3870-[0-9]{7}: )([a-zA-Z1-4 ]*)(?: \()'

        match = re.search(action_type_regex, subject)
        if match:
            action_type = match.group(1)
        else:
            raise MatchNotFound('action_type_regex did not return any matches!')

        return action_type.strip()

    @staticmethod
    def get_assigned_from(body):
        """Returns str representing the CSR whom assigned the ticket someone else"""
        assigned_from_regex = '(?:assigned the following ticket by )([a-zA-Z ]*)(?:\.)'

        match = re.search(assigned_from_regex, body)
        if match:
            assigned_from = match.group(1)
        else:
            assigned_from = ''
        return assigned_from
