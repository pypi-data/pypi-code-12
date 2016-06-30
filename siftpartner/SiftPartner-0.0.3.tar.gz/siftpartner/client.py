import json
import requests
import sys

import siftpartner
from . import version
from . import response

API_URL = "https://partner.siftscience.com/v%s" % version.API_VERSION
API_TIMEOUT = 2


class Client(object):
    def __init__(self, api_key=None, partner_id=None):
        """ Initialize the client

        :param api_key: Your Sift Science Partner API key associated with your
                partner account. This can be found at
                https://siftscience.com//console/api-keys
        :param partner_id: Your partner account id, which can be found at
                https://siftscience.com/console/settings
        """

        if sys.version_info.major < 3:
          self.UNICODE_STRING = basestring
        else:
          self.UNICODE_STRING = str

        # set api key to module scoped key if not specified
        if api_key is None:
            api_key = siftpartner.api_key

        # set partner id to module scoped key if not specified
        if partner_id is None:
            partner_id = siftpartner.partner_id

        self.validate_argument(api_key, 'API key', self.UNICODE_STRING)

        self.validate_argument(partner_id, 'Partner ID', self.UNICODE_STRING)

        self.api_key = api_key
        self.partner_id = partner_id

    @staticmethod
    def user_agent():
        return 'SiftScience/v%s sift-partner-python/%s' % (version.API_VERSION,
                                                           version.VERSION)

    def accounts_url(self):
        return API_URL + "/partners/%s/accounts" % self.partner_id

    def notifications_config_url(self):
        return API_URL + "/accounts/%s/config" % self.partner_id

    def validate_argument(self, argument, name, arg_type):
        if not isinstance(argument, arg_type) or (
               isinstance(argument, self.UNICODE_STRING)
               and len(argument.strip()) == 0
        ):
            raise RuntimeError(name + " must be a " + str(arg_type))

    def new_account(self, site_url, site_email, analyst_email, password):
        """ Creates a new merchant account

        :param site_url: the url of the merchant site

        :param site_email: an email address for the merchant

        :param analyst_email: an email address which will be used to log in
               at the Sift Console

        :param password: password (at least 10 chars) to be used to sign into
               the Console

        :return:When successful, returns a dict including the new account id
                and credentials.
                When an error occurs, The exception is raised.
        """
        self.validate_argument(site_url, 'Site url', self.UNICODE_STRING)
        self.validate_argument(site_email, 'Site email', self.UNICODE_STRING)
        self.validate_argument(analyst_email, 'Analyst email',
                               self.UNICODE_STRING)
        self.validate_argument(password, 'Password', self.UNICODE_STRING)

        properties = {'site_url': site_url,
                      'site_email': site_email,
                      'analyst_email': analyst_email,
                      'password': password
        }

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        params = {}
        try:
            res = requests.post(self.accounts_url(),
                                data=json.dumps(properties),
                                headers=headers,
                                timeout=API_TIMEOUT,
                                params=params
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e

    def get_accounts(self, next_ref = None):
        """Gets a listing of the ids and keys for merchant accounts that
           have been created by this partner. Results limited to 100 accounts
           per request.

        :return: When successful, returns a dict including the key data, which
                 is an array of account descriptions. (Each element has the
                 same structure as a single response from new_account). If
                 has_more is true, pass the value of next_ref back into this
                 function to get the next set of results.

                 When an error occurs, an exception is raised.
        """
        headers = {'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        try:
            res = requests.get(self.accounts_url() if not next_ref else next_ref,
                               headers=headers,
                               timeout=API_TIMEOUT
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e

    def update_notification_config(
       self,
       notification_url = None,
       notification_threshold = None
    ):
        """ Updates the configuration which controls http notifications for
            all merchant accounts under this partner.

        :param notification_url: A String which determines the url to which
               the POST notifications go,containing the string '%s' exactly
               once.  This allows the url to beused as a template, into which a
               merchant account id can be substituted.

        :param notification_threshold: A floating point number between 0.0 and
               1.0, determining the score threshold at which to push
               notifications.  It represents the Sift Score/100

        :return: When successful, a dict is returned containing the new
                 notification configuration.

                 When an error occurs, an exception is raised.

        DEPRECATED USE:
            notification_url may also be a Hash, with keys
            http_notification_url and http_notification_threshold.
            The value of the notification_url will be a url containing the
            string '%s' exactly once.  This allows the url to be used as a
            template, into which a merchant account id can be substituted.
            The  notification threshold should be a floating point number
            between 0.0 and 1.0
        """
        properties = {}
        # This is for backwards compatibility....DEPRECATED
        if isinstance(notification_url, dict):
            properties = notification_url

        # This is for support of the new way of doing things
        else:

            # for each of the parameters, only set them if they are not None
            if notification_url is not None:
                self.validate_argument(notification_url,
                                       'Notification url',
                                       self.UNICODE_STRING
                )
                properties['http_notification_url'] = notification_url

            if notification_threshold is not None:
                self.validate_argument(notification_threshold,
                                   'Notification threshold',
                                   float
                )
                properties['http_notification_threshold'] = notification_threshold


        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        try:
            res = requests.put(self.notifications_config_url(),
                               data=json.dumps(properties),
                               headers=headers,
                               timeout=API_TIMEOUT
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e










