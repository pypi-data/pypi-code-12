
import urllib
from figure import api_requestor, error


class APIResource(object):

    @classmethod
    def class_name(cls):
        if cls == APIResource:
            raise NotImplementedError(
                'APIResource is an abstract class.  You should perform '
                'actions on its subclasses (e.g. Portrait, Photobooth)')
        return str(urllib.quote_plus(cls.__name__.lower()))

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return "/%ss/" % (cls_name,)

    @classmethod
    def instance_url(cls, id):
        if not id:
            raise error.InvalidRequestError(
                'Could not determine which URL to request: %s instance '
                'has invalid ID: %r' % (type(cls).__name__, id), 'id')
        base = cls.class_url()
        extn = urllib.quote_plus(id)
        return "%s%s/" % (base, extn)


class RetrievableAPIResource(APIResource):

    @classmethod
    def get(cls, id, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = cls.instance_url(id)
        return requestor.request('get', url, **params)

class ListableAPIResource(APIResource):

    @classmethod
    def get_all(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = cls.class_url()
        return requestor.request('get', url, **params)


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = cls.class_url()
        return requestor.request('post', url, **params)


class EditableAPIResource(APIResource):

    @classmethod
    def edit(cls, id, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = cls.instance_url(id)
        return requestor.request('put', url, **params)


class DeletableAPIResource(APIResource):

    @classmethod
    def delete(cls, id, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = cls.instance_url(id)
        return requestor.request('delete', url, **params)


# API objects

class Photobooth(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
                 DeletableAPIResource):
    pass


class Place(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class Event(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class TicketTemplate(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):

    @classmethod
    def preview(cls, id, token=None, **params):
       requestor = api_requestor.APIRequestor(token)
       url = '%s/%s' % (cls.instance_url(id), 'preview')
       return requestor.request('get', url, **params)


class Text(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class TextVariable(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class Image(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class ImageVariable(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
            DeletableAPIResource):
    pass


class Portrait(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
               DeletableAPIResource):

    @classmethod
    def get_all_public(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/%s' % (cls.class_url(), 'public')
        return requestor.request('get', url, **params)


class PosterOrder(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
               DeletableAPIResource):
    pass


class WifiNetwork(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
               DeletableAPIResource):
    pass


class CodeList(APIResource):

    @classmethod
    def claim(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = 'codelist/claim/'
        return requestor.request('post', url, **params)

class User(RetrievableAPIResource, CreateableAPIResource, ListableAPIResource, EditableAPIResource,
               DeletableAPIResource):

    @classmethod
    def me(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/me' % cls.class_url()
        return requestor.request('get', url, **params)

    @classmethod
    def edit_me(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/me' % cls.class_url()
        return requestor.request('put', url, **params)

    @classmethod
    def edit_my_password(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/me/password/reset' % cls.class_url()
        return requestor.request('post', url, **params)

    @classmethod
    def register(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/register' % cls.class_url()
        return requestor.request('post', url, **params)

    @classmethod
    def reset_password(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/password/reset' % cls.class_url()
        return requestor.request('post', url, **params)

    @classmethod
    def set_new_password(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/password/reset/confirm/' % cls.class_url()
        return requestor.request('post', url, **params)


class Auth(APIResource):

    @classmethod
    def login(cls, token=None, **params):
        requestor = api_requestor.APIRequestor(token)
        url = '%s/token' % cls.class_url()
        return requestor.request('post', url, **params)



