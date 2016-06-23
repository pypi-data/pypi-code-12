"""user.py contains basic information about the steno3d user"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import properties


class User(properties.PropertyClass):
    """Class representing a user instance"""
    _model_api_location = "user"
    email = properties.String('email')
    name = properties.String('name')
    url = properties.String('url')
    affiliation = properties.String('affiliation')
    location = properties.String('location')
