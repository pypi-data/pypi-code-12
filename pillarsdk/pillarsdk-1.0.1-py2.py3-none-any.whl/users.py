import hashlib
import urllib
from .resource import List
from .resource import Find
from .resource import Create
from .resource import Post
from .resource import Update
from .resource import Delete


class User(List, Find, Create, Post, Update, Delete):
    """User class wrapping the REST nodes endpoint
    """
    path = "users"

    def gravatar(self, size=64):
        """Generate Gravatar link on the fly using the email value"""
        parameters = {'s':str(size), 'd':'mm'}
        return "https://www.gravatar.com/avatar/" + \
            hashlib.md5(self.email.lower()).hexdigest() + \
            "?" + urllib.urlencode(parameters)
