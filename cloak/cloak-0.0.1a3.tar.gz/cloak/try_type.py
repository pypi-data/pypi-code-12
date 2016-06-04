import sys
from functools import wraps
from itertools import chain

from cloak import IS_PY2
from cloak.immutable import Immutable
from cloak.monadic import Monadic, NoSuchElementException
from cloak.option import Some, nil


class TryFilterException(Exception):
    pass


class TryFailureDefaultException(Exception):
    pass


class Try(Monadic, Immutable):
    """
    The Try type is used to contain computations and has a unit and zero subtype (Success and Failure) depending on
    if the computation succeeded, and returned a result, or if it failed, and raised an exception.
    """

    product_arity = 1

    @classmethod
    def unit(cls, value):
        """
        Build an instance of the Try unit subtype, Success, with the give value.

        :param value: The value to wrap inside the Success instance.
        :type value: T
        :return: The given value wrapped in a Success instance.
        :rtype: Success[T]
        """
        return Success(value)

    @classmethod
    def zero(cls, exception=None):
        """
        Build an instance of the Try zero subtype, Failure, optionally with a given exception instance.

        :param exception: OPTIONAL: The exception to wrap in the Failure instance.
            Default: None -> A new TryFailureDefaultException instance.
        :type exception: BaseException | NoneType
        :return: The given exception wrapped in a Failure instance.
        :rtype: Failure[BaseException]
        """
        return Failure(TryFailureDefaultException() if exception is None else exception)

    @classmethod
    def apply(cls, func, *args, **kwargs):
        """
        Wrap the specified computation in a Try object. If the call returns a result successfully, it will be
        wrapped in a Success object, otherwise the raised exception will be returned in a Failure object.

        :param func: The callable to wrap in a Try object.
        :type func: S -> U
        :param args: The positional arguments to the wrapped callable.
        :param kwargs: The keyword arguments to the wrapped callable.
        :return: The result of the callable wrapped in a Success object, if no exception was raised. Otherwise, the
            raised Exception is wrapped in a Failure instance.
        :rtype: Try
        """
        try:
            return Success(func(*args, **kwargs))
        except:
            return Failure(sys.exc_info()[1])

    @property
    def is_failure(self):
        """
        is_failure should always return True if the instance is a Failure object, and False is the instance is a
        Success object.

        :return: True for Failure, False for Success.
        :rtype: bool
        """
        raise NotImplementedError

    @property
    def is_success(self):
        """
        is_success should always return True if the instance is a Success object, and False is the instance is a
        Failure object.

        :return: True for Success, False for Failure.
        :rtype: bool
        """
        raise NotImplementedError

    def filter(self, filter_callable, throw_on_false=TryFilterException):
        """
        This method takes a predicate embedded in a callable, called filter_callable. If the Try object is the
        Success subtype, the filter_callable is evaluated on the inner value. If it evaluates to False (or can be
        converted to False), the method returns a new Failure instance, with the exception set by the throw_on_false
        parameter, which defaults to TryFilterException. If the subtype is Failure, the Try object is returned
        unchanged.

        :param filter_callable: The predicate embedded in an arity 1 callable to evaluate on the inner value, if
            present, to determine if the result should be converted to a Failure or returned as Success. If the current
            Try object is a Failure, this is never evaluated.
        :type filter_callable: T -> bool
        :param throw_on_false: OPTIONAL: The exception class to be instantiated in the exception attribute of the Failure
            object, if the filter callable evaluates to False when called for a success object.
        :type throw_on_false: BaseException
        :return: If the Try subtype is Success, the current Success object is returned if the callable evaluates True,
           a new Failure object is returned otherwise. If the current Try subtype is Failure, the current Failure is
           always returned regardless.
        :rtype: Try[T]
        """
        raise NotImplementedError

    def or_else(self, func, *args, **kwargs):
        """
        This method allows a callable function to be evaluated and returned in the case that the Try subtype of the
        current object is Failure. If the subtype is Success, the current object is returned unmodified.

        :param func: The function to evaluate in the case the current Try is a Failure.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The result of the function call.
        :rtype:  Success[T] | U
        """
        raise NotImplementedError

    def or_else_with(self, func, *args, **kwargs):
        """
        This method allows a callable function to be evaluated and returned wrapped in a new Try in the case that the
        Try subtype of the current object is Failure. If the subtype is Success, the current object is returned
        unmodified. This is very similar to or_else, with the exception that the function is run through the apply
        method to generate a new Try, so that the user may seamlessly use unlifted functions to generate a new
        Try in the event of failure.

        :param func: The function to evaluate in the case the current Try is a Failure.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The result of calling Try.apply with the function call and its arguments.
        :rtype: Success[T] | Success[U] | Failure
        """
        raise NotImplementedError

    def to_option(self):
        """
        Convert the current Try object to the Option container type. If the Try subtype is success, a Some object is
        created with the Try result stored as the Some object's inner value. If the current Try subtype is Failure,
        nil is returned.

        :return: A new Option object. Some for Success, nil for Failure.
        :rtype: cloak.option.Option
        """
        raise NotImplementedError

    def map(self, map_func):
        """
        Apply a map function to the inner value of a Success object, and return the result of the computation in a new
        Success object. If the computation throws an exception a new Failure object will be returned wrapping the
        exception. If the original Try object was a Failure, return it unchanged.

        :param map_func: The computation to apply to the inner value if this is a Success object.
        :type map_func: T -> U
        :return: The result of the mapped inner value, wrapped in a new Try (with a Success object being returned if
            the computation succeeded, and a Failure object being returned if the map function threw an exception).
            If the original Try was a Failure, it is returned unmodified.
        :rtype: Success[U] | Failure
        """
        raise NotImplementedError

    def join(self):
        """
        Either extract (join) the inner value, and return it, if the object is a Success object and has an inner value,
        or return the current object if it is a Failure object.

        :return: The extracted inner value, if this is a Success object, otherwise return the current Failure object
            unchanged.
        :rtype: T | Failure
        """
        raise NotImplementedError

    def get(self):
        """
        Either extract the inner value, and return it, if the object is a Success object and has an inner value,
        or raise a NoSuchElementException if the current object is a Failure object.

        :return: The extracted inner value, if this is a Success object, otherwise raise a NoSuchElementException.
        :rtype: T
        """

        raise NotImplementedError

    def get_or_else(self, alternative_value):
        """
        Either extract the inner value, and return it, if the object is a Success object and has an inner value,
        or return the alternative value provided.

        :param alternative_value: The alternative value, returned if the object is a Failure subtype.
        :type alternative_value: U
        :return: The extracted inner value, if this is a Success object, otherwise return the alternative value.
        :rtype: T | U
        """
        raise NotImplementedError

    def transform(self, on_success, on_failure):
        """
        Transform the current Try instance, with paths provided both in the case of the object being a Success and
        being a Failure.

        :param on_success: An arity 1 callable to transform the the inner value, much as map would.
            This is run via Try.apply, it can generate either a new Success or Failure depending on if the on_success
            callable raises or not.
        :type on_success: T -> U
        :param on_failure: An arity 1 callable object to transform a Failure. The one parameter fed into this
            function is the exception parameter of the failure. This function is run via Try.apply, thus may generate
            either a new Success or Failure depending on if it raises or not.
        :type on_failure: BaseException: -> U
        :return: The extracted inner value, if this is a Success object, otherwise return the alternative value.
        :rtype: Try[U]
        """
        raise NotImplementedError

    def recover(self, *recover_tuples):
        """
        This method allows the user to specify a set of ordered tuples to determine a recovery path for a Failure
        object. Each tuple consists of an exception class and an arity one callable to be executed on the exeception
        instance and the result returned in a new Try, if the Failure's exception instance is found to be an instance
        of the given exception class. The first matching pair is executed, and the result is returned in a new Try,
        via Try.apply. If no match is found, the Failure is returned unchanged. For Success objects, the Success object
        is always returned unchanged.

        :param recover_tuples: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the Exception class to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found.
        :type recover_tuples: (BaseException, BaseException -> T)
        :return: A new Try object if a match is found, and the recovery callable executed, and the object is a Failure.
            If the object is a Failure, and no match is found, the Failure is returned unmodified. If the object is a
            Success, the object is returned unmodified.
        :rtype: Try
        """
        raise NotImplementedError

    def recover_if(self, *recover_if_tuples):
        """
        This method allows the user to specify a set of ordered tuples to determine a recovery path for a Failure
        object. Each tuple consists of an arity one predicate callable and an arity one callable to be executed on
        the exeception instance and the result to be returned in a new try, if the predicate is found to evaluate to
        True when given the Failure's exception. The first matching pair is executed, and the result is returned
        in a new Try, via Try.apply. If no match is found, the Failure is returned unchanged. For Success objects,
        the Success object is always returned unchanged.

        This is different from recover in that recover_if allows the user to specify an arbitrary predicate callable
        to evaluate, rather than matching directly on the exception class.

        :param recover_if_tuples: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the predicate callable to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found.
        :type recover_if_tuples: (BaseException -> bool, BaseException -> T)
        :return: A new Try object if a match is found, and the recovery callable executed, and the object is a Failure.
            If the object is a Failure, and no match is found, the Failure is returned unmodified. If the object is a
            Success, the object is returned unmodified.
        :rtype: Try
        """
        raise NotImplementedError


