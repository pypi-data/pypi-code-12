# -*- coding: utf-8 -*-
import collections
from watson.form.fields import File, Hidden, Definition
from watson.html.elements import TagMixin, flatten_attributes
from watson.common.contextmanagers import suppress
from watson.common.datastructures import MultiDict
from watson.common.decorators import cached_property
from watson.common.imports import get_qualified_name


IGNORED_ATTRIBUTES = ('fields', 'data', 'raw_data', 'errors')


class FieldDescriptor(object):
    """Allow set/get access to the field value via Form.field_name

    Fields accessed via a Form object will provide access directly to
    set and get the value of the field. When the field is being rendered
    in a template, the set/get will provide access to the field object
    itself.
    Access to the field prior to rendering can be made via Form.fields[name]
    where name is the attribute name of the field.
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        field = instance.fields[self.name]
        if instance._rendering:
            return field
        return field.value

    def __set__(self, instance, value):
        instance.fields[self.name].value = value


class FormMeta(type):
    """Assigns the FieldDescriptor objects to the Form object.
    """
    def __init__(cls, name, bases, attrs):
        fields = []
        for field_name in dir(cls):
            if (not field_name.startswith('_') and
                    field_name not in IGNORED_ATTRIBUTES):
                field = getattr(cls, field_name)
                if isinstance(field, Definition):
                    fields.append((field_name, field))
        fields.sort(key=lambda pair: pair[1].count)
        cls._defined_fields = collections.OrderedDict(fields)

    def __call__(cls, *args, **kwargs):
        return type.__call__(cls, *args, **kwargs)


class Form(TagMixin, metaclass=FormMeta):
    """Declarative HTML <form> management.

    Example:

    .. code-block:: python

        from watson.form import fields
        class MyForm(Form):
            text = fields.Text(name='text', label='My TextField')
            another = fields.Checkbox(name='another[]')

        form = MyForm('my_form')
        form.text = 'Something'

        # in view
        {% form.open() %}   # <form name="my_form">
        {% form.text %}     # <input name="text" type="text" value="Something" />
        {% form.text.render_with_label() %} # <label for="text">My TextField</label><input id="text" name="text" type="text" value="Something" />
        {% form.another %}  # <input name="another[]" />
        {% form.close() %}  # </form>
    """
    _fields = None
    _mapped_fields = None
    _rendering = False
    _ignored_bound_fields = None
    _bound_object = None
    _bound_object_mapping = None
    _validated = False

    def __init__(self, name=None, method='post',
                 action=None, detect_multipart=True, validators=None,
                 values_provider=None, **kwargs):
        """Inititalize the form and set some default attributes.

        Args:
            name (string): the name of the form
            method (string): the http method to use
            action (string): the url to submit the form to
            detect_multipart (boolean): automatically set multipart/form-data
        """
        self._ignored_bound_fields = []
        self.validators = validators or []
        self._process_tag_attributes(name, method, action, kwargs)
        self._change_http_method(method)
        self._set_values_provider(values_provider)
        self._detect_multipart(detect_multipart)

    def _process_tag_attributes(self, name, method, action, kwargs):
        if '_class' in kwargs:
            kwargs['class'] = kwargs.get('_class')
            del kwargs['_class']
        self.attributes = collections.ChainMap({
            'name': name or self.__class__.__name__,
            'method': method.lower(),
            'action': action or '/',
            'enctype':
            kwargs.get('enctype', 'application/x-www-form-urlencoded')
        }, kwargs)

    def _change_http_method(self, method):
        if self.method not in ('get', 'post'):
            field_name = 'http_request_method'
            self.attributes['method'] = 'post'
            self._add_field(field_name, Hidden(
                name='HTTP_REQUEST_METHOD',
                value=method.upper(),
                definition=False))

    def _add_field(self, field_name, field):
        self.fields[field_name] = field
        setattr(self.__class__, field_name, FieldDescriptor(field_name))

    def _detect_multipart(self, should_detect):
        if should_detect:
            for field_name, field in self.fields.items():
                if isinstance(field, File):
                    self.attributes['enctype'] = 'multipart/form-data'

    def _set_values_provider(self, values_provider):
        for field_name, field in self.fields.items():
            if hasattr(values_provider, field_name):
                field.values = getattr(values_provider, field_name)

    # field methods

    @cached_property
    def fields(self):
        self._mapped_fields = {}
        fields = collections.OrderedDict()
        for field_name, field in self._defined_fields.items():
            instance = field.generate_instance(self)
            setattr(self.__class__, field_name, FieldDescriptor(field_name))
            if not instance.name:
                instance.name = field_name
            self._mapped_fields[instance.name] = instance
            fields[field_name] = instance
        return fields

    @property
    def defined_fields(self):
        return self._defined_fields

    # data methods

    @cached_property
    def raw_data(self):
        """Returns a dict containing all the original field values.

        Field values will be their pre-filtered values.
        """
        return {field_name: field.original_value for
                field_name, field in self.fields.items()}

    @property
    def data(self):
        """Returns a dict containing all the field values.

        Used as a shorthand method to retrieve data from all the form fields
        rather than having to access the fields themselves.
        """
        return {field_name: field.value for
                field_name, field in self.fields.items()}

    @data.setter
    def data(self, data):
        """Sets the data for the form.

        Iterates through all the fields on the form and injects the value.

        Args:
            data (dict|watson.http.messages.Request): A dict of key/value pairs to populate the form with.
        """
        self.invalidate()
        if hasattr(data, 'post'):
            raw_data = MultiDict()
            raw_data.update(data.post.items())
            for key, value in data.files.items():
                # need to do this rather than .update due to File objects
                # being named tuples
                raw_data[key] = value
        else:
            raw_data = data
        self._set_data_on_fields(raw_data)

    def _set_data_on_fields(self, data):
        # internal method for setting the data on the fields
        for key in self._mapped_fields:
            if key not in self._ignored_bound_fields:
                field = self._mapped_fields[key]
                value = data.get(key, field.default_value)
                if hasattr(field, 'has_multiple_value') \
                        and field.has_multiple_value():
                    if value:
                        if not isinstance(value, (tuple, list)):
                            value = [value]
                    else:
                        value = []
                field.value = value

    # error methods

    @cached_property
    def errors(self):
        """Returns a list of errors associated with the form.

        If the form has not been validated yet, calling this property
        will cause validation to occur.
        """
        self.is_valid()
        errors = {}
        for field_name, field in self.fields.items():
            error_list = field.errors
            if error_list:
                errors[field_name] = {'messages': field.errors,
                                      'label': field.label.text}
        if self._form_errors:
            errors['form'] = {'messages': self._form_errors, 'label': 'Form'}
        return errors

    # binding methods

    @property
    def bound_object(self):
        return self._bound_object

    def bind(self, obj=None, mapping=None, ignored_fields=None, hydrate=True):
        """Binds an object to the form.

        Optionally additional mapping can be specified in order to set values on
        any of the classes that may exist within the object.
        If this method is called after the data has been set on the form, then
        the existing data will be overridden with the attributes on the object
        unless hydrate is set to false.

        Args:
            obj (class|dict): the class to bind to the form.
            mapping (dict): the mapping between the form fields and obj attributes.
            ignored_fields (list|tuple): fields to ignore when binding.
            bool hydrate: whether or not to hydrate the form with the obj attributes.

        Example:

        .. code-block:: python

            form = ...
            user = User(username='test')
            form.bind(user)
            form.username.value  # 'test'
        """
        self._ignored_bound_fields = ignored_fields or []
        if obj:
            self._bound_object = obj
            if mapping:
                self._bound_object_mapping = mapping
        self.invalidate()
        if obj and hydrate:
            self.__hydrate_obj_to_form()

    # validation methods

    @property
    def validated(self):
        return self._validated

    def invalidate(self):
        """Invalidate the data that has been bound on the form.

        This is called automatically when data is bound to the form and
        sets the forms validity to invalid.
        """
        attrs = ('_data', '_raw_data', '_errors', '_form_errors')
        for attr in attrs:
            with suppress(AttributeError):
                delattr(self, attr)
        self._validated = self._valid = False

    def is_valid(self):
        """Determine whether or not the form and relating values are valid.

        Filter all the values on the fields associated with the form, and
        then validate each field. Will only execute the filter/validation
        steps if the form has not been previously validated, or has
        been invalidated.

        Returns:
            boolean value depending on the validity of the form.
        """
        if not self.validated:
            self._form_errors = []
            self._valid = True
            for field_name, field in self.fields.items():
                field.filter()
                valid = field.validate()
                if len(valid) > 0:
                    self._valid = False
            if self._valid:
                for validator in self.validators:
                    try:
                        validator(self)
                    except ValueError as exc:
                        self._valid = False
                        self._form_errors.append(str(exc))
            self._validated = True
        if self._valid and self._bound_object:
            self.__hydrate_form_to_obj()
        return self._valid

    # rendering methods

    def open(self, **kwargs):
        """Render the start tag of the form.

        Any addition kwargs will be used within the attributes.
        """
        self._rendering = True
        attrs = self.attributes.copy()
        if kwargs:
            attrs.update(kwargs)
        return '<form {0}>'.format(flatten_attributes(attrs))

    def close(self, include_http_request=True):
        """Render the end tag of the form.

        If the form has the http_request_method input then include it in the
        tag by default.

        Args:
            include_http_request (boolean): Whether or not to include the HTTP_REQUEST_METHOD field
        """
        self._rendering = False
        tag = '{0}</form>'
        field = ''
        if include_http_request and 'http_request_method' in self.fields:
            field = str(self.fields['http_request_method'])
        return tag.format(field)

    def render(self, with_tag='div', with_label=True):
        """Output the entire form as a string.

        Called automatically by the __str__ method.

        Args:
            with_tag (string): the tag to be used to separate the elements.
            with_label (boolean): render each field with it's label.

        Returns:
            A string representation of the form.
        """
        html = '{open}{fields}{close}'
        fields = ['<{0}>{1}</{0}>'.format(with_tag,
                                          field.render_with_label() if with_label else str(field))
                  for field_name, field in self.fields.items()]
        return (
            html.format(
                open=self.open(),
                close=self.close(False),
                fields=''.join(fields))
        )

    # convenience methods

    @property
    def name(self):
        return self.attributes['name']

    @property
    def method(self):
        return self.attributes['method']

    @property
    def action(self):
        return self.attributes['action']

    @property
    def enctype(self):
        return self.attributes['enctype']

    def __len__(self):
        """Return the number of fields associated with the form.
        """
        return len(self.fields)

    def __repr__(self):
        return '<{0} name:{1} method:{2} action:{3} fields:{4}>'.format(
            get_qualified_name(self),
            self.name,
            self.method,
            self.action,
            len(self))

    # hydration and internal methods

    def __hydrate_obj_to_form(self):
        # should never be called externally. Triggered by bind.
        obj_mapping = self._bound_object_mapping or {}
        for field_name, field in self.fields.items():
            current_obj = self._bound_object
            attr = field_name
            if field_name in obj_mapping:
                attr = obj_mapping[field_name][-1]
                fields = obj_mapping[field_name][0:-1]
                for name in fields:
                    try:
                        current_obj = getattr(current_obj, name)
                    except:
                        raise AttributeError(
                            'Mapping for object does not match object structure.')
            if hasattr(current_obj, attr) and attr not in self._ignored_bound_fields:
                value = getattr(current_obj, attr)
                self.fields[field_name].value = value

    def __hydrate_form_to_obj(self):
        # should never be called externally. Triggered by is_valid.
        obj_mapping = self._bound_object_mapping or {}
        for field_name in self.data:
            field = self.fields[field_name]
            current_obj = self._bound_object
            value = field.value
            attr = field_name
            if field_name in obj_mapping:
                fields = obj_mapping[field_name][0:-1]
                attr = obj_mapping[field_name][-1]
                for name in fields:
                    try:
                        current_obj = getattr(current_obj, name)
                    except:
                        raise AttributeError(
                            'Mapping for object does not match object structure.')
            if hasattr(current_obj, attr) and attr not in self._ignored_bound_fields:
                multiple_attr_setter = 'add_{}'.format(attr)
                try:
                    if hasattr(field, 'has_multiple_value')\
                            and field.has_multiple_value()\
                            and hasattr(current_obj, multiple_attr_setter):
                        method = getattr(current_obj, multiple_attr_setter)
                        for val in value:
                            method(val)
                    else:
                        setattr(current_obj, attr, value or None)
                except:  # pragma: no cover
                    # something nasty happened here, the user should manage it
                    pass


class Multipart(Form):

    """Convenience class for forms that should be multipart/form-data.

    By default, the Form class will automatically detect whether or not
    a field is of type file, and convert it to multipart.
    """

    def __init__(self, name, method='post', action=None, **kwargs):
        kwargs['enctype'] = 'multipart/form-data'
        super(Multipart, self).__init__(name, method, action, **kwargs)
