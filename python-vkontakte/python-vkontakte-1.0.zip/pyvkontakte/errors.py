class VkontakteError(Exception): pass


class VkontakteApiError(VkontakteError):
    """
    Raised in VkontakteApi.call method if api error occured.

    :type json: dict
    """

    def __init__(self, json):
        """
        :param dict json:
        """
        self.json = json['error']

    def __str__(self):
        return '[{0[error_code]}] {0[error_msg]} '.format(self.json)


class VkontakteAuthError(VkontakteError):
    pass


class InvalidCredentials(VkontakteAuthError):
    pass


class ParsingError(VkontakteAuthError):
    pass
