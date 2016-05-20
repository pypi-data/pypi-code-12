import re
import sys
from datetime import date, datetime
from django import forms
from django.db import models
from django.core.validators import RegexValidator
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class ForeignKeyRawIdWidgetWrapper(forms.Widget):
    """
    Admin widget that will show a thumbnail if the item is set instead of just
    a string
    """
    default_thumbnail = '<svg viewBox="0 0 188 188" width="188px" height="188px" xmlns="http://www.w3.org/2000/svg" fill-rule="evenodd" clip-rule="evenodd" stroke-linecap="round" stroke-linejoin="round" stroke-miterlimit="1.414"><path d="M186.75 4.432c0-2.032-1.65-3.682-3.682-3.682H4.432C2.4.75.75 2.4.75 4.432v178.636c0 2.032 1.65 3.682 3.682 3.682h178.636c2.032 0 3.682-1.65 3.682-3.682V4.432z" fill="#ebebeb" stroke-width="1.5" stroke="#000"/><path d="M158.02 52.826c0-1.516-1.23-2.747-2.747-2.747H32.227c-1.516 0-2.747 1.23-2.747 2.746v81.848c0 1.516 1.23 2.747 2.747 2.747h123.046c1.516 0 2.747-1.23 2.747-2.746V52.826z" fill="%s" stroke="#000"/></svg>'

    def __init__(self, widget):
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices
        self.widget = widget
        self.rel = widget.rel
        self.admin_site = widget.admin_site
        self.db = widget.db
        self.widget.label_for_value = self.label_for_value

    def __deepcopy__(self, memo):
        import copy
        obj = copy.copy(self)
        obj.widget = copy.deepcopy(self.widget, memo)
        obj.attrs = self.widget.attrs
        memo[id(self)] = obj
        return obj

    @property
    def media(self):
        return self.widget.media

    def render(self, name, value, *args, **kwargs):
        from django.utils.safestring import mark_safe
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            if obj.thumbnail:
                img_str = '<img src="%s" width="188"> ' % obj.thumbnail
            else:
                img_str = '<div style="float: left;margin-right: 10px">%s</div>' % (self.default_thumbnail % obj.background_color)
        except (ValueError, self.rel.to.DoesNotExist):
            img_str = self.default_thumbnail % '#FFF'
        return mark_safe(img_str + self.widget.render(name, value, *args, **kwargs))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)

    def label_for_value(self, value):
        from django.core.urlresolvers import reverse
        from django.utils.html import escape
        from django.utils.text import Truncator

        rel_to = self.rel.to
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            related_url = reverse('admin:%s_%s_change' %
                                    (rel_to._meta.app_label,
                                    rel_to._meta.model_name),
                                    args=(value, ),
                                    current_app=self.admin_site.name)
            edit_str = '&nbsp;&nbsp;<a href="%s" title="View" target="_blank">View %s</a>' % (related_url, rel_to._meta.model_name)
            metadata = "<br/>".join([
                escape(obj.date_string),
                escape(Truncator(obj.headline).words(14, truncate='...')),
                escape(Truncator(obj.text).words(14, truncate='...')),
            ])
            return "".join([
                "<div>",
                '<strong>%s</strong>' % escape(Truncator(obj).words(14, truncate='...')),
                edit_str,
                "<p>",
                metadata,
                "</p>",
                "</div>"
            ])

        except (ValueError, self.rel.to.DoesNotExist):
            return ''


def get_month_choices():
    """
    Get the choices for months using the locale
    """
    import locale
    locale.setlocale(locale.LC_ALL, '')
    output = [('00', 'No month')]
    for i in range(1, 13):
        output.append(("%02d" % i,
            locale.nl_langinfo(getattr(locale, 'ABMON_%s' % i)))
        )
    return output


def get_day_choices():
    """
    Return the choices for days
    """
    output = [('00', 'No day')]
    for i in range(1, 32):
        output.append(("%02d" % i, str(i)))
    return output


