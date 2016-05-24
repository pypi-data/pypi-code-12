"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

from falkonryclient.helper import schema as Schemas
from falkonryclient.service.http import HttpService
from falkonryclient.helper import utils as Utils
from cStringIO import StringIO

"""
FalkonryService
    Service class to link js client to Falkonry API server
"""


class FalkonryService:

    def __init__(self, host, token):
        """
        constructor
        :param host: host address of Falkonry service
        :param token: Authorization token
        """
        self.host  = host
        self.token = token
        self.http  = HttpService(host, token)

    def get_eventbuffers(self):
        """
        To get list of Eventbuffers
        """
        eventbuffers = []
        response = self.http.get('/Eventbuffer')
        for eventbuffer in response:
            eventbuffers.append(Schemas.Eventbuffer(eventbuffer=eventbuffer))
        return eventbuffers

    def create_eventbuffer(self, eventbuffer, options):
        """
        To create Eventbuffer
        :param eventbuffer: Eventbuffer
        :param options: dict
        """
        form_data = {
            'data': {
                'name'           : eventbuffer.get_name(),
                'timeIdentifier' : options['timeIdentifier'] if 'timeIdentifier' in options else 'time',
                'timeFormat'     : options['timeFormat'] if 'timeFormat' in options else 'iso_8601'
            }
        }
        if 'data' in options:
            data_type = 'json' if ('dataType' in options and options['dataType'] is 'json') else 'csv'
            form_data['files'] = {
                'data': (
                    Utils.random_string(10)+('.json' if data_type is 'json' else '.csv'),
                    StringIO(options['data'])
                )
            }
        raw_eventbuffer = self.http.fpost('/Eventbuffer', form_data)
        return Schemas.Eventbuffer(eventbuffer=raw_eventbuffer)

    def delete_eventbuffer(self, eventbuffer):
        """
        To delete a Eventbuffer
        :param eventbuffer: string
        """
        response = self.http.delete('/Eventbuffer/' + str(eventbuffer))
        return response

    def get_pipelines(self):
        """
        To get list of Pipelines
        """
        pipelines = []
        response = self.http.get('/Pipeline')
        for pipeline in response:
            pipelines.append(Schemas.Pipeline(pipeline=pipeline))
        return pipelines

    def create_pipeline(self, pipeline):
        """
        To create Pipeline
        :param pipeline: Pipeline
        """
        raw_pipeline = self.http.post('/Pipeline', pipeline)
        return Schemas.Pipeline(pipeline=raw_pipeline)

    def delete_pipeline(self, pipeline):
        """
        To delete a Pipeline
        :param pipeline: string
        """
        response = self.http.delete('/Pipeline/' + str(pipeline))
        return response

    def add_input_data(self, eventbuffer, data_type, options, data):
        """
        To add data to a Eventbuffer
        :param eventbuffer: string
        :param data_type: string
        :param options: dict
        :param data: string
        """
        url = '/Eventbuffer/' + str(eventbuffer) + \
              (('?subscriptionKey=' + options['subscription']) if 'subscription' in options else '')
        form_data = {
            'files': {
                'data': (
                    Utils.random_string(10)+('.json' if data_type is 'json' else '.csv'),
                    StringIO(data),
                    'text/plain;charset=UTF-8',
                    {'Expires': '0'}
                )
            }
        }
        response = self.http.fpost(url, form_data)
        return response

    def add_input_stream(self, eventbuffer, data_type, options, data):
        """
        To add data stream to a Eventbuffer
        :param eventbuffer: string
        :param data_type: string
        :param options: dict
        :param data: Stream
        """
        url = '/Eventbuffer/' + str(eventbuffer) + \
              (('?subscriptionKey=' + options['subscription']) if 'subscription' in options else '')
        form_data = {
            'files': {
                'data': (
                    Utils.random_string(10)+('.json' if data_type is 'json' else '.csv'),
                    data,
                    'text/plain;charset=UTF-8',
                    {'Expires': '0'}
                )
            }
        }
        response = self.http.upstream(url, form_data)
        return response

    def get_output(self, pipeline, start=None, end=None):
        """
        To get output of a Pipeline
        :param pipeline: string
        :param start: int
        :param end: int
        """
        url = '/Pipeline/' + str(pipeline) + '/output?'
        if isinstance(end, int):
            url += 'lastTime=' + str(end)
        if isinstance(start, int):
            url += '&startTime=' + str(start)
        else:
            if isinstance(start, int):
                url += '&startTime=' + str(start)
        stream = self.http.downstream(url)
        return stream

    def create_subscription(self, eventbuffer, subscription):
        """
        To create Subscription
        :param eventbuffer: string
        :param subscription: Subscription
        """
        raw_subscription = self.http.post('/Eventbuffer/' + eventbuffer + '/Subscription', subscription)
        return Schemas.Subscription(subscription=raw_subscription)

    def update_subscription(self, eventbuffer, subscription):
        """
        To update Subscription
        :param eventbuffer: string
        :param subscription: Subscription
        """
        raw_subscription = self.http.put('/Eventbuffer/' + eventbuffer + '/Subscription/' + subscription.get_key(), subscription)
        return Schemas.Subscription(subscription=raw_subscription)

    def delete_subscription(self, eventbuffer, subscription):
        """
        To delete Subscription
        :param eventbuffer: string
        :param subscription: Subscription
        """
        response = self.http.delete('/Eventbuffer/' + eventbuffer + '/Subscription/' + subscription)
        return response

    def create_publication(self, pipeline, publication):
        """
        To create Publication
        :param pipeline: string
        :param publication: Publication
        """
        raw_publication = self.http.post('/Pipeline/' + pipeline + '/Publication', publication)
        return Schemas.Publication(publication=raw_publication)

    def update_publication(self, pipeline, publication):
        """
        To update Publication
        :param pipeline: string
        :param publication: Publication
        """
        raw_publication = self.http.put('/Pipeline/' + pipeline + '/Publication/' + publication.get_key(), publication)
        return Schemas.Publication(publication=raw_publication)

    def delete_publication(self, pipeline, publication):
        """
        To delete Publication
        :param pipeline: string
        :param publication: Publication
        """
        response = self.http.delete('/Pipeline/' + pipeline + '/Publication' + publication)
        return response
