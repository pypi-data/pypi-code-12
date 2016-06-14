__all__ = [
    'OAuthToken',
]


class OAuthToken(object):
    """OAuth credentials base-class. Several implementations are available:

    this class:
      provides crawler what is require to authenticate against sources
      via OAuth.
    """
    def __init__(self, **kwargs):
        self.__access_token = kwargs.get('access_token')
        self.__refresh_token = kwargs.get('refresh_token')
        self.__token_secret = kwargs.get('token_secret')
        self.__consumer_key = kwargs.get('consumer_key')
        self.__consumer_secret = kwargs.get('consumer_secret')
        self.__expires = kwargs.get('expires')

    access_token = property(
        fget=lambda slf: slf.__access_token,
        doc='''Read-only property accessor over the
        OAuth granted access token used by Docido to gain access
        to the protected resources on behalf of the user, instead
        of using the user's service provider credentials.

        :rtype: string
        '''
    )

    refresh_token = property(
        fget=lambda slf: slf.__refresh_token,
        doc='''Read-only property accessor over the
        OAuth refresh token used to recreate the access token.

        :rtype: string
        '''
    )

    token_secret = property(
        fget=lambda slf: slf.__token_secret,
        doc='''Read-only property accessor over the
        secret token provided by a service when retrieving an OAuth token.
        This property is set only when required provided by the authentication
        mechanism of the crawled service and required by crawler to fetch data.

        :rtype: string
        '''
    )

    consumer_key = property(
        fget=lambda slf: slf.__consumer_key,
        doc='''Read-only property accessor over the
        Docido consumer key. This property is set when required by
        the crawler to fetch data.

        :rtype: string
        '''
    )

    consumer_secret = property(
        fget=lambda slf: slf.__consumer_secret,
        doc='''Read-only property accessor over the
        Docido consumer secret. This property is set when required by
        the crawler to fetch data.

        :rtype: string
        '''
    )

    expires = property(
        fget=lambda slf: slf.__expires,
        doc='''Read-only property accessor over the expires field provided
        by authentication mechanism of the crawled service when token was
        acquired.

        :rtype: string
        '''
    )
