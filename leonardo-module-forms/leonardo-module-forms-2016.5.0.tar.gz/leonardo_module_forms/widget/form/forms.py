# -#- coding: utf-8 -#-

import copy

from crispy_forms.bootstrap import *
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.layout import HTML, Layout
from django import forms
from django.utils.translation import ugettext_lazy as _
from form_designer.models import Form, FormField
from horizon_contrib.forms import SelfHandlingModelForm
from horizon_contrib.forms.models import create_or_update_and_get
from leonardo.forms.fields.dynamic import DynamicModelChoiceField
from leonardo.module.media.fields import FileField
from leonardo.module.web.widgets.forms import WidgetUpdateForm

from .tables import FormFieldsFormset


class FormForm(SelfHandlingModelForm):

    id = forms.IntegerField('id', widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(FormForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            TabHolder(
                Tab(_('Base'),
                    'id', 'title', 'config_json'
                    ),
            )
        )
        if 'request' in kwargs:
            _request = copy.copy(kwargs['request'])
            _request.POST = {}
            _request.method = 'GET'
            from .tables import FormFieldsTable

            try:
                form = self._meta.model.objects.get(
                    id=kwargs['initial']['id'])
            except:
                form = None
                data = []
            else:
                data = form.fields.all()

            dimensions = Tab(_('Fields'),
                             HTML(
                                 FormFieldsTable(_request,
                                                 form=form,
                                                 data=data).render()),
                             )
            self.helper.layout[0].append(dimensions)

    def handle_related_models(self, request, obj):
        """Handle related models
        """
        formset = FormFieldsFormset(
            request.POST, prefix='fields')

        if formset.is_valid():
            formset.save()
        else:
            for form in formset.forms:
                if form.is_valid():
                    if 'id' in form.cleaned_data:
                        form.save()
                else:
                    # little ugly
                    data = form.cleaned_data
                    data['form'] = obj
                    if 'id' in data and isinstance(data['id'], FormField):
                        data['id'] = data['id'].id
                    data.pop('DELETE', None)
                    create_or_update_and_get(FormField, data)

        # optionaly delete dimensions
        if formset.is_valid():
            formset.save(commit=False)
            # delete objects
            for obj in formset.deleted_objects:
                obj.delete()
        return True

    class Meta:
        model = Form
        exclude = tuple()


class FormWidgetForm(WidgetUpdateForm):

    form = DynamicModelChoiceField(
        label=_("Form"),
        help_text=_("Select form."),
        queryset=Form.objects.all(),
        search_fields=[
            'title__icontains',
        ],
        cls_name='form_designer.form',
        form_cls='leonardo_module_forms.widget.form.forms.FormForm')

    tabs = {
        'advanced': {
            'name': 'Advanced',
            'fields': ('form_layout', 'show_form_title')
        }
    }
