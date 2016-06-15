#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework   import serializers

class SerializerObjectActions(serializers.Serializer):
  icon            = serializers.CharField()
  modelclass      = serializers.CharField()
  action_name     = serializers.CharField()
  description     = serializers.CharField()
  static          = serializers.BooleanField()
  validation_dict = serializers.DictField()
  parameters      = serializers.DictField()
  opt_parameters  = serializers.DictField()
  return_dict     = serializers.DictField()


class ClassNameField(serializers.Field):
  def __init__(self, **kwargs):
    kwargs['read_only'] = True
    super(ClassNameField, self).__init__(**kwargs)

  def get_attribute(self, obj):
    # We pass the object instance onto `to_representation`,
    # not just the field attribute.
    return obj

  def to_representation(self, obj):
    """
    Serialize the object's class name.
    """
    return obj.__class__.__name__

  def to_internal_value(self, data):
    '''Retorna como uma string para a validação com o nome da
       Classe que o objeto se refere'''
    return data


class CustomChoiceTypeField(serializers.Field):
  
  def __init__(self, field_name=None, **kwargs):
        self.field_name = field_name
        super(CustomChoiceTypeField, self).__init__(**kwargs)

  def bind(self, field_name, parent):
      # In order to enforce a consistent style, we error if a redundant
      # 'method_name' argument has been used. For example:
      # my_field = serializer.CharField(source='my_field')
      if self.field_name is None:
        self.field_name = field_name
      else:
        assert self.field_name != field_name, (
          "It is redundant to specify field_name when it is the same"
      )

      super(CustomChoiceTypeField, self).bind(field_name, parent)
  
  def get_attribute(self, obj):
    # We pass the object instance onto `to_representation`,
    # not just the field attribute.
    return obj

  def to_representation(self, obj):
    display_method = 'get_{field_name}_display'.format(field_name=self.field_name)
    field_value = getattr(obj, self.field_name)
    if field_value is not None:
      method = getattr(obj, display_method)
      return [field_value, method()]
    else:
      return None

  def to_internal_value(self, data):
    '''Pega como valor só o primeiro elemento do choice'''
    if type(data) == list:
      #Caso esteja retornando a dupla de valores [chave do banco, descrição da opção]
      return data[0]
    else:
      #Caso esteja retornando só o valor da chave do banco
      return data


class CustomNestedSerializer(serializers.Field):
    """
    A read-only field that get its representation from calling a method on the
    parent serializer class. The method called will be of the form
    "get_{field_name}", and should take a single argument, which is the
    object being serialized.
    For example:
    class ExampleSerializer(self):
        extra_info = SerializerMethodField()
        def get_extra_info(self, obj):
            return ...  # Calculate some data to return.
    """
    def __init__(self, nested_serializer=None, many=False, **kwargs):
      self.nested_serializer = nested_serializer
      self.many = many
      super(CustomNestedSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
      return self.nested_serializer(value, many=self.many).data

    def to_internal_value(self, value):
      if self.many:
        pks = []
        for d in value:
          if d == 'None' or d is None:
            return None
          else:
            pks.append(d['pk'])
        return self.nested_serializer.Meta.model.objects.filter(pk__in=pks)
      else:
        if value == 'None' or value is None:
          return None
        else:
          return self.nested_serializer.Meta.model.objects.get(pk=value['pk'])

def validator_check_for_pk(value):
  pk = value.get('pk')
  if pk is None:
    raise serializers.ValidationError('Nested relations always need pk field')

def validator_check_for_pk_many(value):
  for value in values:
    pk = value.get('pk')
    if pk is None:
      raise serializers.ValidationError('Nested relations always need pk field')
