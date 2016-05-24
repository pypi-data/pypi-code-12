# -*- coding: utf-8 -*-
from datetime import datetime
import itertools
from watson.common.imports import get_qualified_name
from watson.html.elements import TagMixin, flatten_attributes
from watson import validators, filters as filters_


class Definition(object):
    """Placeholder form element which allows for the creation of new form
    elements when the form is instantiated.


    """
    _counter = itertools.count()

    def __init__(self, class_, *args, **kwargs):
        self.count = next(Definition._counter)
        self.class_ = class_
        self.args = args
        self.kwargs = kwargs

    def generate_instance(self, form):
        cls = self.class_
        self.kwargs['form_'] = form
        return cls(definition=False, *self.args, **self.kwargs)


class Label(TagMixin):

    """A <label> tag which can be automatically included with fields.

    Attributes:
        html (string): the html used to render the label
        text (string): the text associated with the label
    """
    html = '<label {0}>{1}</label>'
    text = None

    def __init__(self, text, **kwargs):
        self.text = text
        super(Label, self).__init__(**kwargs)

    def render(self, field=None, **kwargs):
        attrs = self.attributes.copy()
        if 'text' in kwargs:
            self.text = kwargs['text']
            del kwargs['text']
        if 'for_' in kwargs:
            attrs['for'] = kwargs['for_']
            del kwargs['for_']
        attrs.update(kwargs)
        if field and 'id' not in field.attributes and field.name:
            # inject id based on field name
            id = field.name
            field.attributes['id'] = id
            attrs['for'] = id
        return self.html.format(flatten_attributes(attrs), self.text)

    __call__ = render


class FieldMixin(TagMixin):

    """A mixin that can be used as a base to simplify the creation of fields.

    When defining a field, a fully instantiated field must be created with
    definition=False as an argument in it's __init__ method. This is to
    facilitate the way fields are defined in Form objects in 2.0.0.

    Attributes:
        label (watson.form.fields.Label): the label associated with the field
        html (string): the html used to render the field
        validators (list): the validators that will be used to validate the
                           value.
        filters (list): the filters that will be used prior to validation
    """
    _counter = itertools.count()
    label = None
    html = '{0}'
    validators = None
    filters = None
    _errors = None
    _value = None
    _default_value = None
    _original_value = None

    def __new__(cls, definition=True, *args, **kwargs):
        if definition:
            return Definition(cls, *args, **kwargs)
        return super(FieldMixin, cls).__new__(cls)

    def __init__(self, name=None, value=None, default_value=None,
                 label=None, label_attrs=None, **kwargs):
        """Initializes the field with a specific name.
        """
        self.count = next(FieldMixin._counter)
        if not name:
            name = ''
        self.label = Label(label or name)
        if label_attrs and isinstance(label_attrs, dict):
            self.label.attributes.update(label_attrs)
        kwargs['name'] = name
        self.value = value
        self.default_value = default_value
        self.filters = [filters_.Trim()] + kwargs.get('filters', [])
        self.validators = kwargs.get('validators', [])
        if 'validators' in kwargs:
            del kwargs['validators']
        if 'filters' in kwargs:
            del kwargs['filters']
        if '_class' in kwargs:
            kwargs['class'] = kwargs.get('_class')
            del kwargs['_class']
        if 'required' in kwargs:
            self.validators.append(validators.Required())
            kwargs['required'] = 'required'
        if 'form_' in kwargs:
            self.form = kwargs['form_']
            del kwargs['form_']
        self._errors = []
        super(FieldMixin, self).__init__(**kwargs)

    @property
    def value(self):
        """Return the value for the field.

        If the field has been cleaned, the original value can be retrieved
        with FieldMixin.original_value.
        """
        return self._value

    @value.setter
    def value(self, value):
        """Convenience method to set the value on the field.
        """
        self._value = value

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        if not self.value:
            self.value = value

    @property
    def original_value(self):
        """Return the original value for the field.
        """
        return self._original_value if self._original_value else self.value

    def filter(self):
        """Filter the value on the field based on the associated filters.

        Set the original_value of the field to the first value stored. Note, if
        this is called a second time, then the original value will be
        overridden.
        """
        for _filter in self.filters:
            self._original_value = self.value
            self.value = _filter(self.value)

    def validate(self):
        """Validate the value of the field against the associated validators.

        Returns:
            A list of errors that have occurred when the field has been
            validated.
        """
        self._errors = []
        for validator in self.validators:
            try:
                validator(self.value)
            except ValueError as exc:
                self._errors.append(str(exc))
        return self._errors

    @property
    def errors(self):
        return self._errors

    @property
    def name(self):
        """Convenience method to retrieve the name of the field.
        """
        return self.attributes['name']

    @name.setter
    def name(self, name):
        """Override the name attribute on the field.
        """
        self.attributes['name'] = name
        if not self.label.text:
            self.label.text = name

    def render_with_label(self):
        """Render the field with the label attached.
        """
        raise NotImplementedError('The render method has not been implemented')

    def __str__(self):
        return self.render()

    def __call__(self, **kwargs):
        return self.render(**kwargs)

    def __repr__(self):
        return '<{0} name:{1}>'.format(get_qualified_name(self), self.name)