class Success(Try):
    """
    The Success type embodies a successful computation, and contains the result of the computation. This is the unit
    subtype for Try.
    """
    def __init__(self, result):
        self._result = result

    def __repr__(self):
        return "Success({0})".format(repr(self._result))

    def __str__(self):
        return "Success({0})".format(repr(self._result))

    def __eq__(self, other):
        return isinstance(other, Success) and self._result == other.get()

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def is_failure(self):
        """
        is_failure is always False for Success, as it is by definition not a failure.

        :return: False
        :rtype: bool
        """
        return False

    @property
    def is_success(self):
        """
        is_success is always True for Success, as it is by definition a success.

        :return: True
        :rtype: bool
        """
        return True

    def or_else(self, func, *args, **kwargs):
        """
        For Success this is a noop, and returns the current Success object.

        :param func: The function to evaluate in the case the current Try is a Failure.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The current Success object.
        :rtype:  Success[T]
        """
        return self

    def or_else_with(self, func, *args, **kwargs):
        """
        For Success this is a noop, and returns the current Success object.

        :param func: The function to evaluate in the case the current Try is a Failure.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The current Success object.
        :rtype:  Success[T]
        """
        return self

    def to_option(self):
        """
        Convert this Success object into a cloak.option.Some object.

        :return: A new Some (Option) object holding the computation result.
        :rtype: cloak.option.Some
        """
        return Some(self._result)

    def map(self, map_func):
        """
        Map the result of the computation into a new Try. A new Success object with the result of the computation is
        returned if map_func does not raise, otherwise a new Failure is returned with the exception embedded.

        :param map_func: A callable to execute on the inner value and to return the results from.
        :type map_func: T -> U
        :return: A new Success object if the computation succeeded, otherwise a new Failure object is generated.
        :rtype: Try
        """
        return self.apply(map_func, self._result)

    def filter(self, filter_callable, throw_on_false=TryFilterException):
        """
        This method takes a predicate embedded in a callable, called filter_callable. The filter_callable is evaluated
        on the inner value. If it evaluates to False (or can be converted to False), the method returns a new
        Failure instance, with the exception set by the throw_on_false parameter, which defaults to TryFilterException.

        :param filter_callable: The predicate embedded in an arity 1 callable to evaluate on the inner value, if
            present, to determine if the result should be converted to a Failure or returned as Success. If the current
            Try object is a Failure, this is never evaluated.
        :type filter_callable: T -> bool
        :param throw_on_false: OPTIONAL: The exception class to be instantiated in the exception attribute of the Failure
            object, if the filter callable evaluates to False when called for a success object.
        :type throw_on_false: BaseException
        :return: If the Try subtype is Success, the current Success object is returned if the callable evaluates True,
           a new Failure object is returned otherwise. If the current Try subtype is Failure, the current Failure is
           always returned regardless.
        :rtype: Try[T]
        """
        if filter_callable(self._result):
            return self
        else:
            return Failure(TryFilterException())

    def join(self):
        """
        Extract (join) the inner value and return it from the method call.

        :return: The inner value.
        :rtype: T
        """
        return self._result

    def get(self):
        """
        Extract the inner value and return it from the method call.

        :return: The inner value.
        :rtype: T
        """
        return self._result

    def get_or_else(self, _):
        """
        Extract the inner value and return it from the method call.

        :param _: The alternative value that would have been returned if this was a Failure object.
        :type _: U
        :return: The inner value.
        :rtype: T
        """
        return self._result

    def transform(self, on_success, on_failure):
        """
        Transform the current Success instance; this is equivalent to calling map with on_success being the argument.

        :param on_success: An arity 1 callable to transform the the inner value, much as map would.
            This is run via Try.apply, it can generate either a new Success or Failure depending on if the on_success
            callable raises or not.
        :type on_success: T -> U
        :param on_failure: An arity 1 callable object to transform a Failure. The one parameter fed into this
            function is the exception parameter of the failure. This function is run via Try.apply, thus may generate
            either a new Success or Failure depending on if it raises or not.
        :type on_failure: BaseException: -> U
        :return: The extracted inner value, if this is a Success object, otherwise return the alternative value.
        :rtype: Try[U]
        """
        return self.apply(on_success, self._result)

    def recover(self, *_):
        """
        For Success, this returns the current Success object unchanged.

        :param _: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the Exception class to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found. These only get used for
            Failure objects.
        :type _: (BaseException, BaseException -> T)
        :return: The unmodified Success object
        :rtype: Success
        """
        return self

    def recover_if(self, *_):
        """
        For Success, this returns the current Success object unchanged.

        :param _: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the predicate callable to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found. These only get used for
            Failure objects.
        :type _: (BaseException -> bool, BaseException -> T)
        :return: The unmodified Success object
        :rtype: Success
        """
        return self


