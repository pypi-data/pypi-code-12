# -#- coding: utf-8 -#-

from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.conf import settings
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from form_designer.models import FormContent
# do not import this before widget
from leonardo.module.media.utils import handle_uploaded_file
from leonardo.module.web.models import Widget
from leonardo_module_forms.signals import \
    process_valid_form as process_valid_form_signal

from .forms import FormWidgetForm


def _handle_uploaded_file(f, private=None, folder_name=None):
    '''save upladed file
    '''
    return handle_uploaded_file(f, folder=folder_name or settings.FORM_FILES_DIRECTORY,
                                is_public=private or settings.FORM_FILES_PRIVATE)


class FormWidget(Widget, FormContent):

    feincms_item_editor_form = FormWidgetForm

    form_layout = models.TextField(
        _('Form Layout'), blank=True, null=True,
        help_text=_('Crispy Form Layout see \
            http://django-crispy-forms.readthedocs.org/en/latest/layouts.html'))

    class Meta:
        abstract = True
        verbose_name = _('form')
        verbose_name_plural = _('forms')

    def process_valid_form(self, request, form_instance, **kwargs):
        """ Process form and return response (hook method). """

        process_valid_form_signal.send(
            sender=self.__class__,
            widget=self,
            form_instance=form_instance,
            request=request)

    def handle_files(self, form_instance, request):
        '''handle files from request'''

        files = []

        private = form_instance.cleaned_data.pop("private", None)
        folder_name = form_instance.cleaned_data.pop("folder_name", None)

        for key in request.FILES.keys():
            saved_file = _handle_uploaded_file(request.FILES[key],
                                               private=private,
                                               folder_name=folder_name)
            _key = key.replace(self.prefix + '-', '')
            form_instance.cleaned_data[_key] = '%s - %s' % (
                str(saved_file), saved_file.url)
            files.append(saved_file)
        return files

    @property
    def prefix(self):
        return 'fc%d' % self.id

    def get_complete_form(self, form_instance):

        # use crispy forms
        form_instance.helper = FormHelper(form_instance)
        form_instance.helper.form_action = '#form{}'.format(self.id)

        if self.form_layout:

            try:
                form_instance.helper.layout = eval(self.form_layout)
            except Exception as e:
                raise e

        else:

            form_instance.helper.layout = Layout()

            # Moving field labels into placeholders
            layout = form_instance.helper.layout
            for field_name, field in form_instance.fields.items():
                layout.append(Field(field_name, placeholder=field.label))

            form_instance.helper.layout.extend([ButtonHolder(
                Submit('submit', _('Submit'), css_class='button white')
            )
            ])

            # still have choice to render field labels
            if not self.show_form_title:
                form_instance.helper.form_show_labels = False

        return form_instance

    def get_template_data(self, request):
        context = {}

        form_class = self.form.form()

        formcontent = request.POST.get(self.prefix + '-_formcontent')

        if request.method == 'POST' and formcontent == smart_text(self.id):
            form_instance = form_class(
                request.POST, request.FILES, prefix=self.prefix)

            if form_instance.is_valid():

                # handle files
                files = self.handle_files(form_instance, request)

                process_result = self.form.process(form_instance, request)

                self.process_valid_form(
                    request, form_instance)

                # add reverse reference to files
                for file in files:
                    file.description = process_result[
                        'save_fs'].formatted_data()
                    file.save()

                context['message'] = self.success_message or process_result or u''

            else:
                form_instance = self.get_complete_form(form_instance)
                context["form"] = form_instance

        else:
            form_instance = form_class(prefix=self.prefix)
            form_instance = self.get_complete_form(form_instance)

            context['form'] = form_instance

        # append hidden field for check unique
        if "form" in context:
            context['form'].fields["_formcontent"] = forms.CharField(
                initial=self.id, widget=forms.widgets.HiddenInput)
            context['form'].helper.layout.append("_formcontent")

        return context
