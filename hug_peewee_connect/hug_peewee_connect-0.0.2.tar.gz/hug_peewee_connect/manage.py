import hug
from peewee import Model
from playhouse.db_url import connect


def manage(api, db_url, **connect_params):
    exclude = connect_params.pop('exclude', None)
    engine_instance = connect(db_url, **connect_params)

    hug_api = hug.API(api)

    @hug.request_middleware(api=hug_api)
    def process_data(request, response):
        if exclude is None or not exclude(request, 'request'):
            engine_instance.connect()

    @hug.response_middleware(api=hug_api)
    def process_data(request, response, resource):
        if exclude is None or not exclude(request, 'response'):
            engine_instance.close()

    class DatabaseModel(Model):
        class Meta:
            database = engine_instance

    engine_instance.Model = DatabaseModel

    return engine_instance
