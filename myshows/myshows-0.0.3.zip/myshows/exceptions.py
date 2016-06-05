class MyShowsException(Exception):
    pass

class MyShowsAuthentificationFailedException(MyShowsException):
    pass

class MyShowsAuthentificationRequiredException(MyShowsException):
    pass

class MyShowsInvalidParametersException(MyShowsException):
    pass
