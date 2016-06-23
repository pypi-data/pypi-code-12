import requests
import math
import re

from dateutil.parser import parse

class MailLift():

    USERNAME = None
    API_KEY = None

    STATUSES = ('new', 'assigned', 'writing', 'pendingQcApproval', 'approved', 'inMail',
                'modifiedPendingRewriteSchedule', 'qcRejectedPendingRewrite', 'canceled')

    def __init__(self, username=None, api_key=None):
        """
        :param username: E-mail used to access https://maillift.com/
        :param api_key: API Key created https://maillift.com/dashboard -> API -> API Key
        :return None
        """

        if username and api_key:
            self.USERNAME = username
            self.API_KEY = api_key

        if not username and not api_key:
            raise MailLiftError('Please supply your username and api_key in order to use MailLift')
        elif not username:
            raise MailLiftError('Please supply your username in order to use MailLift')
        elif not api_key:
            raise MailLiftError('Please supply your API Key in order to use MailLift')

    def __is_configured__(self):
        if self.USERNAME and self.API_KEY:
            return True
        return False

    def __do_request__(self, method=None, url='https://maillift.maillift.com/2016-04-21/letter/', extras=None):

        if not self.__is_configured__():
            raise MailLiftError('MailLift was improperly configured.')

        if method == 'GET':
            response = requests.get(url=url, params=extras, auth=(self.USERNAME, self.API_KEY))
            if response.status_code == 200:
                if len(response.text):
                    return response.json()
                else:
                    return None
            else:
                raise MailLiftError('Couldn\'t list/get letter. Reason: {0}'.format(response.reason))

        elif method == 'POST':
            response = requests.post(url=url, data=extras, auth=(self.USERNAME, self.API_KEY))
            if response.status_code == 200:
                return Letter(response.json())
            else:
                raise MailLiftError('Couldn\'t create letter. Reason: {0}'.format(response.reason))

        elif method == 'PUT':
            response = requests.put(url=url, data=extras, auth=(self.USERNAME, self.API_KEY))
            if response.status_code == 200:
                return Letter(response.json())
            elif response.status_code == 403:
                return False
            else:
                raise MailLiftError('Couldn\'t update letter. Reason: {0}'.format(response.reason))

        elif method == 'DELETE':
            response = requests.delete(url=url, data=extras, auth=(self.USERNAME, self.API_KEY))
            if response.status_code == 200:
                return True
            elif response.status_code == 403:
                return False
            else:
                raise MailLiftError('Couldn\'t update letter. Reason: {0}'.format(response.reason))


    def check_price(self, text=None):
        """
        :param text: Content of letter
        :return: Float: Total that will be charged (Rounded up)
        """

        if text:
            content = text.strip()
            words = content.split()

            if len(words) <= 50:
                return 0
            else:
                total = (len(words) - 50) * 0.0249
                return math.ceil(total)
        return 0



    def create_letter(self, recipient, message, **options):
        """
        :param recipient: [REQUIRED] Name + Address combination
        :param message: [REQUIRED] Content to be written to letter
        :param options:
            'sender' : Name + Address combination
            'schedule': Date in the future following YYYY-MM-DD format
            'notes': Send additional information to the writer
        :return: Letter Object or None
        """

        data = dict()


        if not recipient and not message:
            raise MailLiftError('You need to supply a recipient and a message in order to create a letter.')
        elif not recipient:
            raise MailLiftError('You need to supply a recipient in order to create a letter')
        elif not message:
            raise MailLiftError('You need to supply a message in order to create a letter')

        data['Recipient'] = recipient
        data['MessageBody'] = message.strip()

        if options.get('sender', None):
            data['Sender'] = options['sender']
        if options.get('schedule', None):
            try:
                parse(options['schedule'])
            except ValueError:
                raise MailLiftError('Schedule parameter contains an invalid date format. Desired format is YYYY-MM-DD')

            data['ScheduledDelivery'] = options['schedule']
        if options.get('notes', None):
            data['Notes'] = options['notes']

        return self.__do_request__(method='POST', extras=data)


    def list_letters(self, **options):
        """
        :param options:
            'creation_date': Filter by date =YYYY-MM-DD | <=YYYY-MM-DD | >=YYYY-MM-DD | <=YYYY-MM-DD,>=YYYY-MM-DD
            'status': list only letters of the specified status
        :return: list of Letter Objects / Empty List
        """

        data = dict()

        if options.get('creation_date', None):
            try:
                filters = re.sub('[><=]', '', options['creation_date']).split(',')
                for filter in filters:
                    parse(filter)
            except ValueError:
                raise MailLiftError('CreationDate parameter contains an invalid date format. Desired format is YYYY-MM-DD')

            data['CreationDate'] = options['creation_date']
        if options.get('status', None):
            data['Status'] = options['status']

        letters = self.__do_request__(method='GET', url='https://maillift.maillift.com/2016-04-21/letter/?', extras=data)

        if letters:
            letters_list = list()
            for lt in letters:
                letters_list.append(Letter(lt))
            return letters_list

        return list()

    def get_letter(self, uuid=None):
        """
        :param uuid: Universal Unique identifier returned when creating a letter.
        :return: Letter Object or None
        """

        if not uuid:
            raise MailLiftError('An UUID is required in order to retrieve a Letter')

        letter = self.__do_request__(method='GET', url='https://maillift.maillift.com/2016-04-21/letter/{0}'.format(uuid))

        if letter:
            return Letter(letter)
        return None

    def modify_letter(self, uuid=None, message=None, delivery=None, **options):
        """
            :param uuid: [REQUIRED] Universal Unique identifier returned when creating a letter.
            :param message: New text for letter
            :param delivery;Date in the future for delivery
            :param options:
                'approval_required': if approval is required (True or False)
            :return: Letter Object or False
            """
        data = dict()

        if not uuid:
            raise MailLiftError('An UUID is required in order to modify a Letter')

        if options.get('approval_required', None):
            data['ApprovalRequired'] = 'true' if options['approval_required'] == True else 'false'
        if message:
            data['MessageBody'] = message
        if delivery:
            try:
                parse(delivery)
                data['ScheduledDelivery'] = delivery
            except ValueError:
                raise MailLiftError("Schedule parameter contains an invalid date format. Desired format is YYYY-MM-DD")

        letter = self.__do_request__(method='PUT', url='https://maillift.maillift.com/2016-04-21/letter/{0}'.format(uuid),
                                     extras=data)
        return letter

    def cancel_letter(self, uuid=None, note=None, letter=None):
        """
        :param uuid: [REQUIRED] Universal Unique identifier returned when creating a letter.
        :param note: Reason to why this note was canceled.
        :param letter: Letter Object. If object is supplied, it will avoid a live call to check its status
        :return: True if able to cancel, False it its past 'In Mail' status.
        """

        if not uuid:
            raise MailLiftError('An UUID is required in order to cancel a Letter')

        data = dict()

        if note:
            data['Notes'] = note


        # Check current status

        if not letter:
            letter = self.get_letter(uuid)

        if letter.Status in ['inMail', 'canceled']:
            return False

        response = self.__do_request__(method='DELETE', url='https://maillift.maillift.com/2016-04-21/letter/{0}'.format(uuid),
                                     extras=data)

        return response

    def letter_history(self, uuid=None):
        """
        :param uuid:
        :return: Array with statuses and updates for given letter
        """

        if not uuid:
            raise MailLiftError('An UUID is required in order to cancel a Letter')

        response = self.__do_request__(method='GET',
                                       url='https://maillift.maillift.com/2016-04-21/letter/status/{0}'.format(uuid))

        return response



class Letter():

    def __init__(self, data=None):
        self.ApprovalRequired = None
        self.MessageBody = None
        self.Owner = None
        self.Pictures = None
        self.Price = None
        self.Recipient = None
        self.ScheduledDelivery = None
        self.Sender = None
        self.Status = None
        self.Uuid = None

        if data:
            for key, value in data.iteritems():
                setattr(self, key, value)

    def __str__(self):
        return "[{0}] - {1}".format(self.Status, self.Uuid)

    def __repr__(self):
        return "[{0}] - {1}".format(self.Status, self.Uuid)



class MailLiftError(Exception):
    pass

