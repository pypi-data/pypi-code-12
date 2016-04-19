# coding: utf8

from appdirs import *
import platform
from .eikonError import *
from .tools import is_string_type

# global profile
profile = None


def set_app_id(app_id):
    """
    Set the application id.

    Parameters
    ----------
    app_id : string
        the application id

    Notes
    -----
    The application ID identifies your application on Thomson Reuters Platform.
    You can get an application ID using the Application ID generator. This App can
    be launched from TR Eikon Proxy welcome page.
    """
    global profile
    profile = Profile(app_id)


def get_profile():
    """
    Returns a Profile class containing the EPAID
    """
    if profile is None:
        raise EikonError('AppID is missing. Did you forget to call set_app_id()?')

    return profile


def get_scripting_proxy_port():
    """

    Returns the port used by the Scripting Proxy stored in a configuration file.

    """

    app_name = 'Eikon Scripting Proxy'
    app_author = 'Thomson Reuters'

    if platform.system() == 'Linux':
        path = user_config_dir(app_name, app_author, roaming=True)
    else:
        path = user_data_dir(app_name, app_author, roaming=True)

    # First test to read .portInUse file
    firstline = read_firstline_in_file(os.path.join(path, '.portInUse'))
    if firstline == '':
        print('Warning: file .portInUse was not found. Is Eikon Scripting Proxy running?')
        print('Defaulting to port 36036')
        # nothing was retrieved from .portInUse, try with scriptingProxy.conf file
        port = '36036'
    else:
        port = firstline.strip()
    return port


def read_firstline_in_file(filename):
    try:
        f = open(filename)
        first_line = f.readline()
        f.close()
        return first_line
    except IOError as e:
        print('I/O error({0}): {1}'.format(e.errno, e.strerror))
        return ''


class Profile(object):
    def __init__(self, application_id):
        """
        Initialization of the profile.

        :param application_id:
        :type application_id: StringTypes
        """
        if not is_string_type(application_id):
            raise AttributeError('application_id must be a string')

        self.application_id = application_id
        self.port = get_scripting_proxy_port()
        self.url = "http://localhost:{0}/api/v1/data".format(self.port)
        self.streaming_url = "ws://localhost:{0}/?".format(self.port)

    def get_application_id(self):
        """
        Returns the application id.
        """
        if not self.application_id:

            raise EikonError('EPAID not set')
        return self.application_id

    def get_url(self):
        """
        Returns the scripting proxy url.
        """
        return self.url

    def get_streaming_url(self):
        """
        Returns the streaming proxy url.
        """
        return self.streaming_url