class Input(FieldMixin):

    """Creates an <input> field.

    Custom input types can be created by sending type='type' through the
    __init__ method.

    Example:

    .. code-block:: python

        input = Input(type='text')  # <input type="text" />
    """
    html = '<input {0} />'

    def render(self, **kwargs):
        """Render the element as html.

        Does not need to be called directly, as will be called by __str__
        natively.
        """
        attributes = self.attributes.copy()
        attributes.update(kwargs)
        if self.value is not None:
            attributes['value'] = str(self.value)

        return self.html.format(flatten_attributes(attributes))

    def render_with_label(self, **kwargs):
        """Render the element as html and include the label.

        Output the element and prepend the <label> to it.
        """
        return ''.join((self.label.render(self), self.render(**kwargs)))


class GroupInputMixin(Input):

    """A mixin for form elements that are used in a group.

    Related form elements are wrapped in a fieldset, with a common legend.
    """
    label_position = 'left'
    wrapped = True
    values = None
    fieldset_html = '<fieldset><legend>{0}</legend>{1}</fieldset>'

    def __init__(self, name=None, values=None, value=None, **kwargs):
        if 'label_position' in kwargs:
            self.label_position = kwargs['label_position']
            del kwargs['label_position']
        super(GroupInputMixin, self).__init__(name, value, **kwargs)
        if not values:
            values = value
        try:
            iter(values)
            self.values = values
        except:
            self.values = [(self.label.text, values)]

    def has_multiple_value(self):
        return isinstance(self.value, (tuple, list))

    def has_multiple_elements(self):
        """Determine whether or not a field has multiple elements.
        """
        return isinstance(self.values, (tuple, list)) and len(self.values) > 1

    def render(self, **kwargs):
        multiple_elements = self.has_multiple_elements()
        elements = []
        id = self.attributes.get('id', self.name)
        for index, label_value_pair in enumerate(self.values):
            attributes = self.attributes.copy()
            label_text, value = label_value_pair
            if multiple_elements:
                element_id = '{0}_{1}'.format(id, index)
            else:
                element_id = id
            attributes.update({
                'name': self.name,
                'id': element_id
            })
            attributes.update(kwargs)
            if value:
                attributes['value'] = value
            value = str(value)
            if isinstance(self.value, (list, tuple)):
                if value in (str(val) for val in self.value):
                    attributes['checked'] = 'checked'
            elif self.value and value == str(self.value):
                attributes['checked'] = 'checked'
            flat_attributes = flatten_attributes(attributes)
            element = self.__render_input(
                element_id,
                flat_attributes,
                label_text)
            elements.append(element)
        return ''.join(elements)

    def render_with_label(self, **kwargs):
        multiple_elements = self.has_multiple_elements()
        if multiple_elements:
            wrap_html = self.fieldset_html
        else:
            wrap_html = '{1}'
        return wrap_html.format(self.label.text, self.render(**kwargs))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.has_multiple_elements() and not isinstance(value, (list, tuple)):
            value = [value]
        self._value = value

    def __render_input(self, id, attributes, label_text):
        element = self.html.format(attributes)
        output = '{0}{1}'
        attrs = self.label.attributes.copy()
        attrs['for'] = id
        flat_attrs = flatten_attributes(attrs)
        if self.wrapped:
            if self.label_position == 'left':
                return (
                    self.label.html.format(
                        flat_attrs,
                        output.format(
                            label_text,
                            element))
                )
            return (
                self.label.html.format(
                    flat_attrs,
                    output.format(element,
                                  label_text))
            )
        else:
            label = self.label.html.format(flat_attrs, label_text)
            if self.label_position == 'left':
                return output.format(label, element)
            return output.format(element, label)


