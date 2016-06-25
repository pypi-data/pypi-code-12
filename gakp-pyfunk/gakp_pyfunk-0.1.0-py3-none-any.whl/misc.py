import pyfunk.combinators as _


def fid(a):
    '''fid :: a -> a'''
    return a


@_.curry
def trace(tag, val):
    '''trace :: Show a => String -> a -> a'''
    print(tag, val)
    return val


def T(*args):
    '''
    Always returns true
    @sig T :: _ -> Bool
    '''
    return True


def F(*args):
    '''
    Always returns false
    @sig F :: _ -> Bool
    '''
    return False
