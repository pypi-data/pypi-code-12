# -*- coding: utf-8 -*-
"""
Entity forms
"""
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from bazar.forms import CrispyFormMixin
from bazar.utils.imports import safe_import_module
from bazar.models import Entity, Note


class EntityModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return u"{kind} - {name}".format(name=obj.name, kind=obj.get_kind_display())


class EntityForm(CrispyFormMixin, forms.ModelForm):
    """
    Entity base form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.entity_helper'

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Entity
        fields = ('name', 'kind', 'adress', 'town', 'zipcode', 'phone', 'fax')


class EntityForKindForm(EntityForm):
    """
    Entity form for a specific kind (the kind is allready setted)
    """
    crispy_form_helper_path = 'bazar.forms.crispies.entity_helper'

    def __init__(self, *args, **kwargs):
        self.kind = kwargs.pop('kind', None)

        self.crispy_form_helper_kwargs = {
            'kind': self.kind,
        }

        super(EntityForKindForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super(EntityForKindForm, self).save(commit=False, *args, **kwargs)
        instance.kind = self.kind
        instance.save()

        return instance

    class Meta:
        model = Entity
        fields = ('name', 'adress', 'town', 'zipcode', 'phone', 'fax')


class EntityDeleteForm(CrispyFormMixin, forms.ModelForm):
    """
    Entity delete form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.entity_delete_helper'

    confirm = forms.BooleanField(label=_("Confirm"), initial=False, required=True)

    def __init__(self, *args, **kwargs):
        self.has_notes = kwargs.get('instance').note_set.count()>0
        self.crispy_form_helper_kwargs = {
            'has_notes': self.has_notes,
        }

        super(EntityDeleteForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)

        # Only add 'move_to' field if there are at least one note
        if self.has_notes:
            self.fields['move_notecards_to'] = EntityModelChoiceField(
                label=_("Move notecards to"),
                queryset=Entity.objects.all().exclude(pk=self.instance.id).order_by('kind', 'name'),
                empty_label=_("[No selection, notes will be deleted]"),
                required=False
            )

    def save(self):
        if self.cleaned_data.get('move_notecards_to', False):
            for note in self.instance.note_set.all():
                note.entity = self.cleaned_data['move_notecards_to']
                note.save()
        self.instance.delete()

        return

    class Meta:
        model = Entity
        fields = ('confirm',)# 'move_notecards_to',)
