from pyfunk import combinators as _
from pyfunk.misc import T
from functools import reduce


def __map_object(obj, fn):
    def reducer(newObj, key):
        newObj[key] = fn(obj[key])
        return newObj
    return reduce(reducer, obj.keys(), {})


def __filter_object(obj, fn):
    def reducer(newObj, key):
        if fn(obj[key]):
            newObj[key] = obj[key]
        return newObj
    return reduce(reducer, obj.keys(), {})


@_.curry
def fmap(fn, f):
    '''
    Generic function for dealing with functors(arrays, maybe).
    @sig map :: Functor f => (a -> b) -> f a -> f b
    '''
    if hasattr(f, 'fmap'):
        return f.fmap(fn)
    elif hasattr(f, 'keys'):
        return __map_object(f, fn)
    else:
        return list(map(fn, f))


@_.curry
def fslice(x, y, arr):
    '''
    Composable equivalent of [:]. Use None for the second argument
    for the equivalent [x:]
    @sig slice :: (Number, Number) -> [a] -> [a]
    '''
    return arr[x:y]


@_.curry
def ffilter(fn, f):
    '''
    Composable equivalent of iterable filter function.
    @sig filter :: (a -> Bool) -> [a] -> [a]
    '''
    if hasattr(f, 'keys'):
        return __filter_object(f, fn)
    else:
        return list(filter(fn, f))


@_.curry
def prop(str, obj):
    '''
    Property access as a function
    @sig prop :: String -> Dict -> a
    '''
    return obj.get(str)


@_.curry
def concat(c1, c2):
    '''
    Equivalent of + for concatables(string, array)
    @sig concat :: Concatable c => c a -> Number -> c a
    '''
    return c1 + c2


@_.curry
def index_of(fn, arr):
    '''
    Find the index of first element that passes given.
    @sig index_of :: (a -> Bool) -> [a] -> Number
    '''
    for i in range(len(arr)):
        if fn(arr[i]):
            return i
    return -1


@_.curry
def array_get(i, arr):
    '''
    Array access as a function.
    @sig array_get :: [a] -> Number -> a
    '''
    try:
        return arr[i]
    except IndexError:
        return None


@_.curry
def first(fn, arr):
    '''
    Get the first element that passes the test.
    @sig first :: (a -> Bool) -> [a] -> a
    '''
    return array_get(index_of(fn, arr), arr)


# head :: [a] -> a'''
head = first(T)


@_.curry
def take_while(fn, arr):
    '''
    Retrieve the first set of elements that pass the given test.
    @sig take_while :: (a -> Bool) -> [a] -> [a]
    '''
    i = index_of(_.fnot(fn), arr)
    i = 0 if i == -1 else i
    return fslice(0, i, arr)


@_.curry
def drop_while(fn, arr):
    '''
    Slice array starting from the element that fails the given test.
    @sig drop_while :: (a -> Bool) -> [a] -> [a]
    '''
    i = index_of(_.fnot(fn), arr)
    i = len(arr) if i == -1 else i
    return fslice(i, None, arr)
