# encoding: utf-8
from zope import schema
from zope.interface import implementer

from dexterity.localrolesfield.interfaces import ILocalRoleField, ILocalRolesField


@implementer(ILocalRolesField)
class LocalRolesField(schema.List):

    """Multi value local role field."""


@implementer(ILocalRoleField)
class LocalRoleField(schema.Choice):

    """Single value local role field."""
