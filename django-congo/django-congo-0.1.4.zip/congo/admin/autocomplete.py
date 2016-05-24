# -*- coding: utf-8 -*-
import autocomplete_light.shortcuts as autocomplete_light

class TextAutocomplete(autocomplete_light.AutocompleteModelBase):
#    attrs = {
##        'placeholder': 'Other model name ?',
#        'data-autocomplete-minimum-characters': 2,
#    }
#    widget_attrs = {
#        'data-widget-maximum-values': 15,
#    }

    def choices_for_request(self):
        assert self.choices is not None, 'choices should be a queryset'
        assert self.search_fields, 'autocomplete.search_fields must be 1 element list'

        self.order_by = [self.search_fields[0]]

        query = self.request.GET.get('q', '')
        exclude = self.request.GET.getlist('exclude')
        conditions = self._choices_for_request_conditions(query, self.search_fields)

        if self.request.user.is_staff:
            queryset = self.order_choices(self.choices.filter(conditions).exclude(pk__in = exclude))
        else:
            queryset = self.choices.none()

        result = []

        for value in queryset.values_list(self.search_fields[0], flat = True).distinct()[0:self.limit_choices]:
            attr_dict = {self.search_fields[0]: value}
            result.append(self.choices.model(**attr_dict))

        return result

    def choice_label(self, choice):
        return unicode(getattr(choice, self.search_fields[0]))

class HtmlAutocomplete(autocomplete_light.AutocompleteModelTemplate):
#    choice_template = 'template_autocomplete/choice.html'
#    attrs = {
##        'placeholder': 'Other model name ?',
#        'data-autocomplete-minimum-characters': 2,
#    }
#    widget_attrs = {
#        'data-widget-maximum-values': 15,
#    }

    def choices_for_request(self):
        choices = super(HtmlAutocomplete, self).choices_for_request()

        if not self.request.user.is_staff:
            choices = choices.none()

        return choices
