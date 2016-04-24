# feed.py
"""Module containing feed.
"""


import logging
import os

from gmailresthandler import GmailRestHandler

from paraturegmailfeed.config import Config
from paraturegmailfeed.mongodao import MongoDao
from paraturegmailfeed.paratureaction import ParatureAction

# LOG_CONFIG['level'] = logging.DEBUG
# logging.basicConfig(**LOG_CONFIG)


class ParatureGmailFeed(object):
    """The ParatureGmailFeed implements a feed that fetches messages from
    the Gmail API, transforms the messages, parses them for pertintent data,
    and loads them into a MongoDB database.
    """

    # The class that is used to load configuration
    config_class = Config

    root_path = os.getcwd()
    db = None

    def __init__(self, config_filepath):
        self.config = self.config_class(self.root_path)
        self.config.from_pyfile(config_filepath)
        self.gmail_handler = GmailRestHandler(config_filepath)
        self.db = MongoDao(self.config['MONGO_URI'], self.config['DB_NAME'])

    def run(self):
        """Run the feed"""
        user_id = self.config['USER_ID']
        target_label = self.config['TARGET_LABEL_QUERY']

        # Fetch list of messages ids
        message_list = self.gmail_handler.list_messages_matching_query(user_id, target_label)
        message_ids = [msg['id'] for msg in message_list]

        for msg_id in message_ids:
            gmail_message = self.gmail_handler.get_message(user_id, msg_id)

            try:
                action = ParatureAction(gmail_message)
            except Exception:
                print "Exception caught when processing: \n{}".format(gmail_message)
            else:
                self.db.save('action', action.to_dict())

                # Modify message (apply 'Processed' label)
                label_modifier_query = {
                    'removeLabelIds': ['Label_14'],
                    'addLabelIds': ['Label_13']
                }
                # Remove label and replace with another
                self.gmail_handler.modify_message(user_id, msg_id, label_modifier_query)
