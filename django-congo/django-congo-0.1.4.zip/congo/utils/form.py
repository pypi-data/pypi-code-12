# -*- coding: utf-8 -*-
from django import forms

def add_widget_css_class(obj, css_class):
    """
    Adds css class for all forms fields or one field
    """
    if isinstance(obj, (forms.Form, forms.ModelForm)):
        for field_name in obj.fields:
            add_widget_attr(obj.fields[field_name], 'class', css_class)
    else:
        add_widget_attr(obj, 'class', css_class)


def set_widget_placeholder(obj):
    """
    Sets placeholder for all forms fields or one field
    """
    if isinstance(obj, (forms.Form, forms.ModelForm)):
        for field_name in obj.fields:
            filed = obj.fields[field_name]
            set_widget_attr(filed, 'placeholder', filed.label)
    else:
        set_widget_attr(obj, 'placeholder', obj.label)

def add_widget_attr(field, attr, value):
    if attr in field.widget.attrs and field.widget.attrs[attr]:
        field.widget.attrs[attr] += " %s" % value
    else:
        field.widget.attrs[attr] = value

def set_widget_attr(field, attr, value):
    field.widget.attrs[attr] = value
