from functools import wraps

from cloak import IS_PY2
from cloak.immutable import Immutable
from cloak.monadic import Monadic, InnerValueNotContainerTypeException, NoSuchElementException


def _reverse_func_arity_two(func):
    return wraps(func)(lambda x, y: func(y, x))


class Option(Monadic, Immutable):
    """
    Option is the abstract type that both Some and Nothing (which is a singleton with the instance bound to nil),
    inherit from. It should both respect the monad laws, as well as be immutable.
    """
    product_arity = 1

    @classmethod
    def unit(cls, value):
        """
        Create a new option unit container from a specified value.

        :param value: The inner value for the resulting Option.
        :type value: T
        :return: The inner value in cloak.option.Option's unit container, cloak.option.Some.
        :rtype: Some[T]
        """
        return Some(value)

    @classmethod
    def zero(cls):
        """
        Access the zero element for the cloak.option.Option type, cloak.option.nil

        :return: nil
        :rtype: cloak.option.Nothing
        """
        return nil

    @property
    def is_empty(self):
        """
        is_empty must be defined by the corresponding subtype, and is True if the container is nil, and False
        if the container is Some

        :return: True if nil, False if Some.
        :rtype: bool
        """
        raise NotImplementedError

    @property
    def is_defined(self):
        """
        is_defined must be defined by the corresponding subtype, and is False if the container is nil, and True
        if the container is Some

        :return: False if nil, True if Some.
        :rtype: bool
        """
        return not self.is_empty

    def get(self):
        """
        Extract and return the inner value if the option is Some, else throw NoSuchElementException if nil.

        :return: The inner value if present, else raise NoSuchElementException
        """
        raise NotImplementedError

    def get_or_else(self, else_value):
        """
        Extract and return the inner value if the option is Some, or return else_value if this is nil.

        :param else_value: The value to return if the option is nil/Nothing.
        :return: The inner value if present, else else_value
        """
        raise NotImplementedError

    def or_else(self, alternative_callable, *args, **kwargs):
        """
        Return the current option if the option is Some, else call alternative_callable and return its result if
        the option is nil/Nothing.

        :param alternative_callable: A function to call and get a result from if the option is nil.
        :type alternative_callable: function | method
        :param args: Positional arguments to be passed to alternative_callable.
        :param kwargs: Keyword arguments to be passed to alternative_callable.
        :return: The current option object itself, if it's Some, else the result of calling alternative_callable with
            the specified arguments if the current option is nil/Nothing.
        """
        raise NotImplementedError

    def exists(self, predicate_callable):
        """
        If the current option is Some, this method results the result of predicate_callable called with the inner
        value as its only argument cast to bool.

        If the current option is nil/Nothing, this method always returns False, and predicate_callable is never
        evaluated.

        :param predicate_callable: A function that evaluates if an inner value exists that satisfies its embodied
            predicate
        :type predicate_callable: T -> bool
        :return: True if an element exists that satisfies the predicate, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError

    def filter(self, filter_callable):
        """
        If the current option is Some, this method returns the current Option object if filter_callable returns a value
        that converts to True when evaluated with the inner value. If the result is False, the Nothing singleton nil
        is returned.

        If the current option is nil/Nothing, the current option object (which is the same as nil), is always returned
        and filter_callable is not evaluated.

        :param filter_callable: A function which is evaluated on the inner value, if present.
        :type filter_callable: T -> bool
        :return: The current object if it has an inner value (i.e. not nil), and the evaluation of filter_callable
            is truthy. Otherwise returns nil.
        :rtype: cloak.option.Option
        """
        raise NotImplementedError

    def flatten(self):
        """
        Flatten is similar to join, with an additional check made that InnerValueNotContainerTypeException will be
        thrown if the inner value exists, but does not inherit from cloak.option.Option.

        :return: The extracted option, if applicable.
        :rtype: Option[T]
        """
        raise NotImplementedError

    def map(self, map_func):
        """
        Apply the map_func to the inner value, if it exists, and return a new Option with the result of the computation.
        If the Option is nil, map_func is not called, and nil is returned.

        :param map_func: An arity one function to apply to the inner value, if it exists. The computation will be
            returned in a new Option.
        :type map_func: T -> S
        :return: A Some container with the computation result, if the original option was not nil/Nothing. Otherwise
            nil is returned.
        :rtype: Option[S]
        """
        raise NotImplementedError

    def join(self):
        """
        Extract the inner value from option if it has one, otherwise return nil.

        :return: The inner value or nil if the origin object is nil.
        :rtype: T | Nothing
        """
        raise NotImplementedError


class Some(Option):
    """
    Some[T] is the unit subtype for Option. It denotes the presence of an inner value.
    """
    def __init__(self, value):
        self._value = value
        super(Option, self).__init__()

    def __repr__(self):
        return "Some({0})".format(repr(self._value))

    def __str__(self):
        return "Some({0})".format(repr(self._value))

    def __eq__(self, other):
        return isinstance(other, Some) and self._value == other.get()

    def __ne__(self, other):
        return not self.__eq__(other)

    def map(self, map_func):
        """
        Apply a computation to the inner value, and return the result in a new Option.

        :param map_func: The arity one computation function to apply to the inner value.
        :type map_func: T -> S
        :return: A new option contained the result of the applied computation.
        :rtype: Option[S]
        """
        return self.__class__(map_func(self._value))

    def flatten(self):
        """
        Extract the inner value, if it's an Option subclass. If the inner value is not an instance of Option,
        InnerValueNotContainerTypeException is raised.

        :return: The inner value, if it's an Option subtype.
        :rtype: T
        """
        if not isinstance(self._value, Option):
            raise InnerValueNotContainerTypeException("Can't flatten if inner type is not an Option[T] type!")
        return self._value

    @property
    def is_empty(self):
        """
        is_empty is always False for the Some Option subtype. This signifies the inner value is not empty.

        :return: False
        :rtype: bool
        """
        return False

    @property
    def is_defined(self):
        """
        is_defined is always True for the Some Option subtype. This signifies that the inner value is defined.

        :return: True
        :rtype: bool
        """
        return True

    def get(self):
        """
        Extract and return the inner value.

        :return: The inner value.
        :rtype: T
        """
        return self._value

    def join(self):
        """
        Extract and return the inner value.

        :return: The inner value.
        :rtype: T
        """
        return self._value

    def get_or_else(self, _):
        """
        Extract and return the inner value.

        :param _: The value that would have been returned if this Option were nil.
        :type _: S
        :return: The inner value.
        :rtype: T
        """
        return self._value

    def or_else(self, alternative_callable, *args, **kwargs):
        """
        Return the current Some object.

        :param alternative_callable: The callable function that would have been called if this Option were nil.
        :type alternative_callable: S -> U
        :param args: Positional arguments to the alternative_callable.
        :param kwargs: Keyword arguments to the alternative_callable.
        :return: The current object (self)
        :rtype: Some[T]
        """
        return self

    def exists(self, predicate_callable):
        """
        Check to see if the inner value satisfies the predicate_callable, by calling it with the inner value
        and returning the result of this computation converted to a boolean.

        :param predicate_callable: This function take the inner value as its only argument and it's return value
           is converted to bool and returned from this method. This is intended to allow the programmer to determine
           if the inner value exists, and satisfies an arbitrary criterion embedded in the predicate_callable.
        :type predicate_callable: T -> bool
        :return: True if the result of predicate_callable can be converted to True, False otherwise.
        :rtype: bool
        """
        return bool(predicate_callable(self._value))

    def filter(self, filter_callable):
        """
        Check to see if the inner value satisfies the filter_callable, by calling it with the inner value
        and returning the result of this computation converted to a boolean. If True, the current option is returned,
        if False the nil Option is returned.

        :param filter_callable: This function take the inner value as its only argument and is used to determine if
           the current Some option is returned or nil. If filter_callable evaluates to False, nil is returned, if True
           the current Some Option is returned
        :type filter_callable: T -> bool
        :return: The current option object is filter_callable evaluates to True, otherwise nil
        :rtype: Option
        """
        return self if filter_callable(self._value) else nil

    def for_each(self, apply_callable):
        """
        Run a side-effecting callable on the inner value. This is pretty much syntatic sugar over the bind method.

        :param apply_callable: The callable to execute with the inner value as its only argument.
        :type apply_callable: T -> Any
        :return: None
        :rtype: NoneType
        """

        apply_callable(self._value)


class Nothing(Option):
    """
    Nothing[T] is the zero subtype for Option. It denotes the absence of a contained inner value.

    Nothing exists as a singleton, called nil.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Nothing, cls).__new__(cls)
        return cls._instance

    def __init__(self, _):
        super(Option, self).__init__()

    def __repr__(self):
        return "nil"

    def __str__(self):
        return "nil"

    def map(self, _):
        """
        Return nil, because there was no inner value for the function to operate on.

        :param _: The map callable that would have operated on the inner value.
        :type _: T -> S
        :return: nil
        :rtype: Nothing
        """
        return nil

    def flatten(self):
        """
        Return nil, because there was no inner value to flatten.

        :return: nil
        :rtype: Nothing
        """
        return nil

    @property
    def is_empty(self):
        """
        is_empty is always True for the Nothing/nil Option subtype. This signifies the inner value is empty.

        :return: True
        :rtype: bool
        """
        return True

    @property
    def is_defined(self):
        """
        is_defined is always False for the Nothing/nil Option subtype. This signifies the inner value is empty.

        :return: False
        :rtype: bool
        """
        return False

    def get(self):
        """
        Raise NoSuchElementException, because there was no inner value to extract.

        :return: Does not return. Raises NoSuchElementException.
        """
        raise NoSuchElementException

    def join(self):
        """
        Return nil, because there was no inner value to join on.

        :return: nil
        :rtype: Nothing
        """
        return nil

    def get_or_else(self, else_value):
        """
        Return the alternative value, because there was no inner value to return.

        :param else_value: The alternative value to return.
        :type else_value: T
        :return: else_value
        :rtype: T
        """
        return else_value

    def or_else(self, alternative_callable, *args, **kwargs):
        """
        Call and return an alternative callable, because the Option is empty (hence or_else).

        :param alternative_callable: The function or method to call, whose result will be returned.
        :tyep alternative_callable: S -> U
        :param args: Positional arguments to the alternative callable.
        :param kwargs: Keyword arguments to the alternative callable.
        :return: The result of calling alternative_callable.
        :rtype: U
        """
        return alternative_callable(*args, **kwargs)

    def exists(self, _):
        """
        Return False, because there was no inner value to check if the callable returns true for.

        :param _: The callable that would have been evaluated on the inner value to return some truthiness, if
           an inner value was present. This never gets called when the Option is nil.
        :type _: T -> bool
        :return: False
        :rtype: bool
        """
        return False

    def filter(self, _):
        """
        Return nil, because there was no inner value to check if the callable returns true for.

        :param _: The callable that would have been evaluated on the inner value to return some truthiness to filter
            the option if an inner value was present. This never gets called when the Option is nil.
        :type _: T -> bool
        :return: nil
        :rtype: Nothing
        """
        return nil

    def for_each(self, _):
        """
        Because the Option is nil, this method is a noop.

        :param _: The side-effecting callable that would have been evaluated on the inner value, if it were present.
        :type _: T -> S
        :return: None
        :rtype: NoneType
        """
        pass

