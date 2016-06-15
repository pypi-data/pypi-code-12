from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.settings import api_settings
from hosted_plugins import models

class KeyValueSerializer(serializers.ListSerializer):
    default_error_messages = {
        'not_a_dict': _('Expected a dict of items but got type `{input_type}`.')
    }
    
    def __init__(self, *args, **kwargs):
        super(KeyValueSerializer, self).__init__(*args, **kwargs)
        child_fields = self.child.fields.fields.keys()
        assert len(child_fields) == 2, 'The `fields` argument should be (key, value).'
        self.key_field = child_fields[0]
        self.val_field = child_fields[1]
    
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            message = self.error_messages['not_a_dict'].format(
                input_type=type(data).__name__
            )
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })
        data = [OrderedDict([(self.key_field, key), (self.val_field, val)]) for key,val in data.iteritems()]
        return super(KeyValueSerializer, self).to_internal_value(data)
    
    def to_representation(self, data):
        data = super(KeyValueSerializer, self).to_representation(data)
        value = OrderedDict()
        for kv in data:
            value.update(OrderedDict([(kv[self.key_field], kv[self.val_field])]))
        return value

class DocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Documentation
        fields = ('slug', 'content',)
        list_serializer_class = KeyValueSerializer

class ChecksumSerializer(serializers.ModelSerializer):
    checksum_type = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Checksum
        fields = ('checksum_type', 'checksum',)
        list_serializer_class = KeyValueSerializer
    
    def get_checksum_type(self, obj):
        return models.Checksum.CHECKSUM_TYPE[obj.checksum_type]

class UpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='platform.plugin')
    url = serializers.URLField()
    checksums = ChecksumSerializer(many=True)
    docs = DocumentationSerializer(many=True)
    
    class Meta:
        model = models.Update
        fields = ('name','version','min_reqd','max_tested',
                  'release_date','url',
                  'downloads','checksums','docs')
