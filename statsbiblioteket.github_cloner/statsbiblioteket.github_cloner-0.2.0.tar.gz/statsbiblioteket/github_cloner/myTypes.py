import enum

Url = str
Path = str


class Repository(object):
    """
    The repository definition for the github cloner.
    It has just three fields, name, description, url
    """

    def __init__(self, name: str, description: str, url: Url):
        """
        The repository definition for the github cloner.

        :param name: the name of the repository
        :param description:  the description from github
        :param url: the url to clone/fetch from
        """
        self.name = name
        self.description = description
        self.url = url


class UserType(enum.Enum):
    """The enum for the types of github users, 'users' and 'orgs' """
    USER = 'users'
    ORG = 'orgs'


class RepoType(enum.Enum):
    """Github have two kind of repos, real repos 'repos' and weird repos
    'gists'"""
    REPO = 'repos'
    GIST = 'gists'
