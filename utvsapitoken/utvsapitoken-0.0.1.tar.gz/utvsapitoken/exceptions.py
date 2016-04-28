class TokenError(BaseException):
    '''General exception about token'''
    pass


class TokenInvalid(TokenError):
    '''Exception indicating a token is invalid'''
    pass


class TokenExpired(TokenError):
    '''Exception indicating a token is expired'''
    pass


class UsermapError(TokenError):
    '''Exception indicating something bad happened in usermap'''
    pass
