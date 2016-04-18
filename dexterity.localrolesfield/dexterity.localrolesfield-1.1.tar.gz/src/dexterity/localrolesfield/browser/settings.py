# encoding: utf-8
from collective.z3cform.datagridfield import DictRow
from z3c.form import field, validator
from zope.interface import Interface
from zope.schema import Choice
from zope.schema import Text, TextLine
from dexterity.localroles import _ as LRMF

from dexterity.localroles.browser.settings import LocalRoleConfigurationForm, LocalRoleConfigurationPage
from dexterity.localroles.browser.settings import LocalRoleList, RelatedFormatValidator, Role
from dexterity.localroles.browser.settings import WorkflowState
from dexterity.localroles.vocabulary import plone_role_generator

from dexterity.localrolesfield.utils import get_localrole_fields
from dexterity.localrolesfield import _


class ILocalRoleConfig(Interface):
    state = WorkflowState(title=LRMF(u'state'), required=True)

    value = TextLine(title=_(u'suffix'), required=False, default=u'')

    roles = Role(title=LRMF(u'roles'),
                 value_type=Choice(source=plone_role_generator),
                 required=True)

    related = Text(title=LRMF(u'related role configuration'),
                   required=False)

RelatedFieldFormatValidator = RelatedFormatValidator
validator.WidgetValidatorDiscriminators(RelatedFieldFormatValidator, field=ILocalRoleConfig['related'])


class LocalRoleFieldConfigurationForm(LocalRoleConfigurationForm):

    @property
    def fields(self):
        fields = super(LocalRoleFieldConfigurationForm, self).fields
        fields = fields.values()
        schema_fields = []
        for name, fti_field in get_localrole_fields(self.context.fti):
            f = LocalRoleList(
                __name__=str(name),
                title=fti_field.title,
                description=fti_field.description,
                value_type=DictRow(title=u"fieldconfig",
                                   schema=ILocalRoleConfig)
            )
            schema_fields.append(f)

        schema_fields = sorted(schema_fields, key=lambda x: x.title)
        fields.extend(schema_fields)
        return field.Fields(*fields)


class LocalRoleFieldConfigurationPage(LocalRoleConfigurationPage):
    form = LocalRoleFieldConfigurationForm
