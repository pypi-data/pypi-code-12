# -*- coding: utf-8 -*-
# Time-stamp: < aop.py (2016-02-13 22:30) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Provides basic *AOP* functionality.

:py:class:`AbstractMethodAdvice` provides base class for advices (before,
after, around advice).  Subclass :py:class:`AroundMethodAdvice` to
implement around advice by overriding
:py:meth:`AroundMethodAdvice.__call__` to provide desired behaviour before
and/or after the call.

Intended implementation of AOP is through method decorators.  Support for
such an implementation is provided in :py:class:`Proxy`, ie. proxy class
can intercept calls and can implement special actions before/after/around a
call while accessing target object's methods (or attributes).

See :py:mod:`summer.txaop` and :py:mod:`summer.lxaop` modules for
implementation of transactional and ldap session proxy with accompanying
advice and decorator.

"""

import inspect
import logging
import types

from . import ass
from .utils import Printable

logger = logging.getLogger(__name__)


class AbstractMethodAdvice(Printable):

    """Base class for method advice.

    If one wants to use the advice (ie. apply an aspect), the trick is to
    use the proxy class, that adds another layer of indirection.

    Proxy delegates access to all the attributes to the target object.  If
    the attribute is not decorated, proxy will accesses the attribute
    directly, if not, proxy will invoke and advice before and/or after
    accessing the attribute (usually method call).

    Current implementation supports the creation of an advice in the proxy
    object by searching for a decoration -- if the attribute (method) is
    decorated by particular decorator, new attribute with the same name is
    created on the proxy instance (of the type
    :py:class`AbstractMethodAdvice`) and it gets called instead, doing
    anything the aspect requires (doing some stuff and than delegating the
    call to target object).

    """

    def __init__(self, method: types.MethodType):
        """
        Args:
            method (types.MethodType): method to be adviced
        """
        self.method = method
        # method's full name
        self.mame = "%s.%s" % (self.method.__self__.__class__.__name__,
                               self.method.__name__)

    def before(self, *args, **kwargs) -> object:
        """Called *before* actual method invocation takes place.

        Any arguments provided are forwarded to proxy.

        Returns:

            object: whatever the target returns.
        """
        pass

    def after(self, *args, **kwargs) -> object:
        """Called *after* actual method invocation takes place.

        Any arguments provided are forwarded to proxy.

        Returns:

            object: whatever the target returns.
        """
        pass

    def around(self, *args, **kwargs) -> object:
        """Called *around* actual method invocation.  Probably most usefull kind of
        advice; sure the most powerful.

        Any arguments provided are forwarded to proxy.

        Returns:

            object: whatever the target returns.
        """
        pass

    def __call__(self, *args, **kwargs) -> object:
        """This should delegate the call to :py:meth:`before`, :py:meth:`after` or
        :py:meth:`around` method.  Implemented in subclasses.

        Any arguments provided are forwarded to proxy.

        Returns:

            object: whatever the target returns.

        """
        pass

    def __str__(self):
        tmp = "%s [mame: %s]" % (self.__class__.__name__, self.mame)
        return tmp


class AroundMethodAdvice(AbstractMethodAdvice):

    """Around method advice."""

    def __init__(self, method: types.MethodType):
        AbstractMethodAdvice.__init__(self, method)

    def __call__(self, *args, **kwargs) -> object:
        """Delegates method call to :py:meth:`AbstractMethodAdvice.around`
        method.

        Any arguments provided are forwarded to proxy.

        Returns:

            object: whatever the target returns.

        """
        return self.around(*args, **kwargs)


class Proxy(object):

    """Generic proxy object proxies the target's method calls by applying an
    *advice* -- and so implementing an *aspect*.

    """

    def __init__(self, target: object):
        """
        Args:

            target (object): object to be peroxied.
        """
        ass.is_not_none(target)
        self.target = target

    def __getattr__(self, name: str) -> object:
        """Delegates the attribute access to itself and than to target object if
        not found.

        Proxied (adviced) attributes (:py:class:`AbstractMethodAdvice`
        instances) has the same name as their decorated counterparts in the
        target object.  In such a case, they gets called instead of the
        target object methods.

        Args:

            name (str): attribute name to return.

        Returns:

            object: Any value store in attribute.

        """
        if name in self.__dict__:
            logger.debug("accessing proxied attr '%s'", name)
            return self.__dict__[name]
        else:
            logger.debug("accessing non-proxied attr '%s'", name)
            return getattr(self.target, name)

    def _get_decorated_methods(self, decorator_name: str) -> list:
        """Gets methods decorated by ``decorator_name`` in the ``self.target``.
        Decorated methods can be proxied.

        It is very handy to implement aspects using decorators -- with just
        a method decoration one can mark that method for the proxy as a
        target method for applying an advice -- and so implementing an
        aspect.  This method seres as a helper to decide which methods of
        the target object should be adviced.

        Args:

            decorator_name (str): name of the decorator to look for.

        Returns:

            list: List of method objects decorated by decorator.

        """
        methods = list()
        member_names = dir(self.target)
        for name in member_names:
            attr = getattr(self.target, name)
            if inspect.ismethod(attr) and getattr(attr, decorator_name, False):
                methods.append(attr)
        logger.debug("methods decorated with '%s': %s",
                     decorator_name, [i.__name__ for i in methods])
        return methods
