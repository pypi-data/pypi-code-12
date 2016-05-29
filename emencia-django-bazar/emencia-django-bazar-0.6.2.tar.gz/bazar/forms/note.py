# -*- coding: utf-8 -*-
"""
Note forms
"""
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from bazar.forms import CrispyFormMixin
from bazar.utils.imports import safe_import_module
from bazar.models import Entity, Note

class NoteForm(CrispyFormMixin, forms.ModelForm):
    """
    Note form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.note_helper'
    
    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.entity = kwargs.pop('entity', None)
        
        super(NoteForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        
        # Set the form field editor for content field
        field_helper = safe_import_module(settings.BAZAR_MARKUP_FIELD_HELPER_PATH)
        if field_helper is not None:
            self.fields['content'] = field_helper(self, **{'label':_('Content'), 'required': False})
        
        self.fields['tags'].help_text = _("A comma-separated list of tags")

    def clean_content(self):
        """
        content content validation
        """
        content = self.cleaned_data.get("content")
        if content:
            validation_helper = safe_import_module(settings.BAZAR_MARKUP_VALIDATOR_HELPER_PATH)
            if validation_helper is not None:
                return validation_helper(self, content)
            
        return content

    def clean(self):
        cleaned_data = super(NoteForm, self).clean()
        content = self.cleaned_data.get("content", None)
        uploaded_file = self.cleaned_data.get("file", None)
        
        if not content and not uploaded_file:
            raise forms.ValidationError(_("You must fill at least a content or a file"))
        
        return cleaned_data
    
    def save(self, *args, **kwargs):
        instance = super(NoteForm, self).save(commit=False, *args, **kwargs)
        instance.author = self.author
        instance.entity = self.entity
        instance.save()
        
        # Using "commit=False" we need to trigger m2m save for tags :
        # http://django-taggit.readthedocs.org/en/latest/forms.html
        self.save_m2m()
        
        return instance
    
    class Meta:
        model = Note
        fields = ('title', 'content', 'file', 'tags')

class NoteDeleteForm(CrispyFormMixin, forms.ModelForm):
    """
    Note delete form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.note_delete_helper'
    
    confirm = forms.BooleanField(label=_("Confirm"), initial=False, required=True)
    
    def __init__(self, *args, **kwargs):
        super(NoteDeleteForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        
    def save(self):
        self.instance.delete()
        
        return
    
    class Meta:
        model = Note
        fields = ('confirm',)