nil = Nothing(None)


def lift_option_functor(function):
    """
    Lift a function to seamlessly operate on and return Options.
    After a function has been decorated by this functor, if any of the arguments passed
    to the function on later invocations are nil, the function call is skipped, and nil is
    returned. All instances of Some passed to the function as arguments are joined, and the inner value extracted
    to be passed as the argument in place of its parent Option; any arguments that do not inherit from
    Option as passed unchanged. If none of the arguments are nil, the result will be returned wrapped in a Some
    container.

    :param function: The function to decorate.
    :type function: T -> S
    :return: The lifted function, with correct Option handling installed.
    :rtype: T -> Option[S]
    """
    def extract_argument_values(args):
        return (arg.get() if isinstance(arg, Some) else arg for arg in args)

    def extract_keyword_args(kwargs):
        if IS_PY2:
            return {key: value.get() if isinstance(value, Some) else value for key, value in kwargs.iteritems()}
        else:
            return {key: value.get() if isinstance(value, Some) else value for key, value in kwargs.items()}

    @wraps(function)
    def wrapped(*args, **kwargs):
        if IS_PY2:
            if nil in args or nil in kwargs.itervalues():
                return nil
            else:
                return Some(function(*extract_argument_values(args), **extract_keyword_args(kwargs)))
        else:
            if nil in args or nil in kwargs.values():
                return nil
            else:
                return Some(function(*extract_argument_values(args), **extract_keyword_args(kwargs)))
    return wrapped


