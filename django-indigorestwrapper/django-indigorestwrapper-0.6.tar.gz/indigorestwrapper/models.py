# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Device(models.Model):
    modelpk = models.AutoField(primary_key=True)
    lastChangedTimeStr = models.CharField(max_length=32)
    # lastChangedRFC822 = models.DateTimeField()
    typeSupportsHVAC  = models.BooleanField()
    hasStateToDisplay = models.BooleanField()
    typeSupportsEnergyMeter  = models.BooleanField()
    typeSupportsIO = models.BooleanField()
    id = models.IntegerField() # id in indigo JSON
    typeFlags = models.IntegerField()
    typeSupportsOnOff = models.BooleanField()
    addressStr = models.CharField(max_length=32)
    typeSupportsSensorValue = models.BooleanField()
    type = models.CharField(max_length=128)
    classID = models.IntegerField()
    displayRawState = models.CharField(max_length=32)
    typeSupportsSpeedControl = models.BooleanField()
    displayInUI = models.BooleanField()
    displayLongState = models.CharField(max_length=32)
    restParent = models.CharField(max_length=32)
    address = models.IntegerField()
    versByte = models.IntegerField()
    name = models.CharField(max_length=128)
    lastChanged = models.IntegerField()
    typeSupportsDim = models.BooleanField()
    lastChangedDateStr = models.DateField()
    lastChangedRFC3339 = models.DateTimeField()
    devProtocol = models.IntegerField()
    folderID = models.IntegerField()
    typeSupportsSprinkler = models.BooleanField()
    
    def __unicode__(self):
        return '%i %s' % (self.id, self.name)

#Type 1:
class Device1History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    sensitivity = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    state_active = models.NullBooleanField()
    state_disconnected = models.NullBooleanField()
    state_passive = models.NullBooleanField()
    state_preparing = models.NullBooleanField()
    state_unavailable = models.NullBooleanField()
    type = models.TextField(blank=True, null=True)

    def __unicode__(self):
        # return '%i %s %i %i %i %i %i %i %i %i %s' % (self.id, self.ts, self.sensitivity, self.state, self.state_active, self.state_disconnected, self.state_passive, self.state_preparing, self.state_unavailable, self.type )
        print self.id, self.ts, self.sensitivity, self.state, self.state_active, self.state_disconnected,
        print self.state_unavailable, "A", self.type, "B"
        print self.state_preparing
        print "TEST",self.state_passive,'TEST'
        return ""


    # def __init__(self, db_table):
    #     print 'init with db_table',db_table
    #     self._meta.db_table = db_table

    class Meta:
        managed = False
        db_table = ''


#Type 2:
class Device2History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    onoffstate = models.NullBooleanField()
    class Meta:
        managed = False
        db_table = ''

#Type 3:
class Device3History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    onoffstate = models.NullBooleanField()
    sensorvalue = models.IntegerField(blank=True, null=True)
    sensorvalue_ui = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = ''

#Type 4:
class Device4History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    onoffstate = models.NullBooleanField()
    batterylevel = models.IntegerField(blank=True, null=True)
    batterylevel_ui = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = ''
        
#Type 5:
class Device5History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    sensorvalue = models.IntegerField(blank=True, null=True)
    sensorvalue_ui = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = ''
        
#Type 6:
class Device6History(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ts = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    accumenergytimedelta = models.IntegerField(blank=True, null=True)
    accumenergytimedelta_ui = models.TextField(blank=True, null=True)
    accumenergytotal = models.IntegerField(blank=True, null=True)
    accumenergytotal_ui = models.TextField(blank=True, null=True)
    brightnesslevel = models.IntegerField(blank=True, null=True)
    curenergylevel = models.IntegerField(blank=True, null=True)
    curenergylevel_ui = models.TextField(blank=True, null=True)
    onoffstate = models.NullBooleanField()
        
    class Meta:
        managed = False
        db_table = ''