class Radio(GroupInputMixin):

    """Creates a radio input.

    Example:

    .. code-block:: python

        field = Radio(name='test', label='My Radio Options', values=(('Test', 1), ('Testing', 2)))
        str(field)

    .. code-block:: html

        <fieldset>
            <legend>My Radio Options</legend>
            <label for="test_0">Test<input id="test_0" name="test" type="radio" value="1" /></label>
            <label for="test_1">Testing<input id="test_1" name="test" type="radio" value="2" /></label>
        </fieldset>

    .. code-block:: python

        field = Radio(name='test', label='My Radio', values=1)
        str(field)

    .. code-block:: html

        <label for="test"><input type="radio" name="test" values="1" />My Radio</label>
    """

    def __init__(self, name=None, values=None, value=None, **kwargs):
        """Initializes the radio.

        If a value is specified, then that value out of the available values will
        be checked.
        If multiple values are specified, then a radio group will be created.

        Args:
            string name: the name of the field
            tuple|list values: the values to be used
            mixed value: the value for the field
        """
        super(
            Radio,
            self).__init__(
            name,
            values,
            value,
            type='radio',
            **kwargs)


class Checkbox(GroupInputMixin):

    """Creates a checkbox input.

    Example:

    .. code-block:: python

        field = Checkbox(name='test', label='My Radio Options', values=(('Test', 1), ('Testing', 2)))
        str(field)

    .. code-block:: html

        <fieldset>
            <legend>My Checkbox Options</legend>
            <label for="test_0">Test<input id="test_0" name="test" type="checkbox" /></label>
            <label for="test_1">Testing<input id="test_1" name="test" type="checkbox" /></label>
        </fieldset>

    .. code-block:: python

        field = Checkbox(name='test', label='My Checkbox', values=1)
        str(field)=None

    .. code-block:: html

        <label for="test"><input type="checkbox" name="test" value="1" />My Checkbox</label>
    """

    def __init__(self, name=None, values=None, value=None, **kwargs):
        """Initializes the checkbox.

        If a value is specified, then that value out of the available values will
        be checked.
        If multiple values are specified, then a checkbox group will be created.

        Args:
            name (string): the name of the field
            values (tuple|list): the values to be used
            value (mixed): the value for the field
        """
        super(
            Checkbox,
            self).__init__(
            name,
            values,
            value,
            type='checkbox',
            **kwargs)


class Button(Input):

    """Creates a button, can be used instead of Input(type="button").
    """
    html = '<button {0}>{1}</button>'

    def render(self, **kwargs):
        attributes = self.attributes.copy()
        attributes.update(kwargs)
        if self.value:
            attributes['value'] = str(self.value)
        return (
            self.html.format(flatten_attributes(attributes), self.label.text)
        )

    def render_with_label(self, **kwargs):
        return self.render(**kwargs)


class Submit(Input):

    """Creates a submit input.

    Attributes:
        button_mode (bool): whether or not to render as <button> or <input>
    """
    button_mode = False

    def __init__(self, name=None, value=None, button_mode=False, **kwargs):
        real_value = value or kwargs.get('label', name)
        if button_mode:
            self.html = '<button {0}>{1}</button>'
            self.button_mode = True
        super(Submit, self).__init__(name, real_value, type='submit', **kwargs)

    def render(self, **kwargs):
        if self.button_mode:
            attributes = self.attributes.copy()
            attributes.update(kwargs)
            return (
                self.html.format(
                    flatten_attributes(attributes),
                    self.label.text)
            )
        return super(Submit, self).render()

    def render_with_label(self, **kwargs):
        return self.render(**kwargs)


class Textarea(Input):

    """Creates a textarea field.
    """
    html = '<textarea {0}>{1}</textarea>'

    def render(self, **kwargs):
        attributes = self.attributes.copy()
        attributes.update(kwargs)
        value = self.value if self.value else ''
        return self.html.format(flatten_attributes(attributes), value)


