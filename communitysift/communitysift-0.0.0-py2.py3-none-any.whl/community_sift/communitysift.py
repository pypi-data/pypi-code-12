import os
import sys

from utils.constants import *
import requests
import json
import ConfigParser

parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PROJECT_CONFIG_FILE = os.path.join(parent_directory, 'config.txt')


class ConfigError(Exception):
    """ raised when a bad configuration file is found, and no reasonable
    workaround can be found """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def load_configurations(config_file):
    """
    This method is loading the config.txt and read the values of the file and return the basic_auth key,
    API base URL and API version
    :param config_file: absolute path of the configuration file is given here
    :return: API basic auth key, API Base URL and API version specified in the file
    """
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(config_file))
        headers_section = 'HTTP_Header_Params'
        url_params_section = 'HTTP_Url_Params'

        api_basic_auth_key = config.get(headers_section, 'api_basic_auth_key')
        api_base_url = config.get(url_params_section, 'api_base_url')
        api_version = config.get(url_params_section, 'api_version')

        return api_basic_auth_key, api_base_url, api_version

    except IOError:
        e = sys.exc_info()[0], sys.exc_info()[1]
        print e
        raise ConfigError("""
    Config file not found (%s)
    Make sure you have the config.txt file in the project root folder
    """ % config_file)


def create_session():
    """
    This method is used to generate a communitysift API session object along with the API endpint URL
    :return: Communitysift API session and API endpoint URL
    """
    communitysift_session = requests.Session()

    try:
        api_basic_auth_key, api_base_url, api_version = load_configurations(PROJECT_CONFIG_FILE)

        communitysift_session.auth = ('', api_basic_auth_key)
        communitysift_session.headers.update({CONTENT_TYPE: APPLICATION_JSON})

        endpoint_url = create_endpoint_url(api_base_url, api_version)
        return communitysift_session, endpoint_url

    except:
        print 'Session not created'


def create_endpoint_url(api_base_url, api_version):
    """
    This will create the Endpoint URL that will be called for CommunitySift features
    :param api_base_url: Base API URL
    :param api_version: API Version
    :return: This will construct the Endpoint URL similar to  https://twitter.pottymouthfilter.com/v1
    """
    return '{0}{1}{2}'.format(api_base_url, URL_SEPERATOR, api_version)


class CommunitySift (object):

    # Any Communitysift object will get a unique session and an endpoint URL
    def __init__(self):
        self.communitysift_session, self.endpoint_url = create_session()
        pass

    def create_input_for_chat_filter(self, chat_text, chat_room_id=None, language_code=None, rule_id=None,
                                     server_name=None, player=None, player_display_name=None):
        """
        This method creates a JSON object that can be sent as an input to the Chat filter endpoint
        :param chat_text: text that needs to be checked
        :param chat_room_id
        :param language_code
        :param rule_id
        :param server_name
        :param player
        :param player_display_name
        :return: JSON input for the chat filter endpoint
        """
        chat_input = {
            "room": chat_room_id or "Lobby",
            "language": language_code or "en",
            "text": chat_text,
            "rule": rule_id or 1,
            "server": server_name or "Gamma",
            "player": player or 3455643,
            "player_display_name": player_display_name or "Stinky Feet"
        }
        return chat_input

    def create_input_for_username_check(self, player_id, username, rule_num=None, language=None):
        """
        This method creates a JSON object that can be sent as an input to the Username validation endpoint
        :param player_id
        :param username: username that needs to be checked
        :param rule_num
        :param language
        :return: JSON input for the username validation endpoint
        """
        username_check_input = {
            "player_id": player_id,
            "username": username,
            "rule": rule_num or 1,
            "language": language or "en",
        }
        return username_check_input

    def process_input(self, command, input_data):
        """
        This method is to create input for the communitysift API based on the command and the input JSON
        given by the user
        :param command: whether this is the Filtering Chats or Username Validation
        :param input_data: input JSON object with arbitrary data
        :return: a valid input JSON object that is accepted by the Communitysift API
        """
        chat_room = language = server = player = player_display_name = player_id = username = rule_num = chat_text = None
        request_input = None
        if input_data.get('text'):
            chat_text = input_data['text']
        if input_data.get('room'):
            chat_room = input_data['room']
        if input_data.get('language'):
            language = input_data['language']
        if input_data.get('rule'):
            rule_num = input_data['rule']
        if input_data.get('server'):
            server = input_data['server']
        if input_data.get('player'):
            player = input_data['player']
        if input_data.get('player_display_name'):
            player_display_name = input_data['player_display_name']
        if input_data.get('player_id'):
            player_id = input_data['player_id']
        if input_data.get('username'):
            username = input_data['username']

        if command == FILTER_CHATS:
            request_input = self.create_input_for_chat_filter(chat_text, chat_room, language, rule_num, server, player,
                                                              player_display_name)
        elif command == USERNAME_VALIDATION:
            request_input = self.create_input_for_username_check(player_id, username, rule_num, language)
        else:
            print "No valid command given"
        return request_input

    def execute(self, command, input_data):
        """
        This method is the entry point to the CommunitySift methods. User can give different commands along with
        the required JSON objects as input data.
        :param command: the input command should be one of below:
            filterChats, userNameValidation
        :param input_data: a valid JSON input. Refer test_communitysift.python for sample JSON inputs
        :return: based on the command and the input, a True/False will be returned along with a JSON output of
            the API response
        """
        request_input = None
        endpoint_url = None

        if command == FILTER_CHATS:

            request_input = self.process_input(command, input_data)

            # Constructing a URL like  http://localhost:8080/v1/chat
            endpoint_url = '{0}{1}{2}'.format(self.endpoint_url, URL_SEPERATOR, CHAT)

        elif command == USERNAME_VALIDATION:
            request_input = self.process_input(command, input_data)

            # Constructing a URL like  http://localhost:8080/v1/username
            endpoint_url = '{0}{1}{2}'.format(self.endpoint_url, URL_SEPERATOR, USERNAME)

        else:
            print "No valid command given"

        communitysift_request = self.communitysift_session.post(endpoint_url, data=json.dumps(request_input))
        if communitysift_request.status_code == 200:
            response_data = communitysift_request.json()

            response = response_data["response"]
            return response, response_data