class Failure(Try):
    """
    The Failure type embodies a failed computation, and contains the exception thrown as the exception attribute.
    This type also provides a nested_exceptions attribute in order to coalesce Failure instances without loosing
    information about all of the exceptions thrown.
    """
    def __init__(self, exception=None, nested_exceptions=()):
        self.exception = TryFailureDefaultException() if exception is None else exception
        self.nested_exceptions = nested_exceptions

    def __repr__(self):
        return "Failure({0})".format(repr(self.exception))

    def __str__(self):
        return "Failure({0})".format(repr(self.exception))

    def __eq__(self, other):
        return isinstance(other, Failure) and self.exception == other.exception

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def is_failure(self):
        """
        is_failure is always True for Failure, as it is by definition a failure.

        :return: True
        :rtype: bool
        """
        return True

    @property
    def is_success(self):
        """
        is_success is always False for Failure, as it is by definition not a success.

        :return: False
        :rtype: bool
        """
        return False

    def or_else(self, func, *args, **kwargs):
        """
        This method executes the given callable function with the specified arguments, and returns
        the result.

        :param func: The function to evaluate.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The result of the function call.
        :rtype: U
        """
        return func(*args, **kwargs)

    def or_else_with(self, func, *args, **kwargs):
        """
        This method wraps the callable function to be evaluated in a new Try via Try.apply.
        This is very similar to or_else, with the exception that the function is run through the apply
        method to generate a new Try, so that the user may seamlessly use unlifted functions to generate a new
        Try in the event of failure.

        :param func: The function to evaluate.
        :type func: S -> U
        :param args: The positional arguments for the function to be evaluated.
        :param kwargs: The keyword arguments for the function to be evaluated.
        :return: The result of calling Try.apply with the function call and its arguments.
        :rtype: Success[U] | Failure
        """
        return self.apply(func, *args, **kwargs)

    def to_option(self):
        """
        Convert this Failure object into cloak.option.nil.

        :return: nil.
        :rtype: cloak.option.Nothing
        """
        return nil

    def map(self, _):
        """
        This method does nothing for a Failure object; the Failure is returned unchanged.

        :param _: The function that would have been applied to the inner value if this were a Success object.
        :type _: T -> U
        :return: The unmodified Failure.
        :rtype: Failure
        """
        return self

    def filter(self, filter_callable, throw_on_false=TryFilterException):
        """
        This method does nothing for a Failure object; the Failure is returned unchanged.

        :param filter_callable: If this were a Success object, this would have been evaluated against the inner value
            to determine if the current Success object were return, or if a new Failure was to be generated.
        :type filter_callable: T -> bool
        :param throw_on_false: OPTIONAL: If this were a Success object, this would have been the default exception
            class to put into the new Failure object in the case that the filter function evaluated to False.
        :type throw_on_false: BaseException
        :return: The unmodified Failure.
        :rtype: Failure
        """
        return self

    def join(self):
        """
        Return the current Failure object unchanged.

        :return: The Failure object unchanged.
        :rtype: Failure
        """
        return self

    def get(self):
        """
        Raise a NoSuchElementException as no inner value is present to get.

        :return: A NoSuchElementException is raised.
        """
        raise NoSuchElementException

    def get_or_else(self, else_value):
        """
        Return the alternative value provided.

        :param else_value: The alternative value to be returned by this method call.
        :type else_value: U
        :return: The alternative value.
        :rtype: U
        """
        return else_value

    def transform(self, on_success, on_failure):
        """
        Transform the current Failure instance, with the results on on_failure being returned in a new Try.

        :param on_success: An arity 1 callable to transform the the inner value, much as map would.
            This is run via Try.apply, it can generate either a new Success or Failure depending on if the on_success
            callable raises or not.
        :type on_success: T -> U
        :param on_failure: An arity 1 callable object to transform a Failure. The one parameter fed into this
            function is the exception parameter of the failure. This function is run via Try.apply, thus may generate
            either a new Success or Failure depending on if it raises or not.
        :type on_failure: BaseException: -> U
        :return: The extracted inner value, if this is a Success object, otherwise return the alternative value.
        :rtype: Try[U]
        """
        return self.apply(on_failure, self.exception)

    def recover(self, *recover_tuples):
        """
        This method allows the user to specify a set of ordered tuples to determine a recovery path for a Failure
        object. Each tuple consists of an exception class and an arity one callable to be executed on the exeception
        instance and the result returned in a new Try, if the Failure's exception instance is found to be an instance
        of the given exception class. The first matching pair is executed, and the result is returned in a new Try,
        via Try.apply. If no match is found, the Failure is returned unchanged.

        :param recover_tuples: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the Exception class to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found.
        :type recover_tuples: (BaseException, BaseException -> T)
        :return: A new Try object if a match is found, and the recovery callable executed, and the object is a Failure.
            If the object is a Failure, and no match is found, the Failure is returned unmodified. If the object is a
            Success, the object is returned unmodified.
        :rtype: Try
        """
        for exception_type, recover_func in recover_tuples:
            if isinstance(self.exception, exception_type):
                return self.apply(recover_func, self.exception)
        return self

    def recover_if(self, *recover_if_tuples):
        """
        This method allows the user to specify a set of ordered tuples to determine a recovery path for a Failure
        object. Each tuple consists of an arity one predicate callable and an arity one callable to be executed on
        the exeception instance and the result to be returned in a new try, if the predicate is found to evaluate to
        True when given the Failure's exception. The first matching pair is executed, and the result is returned
        in a new Try, via Try.apply. If no match is found, the Failure is returned unchanged.

        This is different from recover in that recover_if allows the user to specify an arbitrary predicate callable
        to evaluate, rather than matching directly on the exception class.

        :param recover_if_tuples: Length 2 tuples ordered in matching preference (with the first to match given first
            in the arguments), with the first item in the tuple being the predicate callable to match, the second being
            the arity 1 callable to execution on the Failure's exception if a match is found.
        :type recover_if_tuples: (BaseException -> bool, BaseException -> T)
        :return: A new Try object if a match is found, and the recovery callable executed, and the object is a Failure.
            If the object is a Failure, and no match is found, the Failure is returned unmodified. If the object is a
            Success, the object is returned unmodified.
        :rtype: Try
        """
        for praedicate_func, recover_func in recover_if_tuples:
            if praedicate_func(self.exception):
                return self.apply(recover_func, self.exception)
        return self


