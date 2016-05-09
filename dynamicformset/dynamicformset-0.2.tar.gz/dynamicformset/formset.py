from django.forms import (
    BaseFormSet,
    HiddenInput,
    IntegerField,
)

from django.forms.formsets import ORDERING_FIELD_NAME, DELETION_FIELD_NAME
from django.forms.widgets import Media
from django.template.loader import get_template, render_to_string


class DynamicFormSet(BaseFormSet):
    class Media:
        css = {
            'all': (
                'dynamicformset/dynamicformset.css',
            )
        }
        js = (
            'dynamicformset/dynamicformset.js',
        )

    button_text = 'Add form'
    delete_text = 'Delete form'
    template_name = "dynamicformset/base.html"

    @property
    def media(self):
        try:
            media = self.forms[0].media
        except (KeyError, IndexError):
            media = self.empty_form.media

        # Prepend list of assets with those that are defined in the class
        return Media(self.Media) + media

    def add_fields(self, form, index):
        """
        Overridden to make "ORDER" and "DELETE" fields hidden and
        add css class names to them
        """

        if self.can_order:
            widget = HiddenInput(attrs={
                'class': 'order_index'
            })
            # Only pre-fill the ordering field for initial forms.
            if index is not None and index < self.initial_form_count():
                form.fields[ORDERING_FIELD_NAME] = IntegerField(widget=widget, initial=index + 1, required=False)
            else:
                form.fields[ORDERING_FIELD_NAME] = IntegerField(widget=widget, required=False)
        if self.can_delete:
            widget = HiddenInput(attrs={
                'class': 'delete_flag'
            })
            form.fields[DELETION_FIELD_NAME] = IntegerField(widget=widget, required=False)

    def _should_delete_form(self, form):
        """
        JavaScript sets field value to "1" if form needs to be deleted
        """
        value = form.cleaned_data.get(DELETION_FIELD_NAME, None)
        return value is not None and value > 0

    def __str__(self):
        return render_to_string(self.template_name, {
            'formset': self,
            'button_text': self.button_text,
            'delete_text': self.delete_text
        })

    def as_table(self):
        raise NotImplemented("Use __str__() instead")

    def as_p(self):
        raise NotImplemented("Use __str__() instead")

    def as_ul(self):
        raise NotImplemented("Use __str__() instead")