def lift_exception_to_option_functor(function, target_exceptions):
    """
    Lift a function to return nil if one of a set of target exceptions is raised,
    or otherwise return the result inside a new Option (Some) container.

    This is especially useful for converting code that originally relied on exceptions
    for flow control into using options, and leaving exceptions for abnormalities only.
    An especially poignant example of this is the get() method on Queue-like objects in
    Python. Under normal circumstances, the only way to check and fetch results without
    introducing race conditions is to use a try/except Empty/else clause over the method,
    each providing a different code path depending on if the queue had a message or not.
    By decorating the get method with this functor, and setting the target_exceptions to
    the set containing the Empty exception, the get() function will the message fetched
    from the queue wrapped in a Some container if an object was present, and nil if
    nothing was waiting the queue; further operation on the retrieved object can simply
    be mapped onto the resultant Option.

    :param function: The function to decorate.
    :type function: T -> S
    :param target_exceptions: The set of exceptions to convert into nil instead of re-raising.
    :type target_exceptions: set[BaseException] | list[BaseException] | tuple[BaseException]
    :return: The decorated function.
    :rtype: T -> Option[S]
    """
    target_exceptions = tuple(target_exceptions)

    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return Some(function(*args, **kwargs))
        except target_exceptions as _:
            return nil
    return wrapped