def lift_try_functor(function):
    """
    This functor lifts another function to deal with Try/Success/Failure seamlessly. If any of the argumments are
    a Failure instance, the first Failure instance is returned, with the exception data from all other failures
    loaded into the first Failure's nested_exceptions attribute, and the computation is skipped. If there are no
    Failure instances in the arguments, all instances of Success will be replaced with their inner values where
    they were used as arguments, and all other arguments will be passed unchanged. The function will be called via
    Try.apply, and a Success or Failure instance will be returned, based on if the function succeeded in returning a
    result, or raised an exception while running.

    :param function: The function to lift.
    :type function: T -> S
    :return: The lifted function.
    :rtype: T -> Try[S]
    """
    def check_failure(obj):
        return isinstance(obj, Failure)

    def unroll_exceptions(failures):
        for failure in failures:
            yield failure.exception
            for exception in failure.nested_exceptions:
                yield exception

    def extract_argument_values(args):
        return (arg.get() if isinstance(arg, Success) else arg for arg in args)

    def extract_keyword_args(kwargs):
        if IS_PY2:
            return {key: value.get() if isinstance(value, Success) else value for key, value in kwargs.iteritems()}
        else:
            return {key: value.get() if isinstance(value, Success) else value for key, value in kwargs.items()}

    @wraps(function)
    def wrapped(*args, **kwargs):
        args_failures = tuple(filter(check_failure, args))
        if IS_PY2:
            kwargs_failures = tuple(filter(check_failure, kwargs.itervalues()))
        else:
            kwargs_failures = tuple(filter(check_failure, kwargs.values()))
        if args_failures or kwargs_failures:
            all_failures = chain(args_failures, kwargs_failures)
            if IS_PY2:
                first_failure = all_failures.next()
            else:
                first_failure = all_failures.__next__()
            remaining_exceptions = tuple(chain(first_failure.nested_exceptions, unroll_exceptions(all_failures)))
            return Failure(exception=first_failure.exception, nested_exceptions=remaining_exceptions)
        else:
            return Try.apply(function, *extract_argument_values(args), **extract_keyword_args(kwargs))
    return wrapped
