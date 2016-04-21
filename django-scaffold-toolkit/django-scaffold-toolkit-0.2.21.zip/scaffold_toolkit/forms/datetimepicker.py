# -*- coding: utf-8 -*-
from django.conf import settings
from django.forms.util import flatatt
from django.forms.widgets import DateTimeInput, TimeInput
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

try:
    import json
except ImportError:
    from django.utils import simplejson as json
try:
    from django.utils.encoding import force_unicode as force_text
except ImportError:  # python3
    from django.utils.encoding import force_text


def get_language():
    lang = translation.get_language()
    return 'zh-CN' if lang == 'zh-hans' else lang


class DateTimePicker(DateTimeInput):
    class Media:
        css = {'all': ('%szui/lib/datetimepicker/datetimepicker.min.css' % settings.STATIC_URL,), }
        js = ('%szui/lib/datetimepicker/datetimepicker.min.js' % settings.STATIC_URL,)

    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (
        ('dd', r'%d'),
        ('d', r'%d'),

        ('mm', r'%m'),
        ('m', r'%m'),

        ('yyyy', r'%Y'),
        ('yy', r'%y'),

        ('MM', r'%B'),
        ('M', r'%b'),

        ('HH', r'%I'),
        ('H', r'%I'),
        ('hh', r'%H'),
        ('h', r'%H'),
        ('ii', r'%M'),
        ('i', r'%M'),

        ('ss', r'%S'),

        ('p', r'%P'),
        ('P', r'%P'),
    )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format.replace("%%", "%")  # fix some error

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-addon">
                <span%(icon_attrs)s></span>
            </span>
        </div>'''

    js_template = '''
        <script>
        $(document).ready(function(){
            $("#%(picker_id)s").datetimepicker(%(options)s);
        })
        </script>'''

    def __init__(self, attrs=None, format=None, options=None, show_icon=False, div_attrs=None, icon_attrs=None):
        if not show_icon:
            self.html_template = "<input%(input_attrs)s/>"
        self.show_icon = show_icon
        if not icon_attrs:
            icon_attrs = {'class': 'icon-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        elif format:
            format = self.conv_datetime_format_js2py(format)
        else:
            format = self.conv_datetime_format_js2py("yyyy-mm-dd hh:ii")
        super(DateTimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if options == False:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['language'] = get_language()
            self.options['weekStart'] = 1
            self.options['todayBtn'] = 1
            self.options['autoclose'] = 1
            self.options['todayHighlight'] = 1
            self.options['startView'] = 2
            self.options['forceParse'] = 0
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        input_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible
        if not self.picker_id:
            self.picker_id = input_attrs.get('id', '') + ('_picker' if self.show_icon else '')
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = dict(
            [(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if not self.options:
            js = ''
        else:
            js = self.js_template % dict(picker_id=picker_id,
                                         options=json.dumps(self.options or {}))
        return mark_safe(force_text(html + js))


class DatePicker(DateTimePicker):
    def __init__(self, attrs=None, format=None, options=None, show_icon=False, div_attrs=None, icon_attrs=None):
        self.show_icon = show_icon
        if format is None and options and options.get('format'):
            format = options.get('format')
        else:
            format = "yyyy-mm-dd"
        options = options or {}
        options['weekStart'] = 1
        options['todayBtn'] = 1
        options['autoclose'] = 1
        options['todayHighlight'] = 1
        options['startView'] = 2
        options['minView'] = 2
        options['forceParse'] = 0
        options['format'] = format
        options['language'] = get_language()
        super(DatePicker, self).__init__(attrs=attrs, format=format, options=options, show_icon=show_icon,
                                         div_attrs=div_attrs,
                                         icon_attrs=icon_attrs)


# As a TimeInput

class TimePicker(TimeInput):
    class Media:
        css = {'all': ('zui/lib/datetimepicker/datetimepicker.min.css',), }
        js = ('%szui/lib/datetimepicker/datetimepicker.min.js' % settings.STATIC_URL,)

    # http://www.malot.fr/bootstrap-datetimepicker/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (('HH', r'%H'),
                  ('hh', r'%I'),
                  ('mm', r'%M'),
                  ('ss', r'%S'),
                  ('a', r'%p'),
                  ('ZZ', r'%z'),
                  )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-addon">
                <span%(icon_attrs)s></span>
            </span>
        </div>'''

    js_template = '''
        <script>
            $(document).ready(function(){
                    $("#%(picker_id)s").datetimepicker(%(options)s);
            });
        </script>'''

    def __init__(self, attrs=None, format=None, options=None, show_icon=False, div_attrs=None, icon_attrs=None):
        self.show_icon = show_icon
        if not show_icon:
            self.html_template = "<input%(input_attrs)s/>"
        if not icon_attrs:
            icon_attrs = {'class': 'icon-time'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        elif format:
            format = self.conv_datetime_format_js2py(format)
        else:
            format = self.conv_datetime_format_js2py("hh:ii")
        super(TimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if options == False:  # datetimepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['language'] = get_language()
            self.options['weekStart'] = 1
            self.options['todayBtn'] = 1
            self.options['autoclose'] = 1
            self.options['todayHighlight'] = 1
            self.options['startView'] = 1
            self.options['minView'] = 0
            self.options['maxView'] = 1
            self.options['forceParse'] = 0
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        input_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible
        if not self.picker_id:
            self.picker_id = input_attrs.get('id', '') + ('_picker' if self.show_icon else '')
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = dict(
            [(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if not self.options:
            js = ''
        else:
            js = self.js_template % dict(picker_id=picker_id,
                                         options=json.dumps(self.options or {}))
        return mark_safe(force_text(html + js))
