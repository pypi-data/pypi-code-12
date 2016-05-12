__title__ = 'fobi.contrib.apps.wagtail_integration.widgets'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('FobiFormWidget',)

from nine.versions import DJANGO_GTE_1_7

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from wagtail.wagtailcore.models import Page

from fobi.integration.processors import IntegrationProcessor

from .settings import WIDGET_FORM_SENT_GET_PARAM
from .helpers import (
    get_form_template_choices, get_success_page_template_choices
    )

class FobiFormPage(Page, IntegrationProcessor):
    """
    Widget for to FeinCMS.

    :property fobi.models.FormEntry form_entry: Form entry to be rendered.
    :property str template: If given used for rendering the form.
    """
    # Fobi integration processor configuration
    form_sent_get_param = WIDGET_FORM_SENT_GET_PARAM
    can_redirect = True

    # Wagtail
    #is_abstract = True

    # The configuration fields
    form_entry = models.ForeignKey('fobi.FormEntry', verbose_name=_("Form"))

    form_template_name = models.CharField(
        _("Form template name"), max_length=255, null=True, blank=True,
        choices=get_form_template_choices(),
        help_text=_("Template to render the form with.")
        )

    hide_form_title = models.BooleanField(
        _("Hide form title"), default=False,
        help_text=_("If checked, no form title is shown.")
        )

    form_title = models.CharField(
        _("Form title"), max_length=255, null=True, blank=True,
        help_text=_("Overrides the default form title.")
        )

    form_submit_button_text = models.CharField(
        _("Submit button text"), max_length=255, null=True, blank=True,
        help_text=_("Overrides the default form submit button text.")
        )

    success_page_template_name = models.CharField(
        _("Success page template name"), max_length=255, null=True, blank=True,
        choices=get_success_page_template_choices(),
        help_text=_("Template to render the success page with.")
        )

    hide_success_page_title = models.BooleanField(
        _("Hide success page title"), default=False,
        help_text=_("If checked, no success page title is shown.")
        )

    success_page_title = models.CharField(
        _("Succes page title"), max_length=255, null=True, blank=True,
        help_text=_("Overrides the default success page title.")
        )

    success_page_text = models.TextField(
        _("Succes page text"), null=True, blank=True,
        help_text=_("Overrides the default success page text.")
        )

    class Meta:
        abstract = True
        #app_label = 'fobi'
        #db_table = 'page_page_fobiformwidget'
        verbose_name, verbose_name_plural = _("Fobi form"), _("Fobi forms")

    def __unicode__(self):
        return ugettext('Fobi form')

    if DJANGO_GTE_1_7:
        def get_verbose_name(self):
            """
            """
            return self._meta.verbose_name

    def serve(self, request):
        """
        This is where most of the form handling happens.

        :param django.http.HttpRequest request:
        :return django.http.HttpResponse | str:
        """
        return self._process(request, self)

    def render(self, **kwargs):
        return getattr(self, 'rendered_output', '')

    def finalize(self, request, response):
        # Always disable caches if this content type is used somewhere
        response['Cache-Control'] = 'no-cache, must-revalidate'
