# -*- coding: utf-8 -*-
# Time-stamp: < domain.py (2016-02-14 00:38) >

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

"""Basic support for domain classes, including persistent domain classes.

"""

from .utils import Printable


class Domain(Printable):

    """Suitable class for generic domain objects."""

    def __init__(self):
        Printable.__init__(self)


class Filter(Domain):

    """Base class for *filters* -- ie. classes that support paging through a
    collection.  Used for example in :py:meth:`summer.dao.EntityDao.find`

    * :py:attr:`page` sets the page of the result set, starting at 1
      (ie. first page)
    * :py:attr:`max_results` sets the page limit (entities per page)

    Use :py:meth:`Filter.get_offset` to obtain the first record of the
    result set.  Use :py:meth:`Filter.get_max_results` to obtain the last
    record of the result set.

    """

    def __init__(self, page: int = 1, max_results: int = -1):
        """
        Args:

            page (int): page in collection

            max_results (int) results per page
        """
        Domain.__init__(self)
        self.page = page
        self.max_results = max_results

    @staticmethod
    def get_default():
        """
        Returns:

            Filter: default filter instance, set for single page without
            limit per page (will show all the results)

        """
        tmp = Filter(1, -1)
        return tmp

    def get_offset(self) -> int:
        """Computes the order of the first record, ie. the *offset*.

        Returns:

            int: offset
        """
        tmp = (self.page - 1) * self.max_results
        if tmp < 0:
            return 0
        return tmp

    def get_max_results(self) -> int:
        """Computes the order of the potential last record, ie. the *max_results*.

        Returns:

            int: maximum number of results per page

        """
        return self.max_results

    def copy_limits(self, other):
        """Copy the :py:attr:`page` and :py:attr:`max_results` to ``self``.

        Args:

            other (Filter): filter object to be copied
        """
        self.page = other.page
        self.max_results = other.max_results


class Entity(Domain):

    """Suitable base class for *SQLAlchemy* persistent classes; defines the
    integer :py:attr:`id` attribute.

    """

    def __init__(self):
        Domain.__init__(self)
        self.id = None

    def __eq__(self, other):
        """Equality is based on the :py:attr:`id` attribute."""
        if self is other:
            return True
        if isinstance(other, self.__class__) \
                and self.id is not None \
                and self.id == other.id:
            return True
        return False

    def __hash__(self):
        """Hash is based on the :py:attr:`id` attribute."""
        if self.id is None:
            return hash(id(self))
        return hash(self.id)

    def __str__(self):
        tmp = "%s [id: %s]" % (self.__class__.__name__, self.id)
        return tmp


class CodeEntity(Entity):

    """Suitable base class for *SQLAlchemy* persistent classes that have a
    unique string code attribute (ie. usually catalogs).  This
    :py:attr:`code` attribute should be considered as a string
    representation of an object, its natural id, not necessarily human
    friendly value.

    """

    def __init__(self):
        Entity.__init__(self)
        self.code = None

    def __str__(self):
        tmp = "%s [id: %s, code: %s]" % \
              (self.__class__.__name__, self.id, self.code)
        return tmp


class LdapEntity(Domain):

    """Suiable base class for LDAP persistent classes.  Defines the unique
    string :py:attr:`dn` attribute.

    """

    def __init__(self):
        Domain.__init__(self)
        self.dn = None

    def __eq__(self, other):
        """Equality is based on the :py:attr:`dn` attribute."""
        if self is other:
            return True
        if isinstance(other, self.__class__) \
                and self.dn is not None \
                and self.dn == other.dn:
            return True
        return False

    def __hash__(self):
        """Hash is based on the :py:attr:`dn` attribute."""
        if self.dn is None:
            return hash(id(self))
        return hash(self.dn)

    def __str__(self):
        tmp = "%s [dn: %s]" % (self.__class__.__name__, self.dn)
        return tmp