class Select(FieldMixin):

    """Creates a select field.

    Attributes:
        html (string): the html for the outer select element
        option_html (string): the individual option html element
        optgroup_html (string): the optgroup html element
        options (list|dict): the options available
    """
    html = '<select {0}>{1}</select>'
    option_html = '<option value="{0}"{2}>{1}</option>'
    optgroup_html = '<optgroup label="{0}">{1}</optgroup>'
    options = None

    def __init__(self, name=None, options=None,
                 value=None, multiple=False, **kwargs):
        """Initializes the select field.

        If the options passed through are a dict, and the value of each key is
        a list or tuple, then an optgroup will be rendered, using the key
        as the label for the optgroup.

        Args:
            name (string): the name of the field
            options (list|dict): the options available
            value (string): the selected value
            multiple (bool): whether or not to allow multiple selections

        Example:

        .. code-block:: python

            field = Select(name='test', options=collections.OrderedDict([('Group One', [1, 2]), ('Group Two', [1, 2])]))
            str(field)

        .. code-block:: html

            <select name="test">
                <opgroup label="Group One">
                    <option value="1">1</option>
                </optgroup>
                <opgroup label="Group Two">
                    <option value="2">2</option>
                </optgroup>
            </select>
        """
        self.options = options or []
        if multiple or isinstance(value, (tuple, list)):
            kwargs['multiple'] = 'multiple'
        super(Select, self).__init__(name, value, **kwargs)

    def render(self, **kwargs):
        attributes = self.attributes.copy()
        attributes.update(kwargs)
        return (
            self.html.format(
                flatten_attributes(attributes),
                self._options_render())
        )

    def render_with_label(self, **kwargs):
        return ''.join((self.label.render(self), self.render(**kwargs)))

    # Options can also be referenced as values
    @property
    def values(self):
        return self.options

    @values.setter
    def values(self, values):
        self.options = values

    def _options_render(self):
        # internal method the render the options
        if isinstance(self.options, dict):
            options = []
            for label, value in self.options.items():
                if isinstance(value, (tuple, list)):
                    options.append(
                        self.optgroup_html.format(label,
                                                  self.__render_options(value)))
                else:
                    options.append(self.__render_option(label, value))
            return ''.join(options)
        else:
            return self.__render_options(self.options)

    def __render_options(self, options):
        return (
            ''.join([self.__render_option(value, value) for value in options])
        )

    def __render_option(self, label, value):
        # internal method to render an individual option
        if isinstance(value, (tuple, list)):
            value, label = value
        match = False
        str_value = str(value)
        str_self_value = str(self.value)
        if str_value == str_self_value:
            match = True
        elif isinstance(self.value, (list, tuple)):
            str_values = (str(val) for val in self.value)
            match = str_value in str_values
        selected = ' selected="selected"' if match else ''
        return self.option_html.format(value, label, selected)

# Convenience classes for input types. Can use Input(type='something') instead
# if required to create a different input field.
# Some of the input types add additional validators and filters to simplify the
# process.


class Text(Input):

    """Creates an <input type="text" /> element.
    """

    def __init__(self, name=None, value=None, **kwargs):
        super(Text, self).__init__(name, value, type='text', **kwargs)


class Date(Input):

    """Creates an <input type="date" /> element.
    """

    format = None

    def __init__(self, name=None, value=None, format='%Y-%m-%d', **kwargs):
        self.format = format
        date_filter = filters_.Date(format)
        if 'filters' in kwargs:
            kwargs['filters'].append(date_filter)
        else:
            kwargs['filters'] = [date_filter]
        if format:
            self.format = format
        super(Date, self).__init__(name, value, type='date', **kwargs)

    def render(self, **kwargs):
        """Format the date in the format the HTML5 spec requires.
        """
        if self.value:
            if not isinstance(self.value, str):
                self.value = self.value.strftime(self.format)
            else:
                date = datetime.strptime(self.value, self.format)
                self.value = date.strftime(self.format)
        return super(Date, self).render(**kwargs)


class Email(Input):

    """Creates an <input type="email" /> element.
    """

    def __init__(self, name=None, value=None, **kwargs):
        super(Email, self).__init__(name, value, type='email', **kwargs)


class Hidden(Input):

    """Creates an <input type="hidden" /> element.
    """

    def __init__(self, name=None, value=None, **kwargs):
        super(Hidden, self).__init__(name, value, type='hidden', **kwargs)


class Csrf(Input):

    """Creates an <input type="hidden" /> element for use in csrf protection.
    """

    def __init__(self, name='csrf_token', value=None, **kwargs):
        super(
            Csrf,
            self).__init__(name,
                           value,
                           type='hidden',
                           label='Cross-Site Request Forgery',
                           required=True,
                           **kwargs)
        self.validators.append(validators.Csrf())


class Password(Input):

    """Creates an <input type="password" /> element.
    """

    def __init__(self, name=None, value=None, **kwargs):
        super(Password, self).__init__(name, value, type='password', **kwargs)


class File(Input):

    def __init__(self, name=None, value=None, **kwargs):
        super(File, self).__init__(name, value, type='file', **kwargs)

    def render(self):
        """Overridden to prevent value from being put back into the field.
        """
        attributes = self.attributes.copy()

        return self.html.format(flatten_attributes(attributes))
