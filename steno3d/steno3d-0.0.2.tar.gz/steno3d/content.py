"""content.py contains the base class for everything users can create
in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pformat
import properties

from . import client


class UserContent(properties.PropertyClass):
    """Base class for everything user creates and uploads in steno3d"""
    title = properties.String(
        'Title of the model.',
        default=''
    )
    description = properties.String(
        'Description of the model.',
        default=''
    )
    opts = None

    def __init__(self, **kwargs):
        super(UserContent, self).__init__(**kwargs)
        self._upload_data = None

    @properties.classproperty
    @classmethod
    def _resource_class(cls):
        """name of the class of resource"""
        if getattr(cls, '__resource_class', None) is None:
            cls.__resource_class = cls.__name__.lower()
        return cls.__resource_class

    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/{className}'.format(
                className=cls._resource_class
            )
        return cls.__model_api_location

    # @property
    # def _dirty(self):
    #     """Set containing unsaved properties"""
    #     if not hasattr(self, '__dirty'):
    #         self.__dirty = set()
    #     return self.__dirty

    @classmethod
    def _url_api_from_uid(cls, uid):
        """Get api location object from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=client.Comms.url,
            mapi=cls._model_api_location,
            uid=uid)
        return url

    @classmethod
    def _url_view_from_uid(cls, uid):
        """Get full url from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=client.Comms.base_url,
            mapi=cls._model_api_location,
            uid=uid)
        return url

    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        return True

    @property
    def _contentdata(self):
        """Get basic data about the content"""
        datadict = {
            'title': self.title,
            'description': self.description
        }
        if getattr(self, 'opts', None) is not None:
            datadict['meta'] = self.opts.as_json()
        return datadict

    @property
    def _reqdata(self):
        """Get the required longUids"""
        return {}

    @property
    def _files(self):
        """Get the file information"""
        return {}

    @property
    def _datadict(self):
        """Combine metadata and requirement information for upload"""
        datadict = self._contentdata.copy()
        datadict.update(self._reqdata)
        return datadict

    @property
    def long_uid(self):
        """longUid of uploaded data"""
        if getattr(self, '_upload_data', None) is not None:
            return self._upload_data['longUid']
        else:
            return None

    @property
    def uid(self):
        """uid of uploaded data"""
        if getattr(self, '_upload_data', None) is not None:
            return self._upload_data['uid']
        else:
            return None

    @property
    def url_api(self):
        """api location of uploaded data"""
        uid = self.uid
        if uid is not None:
            return self._url_api_from_uid(uid)
        else:
            return None

    @property
    def url_view(self):
        """full url of uploaded data"""
        uid = self.uid
        if uid is not None:
            return self._url_view_from_uid(uid)
        else:
            return None

    def _upload(self, force=True, pause=False):
        """upload the UserContent to the endpoint selected at login"""
        if getattr(self, '_upload_data', None) is not None and not force:
            return self.url_view

        assert self.validate()

        datadict = self._datadict
        files = self._files
        client.pause()
        req = client.post(
            self._model_api_location,
            data=datadict if datadict else tuple(),
            files=files if files else tuple(),
        )

        if isinstance(req, list):
            for rq in req:
                if rq.status_code != 200:
                    try:
                        resp = pformat(rq.json())
                    except ValueError:
                        resp = rq

                    raise Exception(
                        'Upload failed: {location}'.format(
                            location=self._model_api_location,
                        ) +
                        '\ndata: {datadict}\nfiles: {filedict}'.format(
                            datadict=pformat(datadict),
                            filedict=pformat(files),
                        ) +
                        '\nresponse: {response}'.format(
                            response=resp,
                        )
                    )
            self._upload_data = [rq.json() for rq in req]
        else:
            if req.status_code != 200:
                try:
                    resp = pformat(req.json())
                except ValueError:
                    resp = req
                raise Exception(
                    'Upload failed: {location}'.format(
                        location=self._model_api_location,
                    ) +
                    '\ndata: {datadict}\nfiles: {filedict}'.format(
                        datadict=pformat(datadict),
                        filedict=pformat(files),
                    ) +
                    '\nresponse: {response}'.format(
                        response=resp,
                    )
                )
            self._upload_data = req.json()

        if pause:
            client.pause()

        return self.url_view

    def plot(self):
        """Display the 3D representation of the content"""
        if getattr(self, '_upload_data', None) is None:
            raise Exception('Plotting failed: resource not uploaded - '
                            'please upload() first.')
        return client.plot(self.url_view)

    @property
    def json_after_upload(self):
        """Return a JSON representation of the object,
        uploading if necessary.
        """
        if getattr(self, '_upload_data', None) is None:
            self._upload()
        return self.json

    @property
    def json(self):
        """Return a JSON representation of the object"""
        return getattr(self, '_upload_data', None)

    def grant_access(self, userid):
        """Grant a user access to this object"""
        if userid.isalnum():
            userid = 'User:' + userid
        resp = client.add_edit_permissions(self, userid)
        return client.check_acl_response(resp)

    def revoke_access(self, userid):
        """Revoke a user's access to this object"""
        if userid.isalnum():
            userid = 'User:' + userid
        resp = client.remove_permissions(self, userid)
        return client.check_acl_response(resp)

    def add_view_permissions(self, accessor):
        """Add view permissions to this object for an accessor"""
        client.pause()
        resp = client.add_view_permissions(self, accessor)
        if resp.status_code == 200:
            return True
        return client.check_acl_response(resp)
