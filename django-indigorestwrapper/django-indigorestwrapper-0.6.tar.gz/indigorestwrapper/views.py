from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from models import *
from serializers import *
from django.db import connections
from rest_framework import permissions
import urllib2
import json
from django.conf import settings
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse

def get_json_from_url(url):
    print 'get_json_from_url ',url
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req) 
    data =""
    try:
        data = json.load(f)
    except:
        print f.read()
    
    return data   
        

# class JSONResponse(HttpResponse):
#     """
#     An HttpResponse that renders its content into JSON.
#     """
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)

@api_view(['GET'])
def indigo_device_list(request):
    """
    List all devices, using the standard Indigo response.
    """    
    if request.method == 'GET':
        url = settings.INDIGO_URL + '/devices.json/'
        devices = get_json_from_url(url)
        return Response(devices)
        
        # cursor = connections['indigo_db'].cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        # print cursor.fetchall()
        #
        # devices = DeviceHistory1100227140.objects.all()
        # serializer = DeviceSerializer(devices, many=True)
        # return Response(serializer.data)    
        
@api_view(['GET'])
def device_list(request):
    """
    List all devices, using the cached data - so the actual sensor value etc is likely out of date, but you can use device_history for this.
    """    
    if request.method == 'GET':
        devices = Device.objects.all()
        print 'Got ', devices.count(), 'devices'
        device = devices[0]
        print 'Got device=',device
        print type(device) 
        serializer = DeviceSerializer(devices, many=True)        
        return Response(serializer.data)
        
        # cursor = connections['indigo_db'].cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        # print cursor.fetchall()
        #
        # devices = DeviceHistory1100227140.objects.all()
        # serializer = DeviceSerializer(devices, many=True)
        # return Response(serializer.data)    


@api_view(['GET'])
def device(request, id):
    """
    List information about this device with indigo id = id.
    """    
    if request.method == 'GET':
        # devices = get_json_from_url(settings.INDIGO_URL)
        # url = settings.INDIGO_URL
        # req = urllib2.Request(url+devices[1]['restURL'])
        # f = opener.open(req)
        # device = json.load(f)
        
        device = Device.objects.get(id=id) # FIXME
        print 'Got device=',device
        print type(device)
        serializer = DeviceSerializer(device)        
        return Response(serializer.data)
            
        # cursor = connections['indigo_db'].cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        # print cursor.fetchall()
        #
        # devices = DeviceHistory1100227140.objects.all()
        # serializer = DeviceSerializer(devices, many=True)
        # return Response(serializer.data)    



# class DeviceHistory(APIView):
#     """
#     Retrieve a device instance with identifier=id and show history
#     """

@api_view(['GET'])
def device_history(request, id):
    """
    Retrieve a device instance with identifier=id and show history
    """    
    try:
        print 'looking up device id=',id
        device_type = get_device_type(id)
        device  = get_device(id)
        #import pdb; pdb.set_trace()
        if request.method == 'GET':
            history = device.objects.using('indigo_db').all()
            serializer={}
            if (device_type==1):
                serializer = Device1Serializer(history, many=True)
            elif (device_type==2):
                serializer = Device2Serializer(history, many=True)
            elif (device_type==3):
                serializer = Device3Serializer(history, many=True)
            elif (device_type==4):
                serializer = Device4Serializer(history, many=True)
            elif (device_type==5):
                serializer = Device5Serializer(history, many=True)
            return Response(serializer.data)
    except Exception as inst:
        print inst
        print 'something went wrong...'
        return Response(status=status.HTTP_404_NOT_FOUND)


def get_device_type(identifier):
    """
    Determine a device type from the DB information
    """
    print 'looking up details for device', identifier
    cursor = connections['indigo_db'].cursor()
    sql = "SELECT * from 'device_history_"+str(identifier)+"'"
    cursor.execute(sql)
    col_names = [desc[0] for desc in cursor.description]
    # Not sure if the order could ever change ... if so, we need to do somethig a bit smarter here.
    if (col_names==['id', 'ts', 'sensitivity', 'state', 'state_active', 'state_disconnected', 'state_passive', 'state_preparing', 'state_unavailable', 'type']):
        return 1
    if (col_names==['id', 'ts', 'onoffstate']):
        return 2
    if (col_names==['id', 'ts', 'onoffstate', 'sensorvalue', 'sensorvalue_ui']):
        return 3
    if (col_names==['id', 'ts', 'batterylevel', 'batterylevel_ui', 'onoffstate']):
        return 4
    if (col_names==['id', 'ts', 'sensorvalue', 'sensorvalue_ui']):
        return 5
    if (col_names==['id', 'ts', 'accumenergytimedelta', 'accumenergytimedelta_ui', 'accumenergytotal', 'accumenergytotal_ui', 'brightnesslevel', 'curenergylevel', 'curenergylevel_ui', 'onoffstate']):
        return 6
    print 'Unknown type with column names = ',col_names
    return 0

def get_device(identifier):
    type = get_device_type(identifier)
    print 'type', type
    if type==0:
        print 'Cannot work out the type!'
        raise ValueError('Could not identify the type of device with identifier=',identifier)

    if type==1:
        device = Device1History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
    elif type==2:
        device = Device2History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
    elif type==3:
        device = Device3History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
    elif type==4:
        device = Device4History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
    elif type==5:
        device = Device5History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
    elif type==6:
        device - Device6History
        device._meta.db_table = 'device_history_'+str(identifier)
        return device
        
        
    
