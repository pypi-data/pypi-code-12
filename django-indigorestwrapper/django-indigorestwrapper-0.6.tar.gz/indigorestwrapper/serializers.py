from rest_framework import serializers
from models import *
import datetime
import email

class DeviceSerializer(serializers.ModelSerializer):    
    # def validate_lastChangedRFC822(self, value):
    #     print value
    #     dt = datetime.datetime.utcfromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(value)))
    #     print dt
    #     return dt
    class Meta:
        model = Device
        # Can't get lastChangedRFC822 to work for the moment, but it really shouldn't matter
        fields = ( 'lastChangedTimeStr', 'typeSupportsHVAC', 'hasStateToDisplay', 'typeSupportsEnergyMeter', 
              'typeSupportsIO', 'id', 'typeFlags', 'typeSupportsOnOff', 'addressStr', 'typeSupportsSensorValue', 'type', 'classID', 'displayRawState', 
              'typeSupportsSpeedControl', 'displayInUI', 'displayLongState', 'restParent', 'address', 'versByte', 'name', 'lastChanged', 'typeSupportsDim', 
              'lastChangedDateStr', 'lastChangedRFC3339', 'devProtocol', 'folderID', 'typeSupportsSprinkler',)
    # def get_validation_exclusions(self):
    #        exclusions = super(DeviceSerializer, self).get_validation_exclusions()
    #        return exclusions + ['id']
           
# class Device1Serializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     ts = serializers.CharField()
#     sensitivity = serializers.IntegerField()
#     state = serializers.CharField()
#     state_active = serializers.BooleanField()
#     state_disconnected = serializers.BooleanField()
#     state_passive = serializers.BooleanField()
#     state_preparing = serializers.BooleanField()

class Device1Serializer(serializers.ModelSerializer):
    state = serializers.CharField()

    class Meta:
        model = Device1History
        fields = ('id', 'ts', 'sensitivity', 'state', 'state_active', 'state_disconnected', 'state_passive', 'state_preparing', 'state_unavailable', 'type')
#         fields = ('id', 'ts', 'sensitivity', 'state', )
        
class Device2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Device2History
        fields = ('id', 'ts', 'onoffstate')
        
class Device3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Device3History
        fields = ('id', 'ts', 'onoffstate', 'sensorvalue', 'sensorvalue_ui')
        
class Device4Serializer(serializers.ModelSerializer):
    class Meta:
        model = Device4History
        fields = ('id', 'ts', 'onoffstate', 'batterylevel', 'batterylevel_ui')

class Device5Serializer(serializers.ModelSerializer):
    class Meta:
        model = Device5History
        fields = ('id', 'ts', 'sensorvalue', 'sensorvalue_ui')

class Device6Serializer(serializers.ModelSerializer):
    class Meta:
        model = Device5History
        fields = ('id', 'ts', 'accumenergytimedelta', 'accumenergytimedelta_ui', 'accumenergytotal', 'accumenergytotal_ui', 'brightnesslevel', 'curenergylevel', 'curenergylevel_ui', 'onoffstate')
