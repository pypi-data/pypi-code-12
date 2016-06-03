# encoding: utf-8
"""
interfaces.py

Created by martinpeeters on 2011-08-24.
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from zope.component import Interface


class IInvalidateKey(Interface):
    """
    """


class IMemcachedDefaultNameSpace(Interface):
    """
    """

    def __str__():
        """
        return the current memcached default namespace
        """
