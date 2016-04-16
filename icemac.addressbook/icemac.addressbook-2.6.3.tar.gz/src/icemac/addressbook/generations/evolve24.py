# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.generations.utils
import zope.catalog
import zope.component


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Update indexes due to a bug in update search result handler.

    """
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    catalog.updateIndexes()
