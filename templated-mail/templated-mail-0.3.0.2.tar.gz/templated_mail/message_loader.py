
import os
import functools

import jinja2
import simple_configparser

from templated_mail.sub_template_loader import SubTemplateLoader
from templated_mail.message import Message


class MessageLoader(object):

    """
    A "loader" (though not a Jinja2 subclass) for
    finding files ending in '.msg' in `config.MESSAGE_DIR`.

    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.search_path = config.MESSAGE_DIR
        self.message_class = functools.partial(Message, jinja2.Environment(
            # Pass the MESSAGE_DIR to sub-template loader
            # so it can find templates for inheritance
            loader=SubTemplateLoader(
                config.MESSAGE_DIR
            )
        ))

    def get_message(self, name):
        """

        :param name: Takes the name of a message in config.MESSAGE_DIR,
                     without the '.msg' extension.
        :return:     The corresponding Message if it could be found,
                     otherwise None.
        """

        # open explicitly, because the config parser
        # will be silent about not finding a file
        with open(os.path.join(self.search_path, '{}.msg'.format(name))) as f:
            parser = simple_configparser.SimpleConfigParser()
            parser.read_file(f)
            return self.message_class(parser.items())

