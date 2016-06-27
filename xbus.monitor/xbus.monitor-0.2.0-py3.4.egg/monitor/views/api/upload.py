import aiozmq
import io
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from tempfile import NamedTemporaryFile
from xbus.file_emitter import FileEmitter
from xbus.file_emitter import FileEmitterException

from xbus.monitor.auth import get_logged_user_id
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EmissionProfile


@view_config(
    route_name='upload',
    request_method='POST',
    renderer='json',
    http_cache=0,
)
def upload(request):
    """View to handle file uploads. They are sent to Xbus.
    """

    # Check request parameters.
    emission_profile_id = request.params.get('emission_profile_id')
    file = request.params.get('file')
    if not emission_profile_id or file is None:
        raise HTTPBadRequest(
            json_body={'error': 'No emission profile selected'},
        )

    # Get emission profile data from the database.
    emission_profile = DBSession.query(EmissionProfile).filter(
        EmissionProfile.id == emission_profile_id
    ).first()
    if not emission_profile:
        raise HTTPBadRequest(
            json_body={'error': 'Invalid emission profile'},
        )

    # Ensure execution of the emission profile is authorized for the current
    # user.
    if emission_profile.owner_id != get_logged_user_id(request):
        raise HTTPBadRequest(
            json_body={'error': 'Emission profile unauthorized'},
        )

    # Fetch the input descriptor.
    descriptor = emission_profile.input_descriptor.descriptor.decode('utf-8')
    encoding = emission_profile.encoding

    # TODO Use the selected encoding when decoding the file.

    front_url = request.registry.settings['xbus.broker.front.url']
    login = request.registry.settings['xbus.broker.front.login']
    password = request.registry.settings['xbus.broker.front.password']

    # Use a temporary file to store the upload.
    # TODO Use a pipe or some such?
    with NamedTemporaryFile(prefix='xbus-monitor-upload-') as f_temp:
        while True:
            buf = file.file.read(io.DEFAULT_BUFFER_SIZE)
            f_temp.write(buf)
            if len(buf) == 0:
                break

        # Open the file as text.
        f_temp.flush()
        f_temp_text = open(f_temp.name, 'r', newline='', encoding=encoding)

        # Send our data via 0mq to the Xbus front-end.
        zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
        try:
            emitter = FileEmitter(
                front_url, login, password, [descriptor], loop=zmq_loop
            )
            zmq_loop.run_until_complete(emitter.login())
            envelope_id = zmq_loop.run_until_complete(
                emitter.send_files([(f_temp_text, None)], encoding=encoding)
            )
        except FileEmitterException as e:
            raise HTTPBadRequest(json_body={'error': str(e)})

    return {'envelope_id': envelope_id}
