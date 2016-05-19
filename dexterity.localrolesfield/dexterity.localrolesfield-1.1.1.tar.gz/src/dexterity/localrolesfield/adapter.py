# encoding: utf-8
from zope.component import getUtility, ComponentLookupError
from zope.interface import implements

from plone.dexterity.interfaces import IDexterityFTI

from Products.CMFPlone.utils import base_hasattr
from borg.localrole.interfaces import ILocalRoleProvider

from dexterity.localroles.utils import get_state

from .utils import get_localrole_fields


class LocalRoleFieldAdapter(object):
    implements(ILocalRoleProvider)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal):
        """Grant permission for principal"""
        roles = []
        for field, value in self.field_and_values_list:
            config = self.get_config(field).get(self.current_state)
            if not config:
                continue
            suffixes = self._get_suffixes_for_principal(config, value,
                                                        principal)
            for suffix in suffixes:
                roles.extend(config.get(suffix)['roles'])

        return tuple(roles)

    def _get_suffixes_for_principal(self, config, value, principal):
        """Return the suffixes that match the given principal"""
        suffixes_principals = [(suffix, self._format_principal(value, suffix))
                               for suffix in config.keys()]
        return [s for s, p in suffixes_principals if p == principal]

    def getAllRoles(self):
        """Grant permissions"""
        for field, value in self.field_and_values_list:
            state_config = self.get_config(field).get(self.current_state)
            if not state_config:
                continue
            for suffix, roles_dic in state_config.items():
                yield (self._format_principal(value, suffix), tuple(roles_dic['roles']))

    @staticmethod
    def _format_suffix(suffix):
        if not suffix:
            return u''
        return u'_{0}'.format(suffix)

    def _format_principal(self, principal, suffix):
        return u'{0}{1}'.format(principal, self._format_suffix(suffix))

    @property
    def field_and_values_list(self):
        """Return the id and the values of the LocalRolesField objects on the
        current context"""
        fields = get_localrole_fields(self.fti)
        field_and_values = []
        for fieldname, _field in fields:
            if not base_hasattr(self.context, fieldname):
                continue
            values = getattr(self.context, fieldname) or []
            if not isinstance(values, list):
                values = [values]

            for value in values:
                field_and_values.append((fieldname, value))

        return field_and_values

    @property
    def fti(self):
        """Return the FTI"""
        try:
            return getUtility(IDexterityFTI, name=self.context.portal_type)
        except ComponentLookupError:
            # on site delete
            return None

    def get_config(self, fieldname):
        """Return the config from FTI for a given fieldname"""
        if not base_hasattr(self.fti, 'localroles'):
            return {}
        return self.fti.localroles.get(fieldname, {})

    @property
    def current_state(self):
        """Return the state of the current object"""
        return get_state(self.context)
