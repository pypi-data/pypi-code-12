"""
.. module:: python-xirsys.objects
   :synopsis: python_xirsys Object Definitions

   See http://xirsys.com/api/

.. moduleauthor:: Alexander Kavanaugh (@kavdev)

"""

__all__ = ["SignalingServer", "ICEServer", "Domain", "Application", "Room"]


class XirSysObject(object):

    def __init__(self, connection):
        self.connection = connection

    def __str__(self):
        return getattr(self, self.description_attribute)

    def __repr__(self):
        return "<{classname} [{description}]>".format(classname=str(self.__class__.__name__), description=str(self))

    def __eq__(self, other):
        """ Allow string comparison by the ``description_attribute``."""

        return ((isinstance(other, self.__class__) and self.__dict__ == other.__dict__)) or other == str(self)

    def __ne__(self, other):
        return not self.__eq__(other)


class SignalingServer(XirSysObject):
    path = "/signal"
    description_attribute = "address"

    def __init__(self, address, *args, **kwargs):
        self.address = address

        super().__init__(*args, **kwargs)

    @classmethod
    def generate_token(cls, connection, domain, application, room, secure=True):
        """
        This call grabs a secure WebSocket token from XirSys, which ensures that WebSocket data
        usage is restricted to only the application’s owner. The tokens themselves are encrypted,
        which is expected by the WebSocket endpoints and required to set up a successful
        connection. Invalid tokens or incomplete data within tokens result in an unsuccessful
        WebSocket connection. This is typically called whenever users have to interact with our
        signaling server.

        """

        return connection.post(path=SignalingServer.path + "/token", domain=domain, application=application, room=room, secure=secure)["token"]

    @classmethod
    def list_all(cls, connection):
        """This grabs a list of XirSys WebSocket servers. This is typically only called with very rare use cases."""

        signaling_server_address = connection.post(path=SignalingServer.path + "/list")["value"]
        return SignalingServer(connection=connection, address=signaling_server_address)


class ICEServer(XirSysObject):
    path = "/ice"
    description_attribute = "url"

    def __init__(self, url, server_type, username=None, credential=None, *args, **kwargs):
        self.url = url
        self.server_type = server_type
        self.username = username
        self.credential = credential

        super().__init__(*args, **kwargs)

    @classmethod
    def list_all(cls, connection, domain, application, room, secure=True, timeout=30):
        """
        This is typically called when a user has to authenticate with our STUN and TURN servers.
        This follows a similar path to acquiring a WebSocket token, with the major difference being
        that — instead of returning a token — the request returns an array of WebRTC STUN and TURN
        servers.

        """

        server_list = connection.post(path=ICEServer.path, domain=domain, application=application, room=room, secure=secure, timeout=timeout)["iceServers"]

        iceserver_list = []

        for server in server_list:
            iceserver_list.append(ICEServer(connection=connection,
                                            url=server["url"],
                                            server_type=server["url"].split(":", 1)[0],
                                            username=server.get("username"),
                                            credential=server.get("credential")))

        return iceserver_list


class Domain(XirSysObject):
    path = "/domain"
    description_attribute = "name"

    def __init__(self, name, *args, **kwargs):
        self.name = name

        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, connection, domain):
        """Add a domain to XirSys."""

        connection.post(path=Domain.path, domain=domain)
        return Domain(connection=connection, name=domain)

    def delete(self):
        """Delete a XirSys domain."""

        self.connection.delete(path=Domain.path, domain=self)

    @classmethod
    def list_all(cls, connection):
        """List XirSys domains."""

        domain_names = connection.get(path=Domain.path)
        return [Domain(connection=connection, name=domain_name) for domain_name in domain_names]

    @property
    def applications(self):
        return Application.list_all(connection=self.connection, domain=self)


class Application(XirSysObject):
    path = "/application"
    description_attribute = "name"

    def __init__(self, name, domain, *args, **kwargs):
        self.name = name
        self.domain = domain

        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, connection, domain, application):
        """Create a XirSys application."""

        connection.post(path=Application.path, domain=domain, application=application)
        return Application(connection=connection, name=application, domain=domain)

    def delete(self):
        """Delete a XirSys application."""

        self.connection.delete(path=Application.path, domain=self.domain, application=self)

    @classmethod
    def list_all(cls, connection, domain):
        """List XirSys applications."""

        application_names = connection.get(path=Application.path, domain=domain)
        return [Application(connection=connection, name=application_name, domain=domain) for application_name in application_names]

    @property
    def rooms(self):
        return Room.list_all(connection=self.connection, domain=self.domain, application=self)


class Room(XirSysObject):
    path = "/room"
    description_attribute = "name"

    def __init__(self, name, domain, application, *args, **kwargs):
        self.name = name
        self.domain = domain
        self.application = application

        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, connection, domain, application, room):
        """Create a XirSys room."""

        connection.post(path=Room.path, domain=domain, application=application, room=room)
        return Room(connection=connection, name=room, domain=domain, application=application)

    def delete(self):
        """Delete a XirSys application."""

        self.connection.delete(path=Room.path, domain=self.domain, application=self.application, room=self)

    @classmethod
    def list_all(cls, connection, domain, application):
        """List XirSys applications."""

        room_names = connection.get(path=Room.path, domain=domain, application=application)
        return [Room(connection=connection, name=room_name, domain=domain, application=application) for room_name in room_names]
