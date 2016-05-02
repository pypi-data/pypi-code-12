from django.core.management.base import BaseCommand, CommandError
from indigorestwrapper import views
from django.conf import settings
from indigorestwrapper.serializers import DeviceSerializer

class Command(BaseCommand):
    help = 'Resyncs the local device database with that of the indigo server, as defined in INDIGO_URL in settings.'

    def handle(self, *args, **options):
        url = settings.INDIGO_URL + '/devices.json/'
        self.stdout.write('Attempting to get data from '+url)
        
        devices = views.get_json_from_url(url)
        success = True
        for device in devices:
            device_url = settings.INDIGO_URL +device['restURL']
            self.stdout.write('Attempting to get device data from '+device_url)
            
            data=views.get_json_from_url(device_url)
            serializer = DeviceSerializer(data = data)
            
            if serializer.is_valid():
                self.stdout.write( 'woohoo!' )
                serializer.save()
            else:
                success=False
                for error in serializer.errors:
                    self.stdout.write(error)

        if (success):
            self.stdout.write('Successfully updated database')
        else:
            self.stdout.write('Problems updating database')
            