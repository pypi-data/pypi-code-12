# -*- coding: utf-8 -*-
# Time-stamp: < __init__.py (2016-02-14 09:48) >

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

"""Summer is light weight python framework to support some common tasks in
variety of applications.  It tries to assist you with:

* Managing objects that implement your business logic.

* Using SQL transactions by simply decorating methods as `@transactional`.

* Using LDAP sessions by simply decorating methods as `@ldapaop`.

* Using gettext for localization.

* Loading configuration properties using `configparser.SafeConfigParser`.

With summer you can:

* Create and configure your stateless objects and deploy them into a simple
  container to be ready for any later use.

* Declaratively create transaction proxies or programmatically manage
  transactions.

* Declaratively create ldap proxies or programmatically manage ldap sessions.

* Get gettext l10n configured fast and ready to use.

* Access configuration files with portability in mind.

Reasons to name it summer:

* I wrote it in winter.

* You may know Java based *spring* framework, which was my inspiration.

Summer's top level module simply imports public API classes and methods
into `summer` namespace.

"""

__version__ = "0.6.0"
__date__ = "2016-01-31"

from summer.aop import (
    AbstractMethodAdvice,
    AroundMethodAdvice,
    Proxy,
)

from summer.context import Context

from summer.dao import (
    Dao,
    EntityDao,
    CodeEntityDao,
    DaoException,
)

from summer.domain import (
    Domain,
    Filter,
    Entity,
    CodeEntity,
    LdapEntity,
)

from summer.ex import (
    ApplicationException,
    AbstractMethodException,
    UnsupportedMethodException,
    NotImplementedException,
    UnknownAttributeException,
    IllegalArgumentException,
    ResourceNotFoundException,
    SummerException,
)


from summer.ldapdao import (
    LdapDao,
    LdapEntityDao,
)

from summer.lsf import LdapSessionFactory

from summer.lx import LdapWrapper, LdapCallback

from summer.lxaop import ldapaop, LdapProxy

from summer.pc import (
    Producer,
    Consumer,
    ProducerConsumer,
)

from summer.pcg import (
    ProducerWithGenerator,
    ProducerConsumerWithGenerator,
)

from summer.sf import (
    SessionFactory,
    AbstractTableDefinitions,
    AbstractClassMappings,
)

from summer.tx import TransactionWrapper, TransactionCallback

from summer.txaop import transactional, TransactionProxy

from summer.utils import (
    locate_file,
    chunks,
    Printable,
    FileReader,
    ThreadSafeCounter,
    IdGenerator,
)
