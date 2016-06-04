class Monadic(object):
    """
    Classes that inherit from Monadic should implement behavior that respects
    the monad laws (though it is not necessary they be actual monads).

    Classes that inherit from Monadic should implement a map and join method,
    that respect these laws. Unit and zero class methods should also be defined
    to provide uniform access, where applicable to the corresponding sub-types.
    The implementation should also define a product arity.
    """
    product_arity = None

    def map(self, map_func):
        raise NotImplementedError

    def join(self):
        raise NotImplementedError

    def bind(self, bind_func):
        """
        Map a function to the inner value and join the result.

        :param bind_func: The function to bind to the inner value.
        :type bind_func: T -> U
        :return: The bound and joined inner value, if present.
        """
        return self.map(bind_func).join()

    @classmethod
    def unit(cls, _):
        raise NotImplementedError

    @classmethod
    def zero(cls):
        raise NotImplementedError


class InnerValueNotContainerTypeException(Exception):
    pass


class NoSuchElementException(IndexError):
    pass