class HistoricalDate(object):
    """
    A field that stores a historical date as an integer with different resolutions

    The field format is +/-YYYYYYYYMMDD

    Parsed as last 2 digits are the day, with 00 meaning not specified
    second-to-last 2 digits are month, with 00 meaning not specified
    remaining digits are year.

    Maximum year in the past is 214748 BC

    Examples:
    10000 = 1AD
    -10000 = 1BC
    0 = Undefined
    99999999 = "the present"
    19631122 = Nov 22, 1963
    -45611200 = Dec 4561BC
    """
    def __init__(self, value=None):
        if value and not isinstance(value, (int, date, datetime)):
            raise ValueError("HistoricalDate must be an int, date or datetime.")
        if value:
            if isinstance(value, (date, datetime)):
                self.from_date(value)
                return
            elif abs(value) < 10000:
                raise ValueError("HistoricalDate must have at least 5 digits.")
            elif value == 99999999:
                self.value = sys.maxint
                self.year = sys.maxint
                self.month = sys.maxint
                self.day = sys.maxint
                return
            numstr = str(value)
            day = int(numstr[-2:])
            month = int(numstr[-4:-2])
            year = int(numstr[:-4])
            if month < 1:
                month = None
            if day < 1:
                day = None
        else:
            year = month = day = None
        self.value = value
        self.year = year
        self.month = month
        self.day = day
        self.validate_month()

    def validate_month(self):
        if self.month is not None and (self.month < 1 or self.month > 12):
            raise ValueError("Invalid month in value. %s is not between 00 and 12" % self.month)

    def validate_day(self):
        if self.month is None and self.day is not None:
            raise ValueError("Day specified without month.")
        if self.day is not None and (self.day < 1):
            raise ValueError("Day less than 01")
        if self.day is not None:
            if self.year < 1:
                date(2012, self.month, self.day)  # Use a leap year for that possibility
            else:
                self.to_date()

    def to_dict(self):
        output = {'year': str(self.year)}
        if self.month:
            output['month'] = str(self.month)

            # There shouldn't be a "day" if there isn't a month, but including
            # this in the if self.month condition to make sure.
            if self.day:
                output['day'] = str(self.day)
        return output

    def to_date(self):
        if self.value == sys.maxint:
            return date.today()
        return date(self.year, self.month, self.day)

    def from_date(self, value):
        """
        Populate the values from a date.
        """
        self.year = value.year
        self.month = value.month
        self.day = value.day
        self.value = (self.year * 10000) + (self.month * 100) + self.day

    def __repr__(self):
        return "HistoricalDate(%r)" % self.value

    def __str__(self):
        import locale
        locale.setlocale(locale.LC_ALL, '')
        output = []
        if self.day is not None:
            output.append(str(self.day))
        if self.month is not None:
            output.append(locale.nl_langinfo(getattr(locale, 'ABMON_%s' % self.month)))
        if self.year is not None:
            output.append(str(abs(self.year)))
        if self.year:
            if self.year < 0:
                output.append('BCE')
            else:
                output.append('CE')
        return " ".join(output)

    def __unicode__(self):
        return self.__str__()

    def __int__(self):
        return self.value

    def __cmp__(self, other):
        return cmp(self.value, int(other))


class HistoricalDateWidget(forms.MultiWidget):
    """
    A widget for a Historical Date field. Includes 3 text entry widgets and
    optional "to present" checkbox
    """
    def __init__(self, attrs=None):
        if attrs:
            new_attrs = attrs.copy()
        else:
            new_attrs = {'class': 'vHistoricDateField'}
        year_attrs = new_attrs.copy()
        year_attrs['size'] = "10"
        widgets = (forms.TextInput(attrs=year_attrs),
                   forms.Select(attrs=new_attrs, choices=(('-', 'BCE'), ('+', 'CE'))),
                   forms.Select(attrs=new_attrs, choices=get_month_choices()),
                   forms.Select(attrs=new_attrs, choices=get_day_choices()))
        return super(HistoricalDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            hdate = HistoricalDate(value)
            if hdate.year < 0:
                era = '-'
            else:
                era = '+'
            return [abs(hdate.year), era,
                    "%02d" % (hdate.month or 0), "%02d" % (hdate.day or 0)]
        return ['', '+', '00', '00']

    def format_output(self, rendered_widgets):
        return "&nbsp;".join(rendered_widgets)


class HistoricalDateFormField(forms.MultiValueField):
    widget = HistoricalDateWidget

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = HistoricalDateWidget
        fields = (
            forms.IntegerField(min_value=1),
            forms.ChoiceField(choices=(('-', 'BCE'), ('+', 'CE'))),
            forms.ChoiceField(choices=get_month_choices()),
            forms.ChoiceField(choices=get_day_choices())
        )
        super(HistoricalDateFormField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Convert the value list into an integer
        """
        if not data_list:
            return None
        if data_list[0] is None:
            return None
        out = int("".join([data_list[1], str(data_list[0]), data_list[2], data_list[3]]))
        return out

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': self.verbose_name,
                    'help_text': self.help_text}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return HistoricalDateWidget(**defaults)


class HistoricalDateField(models.IntegerField):
    """
    A subclass of integer that stores a HistoricalDate value.
    """
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "IntegerField"

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return str(self.get_db_prep_value(value))

    def formfield(self, **kwargs):
        defaults = {'form_class': HistoricalDateFormField}
        defaults.update(kwargs)
        return super(HistoricalDateField, self).formfield(**defaults)

    def get_db_prep_value(self, value, *args, **kwargs):
        if isinstance(value, basestring):
            return int(value)
        elif isinstance(value, int):
            return value
        elif isinstance(value, list):
            return int("".join(value))


color_re = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
validate_color = RegexValidator(color_re, _('Enter a valid color.'), 'invalid')


class ColorWidget(forms.Widget):
    class Media:
        js = ['timelines/jscolor.min.js', ]

    def render(self, name, value, attrs=None):
        return render_to_string('timelines/color.html', {'name': name, 'value': value, 'attrs': attrs})


class ColorField(models.CharField):
    default_validators = [validate_color]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorWidget
        return super(ColorField, self).formfield(**kwargs)
