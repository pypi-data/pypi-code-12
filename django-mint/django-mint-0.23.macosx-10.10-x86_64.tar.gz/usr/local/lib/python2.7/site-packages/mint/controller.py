from django.db import models
from mint import mixins
from mint import exceptions
from mint import serializers
from django.conf import settings
from django.http import QueryDict
import simplejson


class EmptyModel(models.Model):
    class Meta:
        app_label = '_mint'


class Controller(mixins.RootMixin, mixins.IDMixin, mixins.ManyToManyMixin, mixins.FieldMixin):
    model = EmptyModel
    related = []
    serializer = serializers.Serializer

    def __init__(self, request):
        self.request = request
        self.original_model = self.model
        self.args = {}
        self.open_args()
        if hasattr(settings, 'REST_SERIALIZER'):
            self.serializer = __import__(getattr(settings, 'REST_SERIALIZER'))

    def open_model(self, idx=None):
        if idx:
            try:
                self.model = self.model.objects.get(pk=idx)
            except self.model.DoesNotExist:
                raise exceptions.HttpNotFound("Could not find %s with id %d" % (self.__class__.__name__, int(idx)))
        else:
            self.model = self.model.objects.all()

    def open_args(self):
        if self.request.method == 'GET':
            self.args = self.request.GET.dict()
        elif self.request.method == 'POST':
            if 'application/json' in self.request.META['CONTENT_TYPE']:
                if len(self.request.body) > 0:
                    self.args = simplejson.loads(self.request.body)
            else:
                self.args = self.request.POST.dict()
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            if 'application/json' in self.request.META['CONTENT_TYPE']:
                if len(self.request.body) > 0:
                    self.args = simplejson.loads(self.request.body)
            else:
                self.args = QueryDict(self.request.body).dict()

    def has_action(self, action):
        return hasattr(self, action)

    def exec_root(self):
        if self.request.method not in self._root_methods():
            raise exceptions.HttpNotAllowed("Invalid method (%s) for this controller (%s)."
                                            % (self.request.method, self.__class__.__name__))
        return self._root_methods()[self.request.method]()

    def exec_id(self, idx):
        if self.request.method not in self._id_methods():
            raise exceptions.HttpNotAllowed("Invalid method (%s) for this controller (%s)."
                                            % (self.request.method, self.__class__.__name__))
        self.open_model(idx)
        return self._id_methods()[self.request.method]()

    def exec_action(self, action, idx=None):
        if not hasattr(self, action):
            raise exceptions.HttpNotAllowed("Invalid action (%s) for this controller (%s)."
                                            % (action, self.__class__.__name__))
        return getattr(self, action)()

    def exec_m2m(self, idx, field):
        if self.request.method not in self._m2m_methods():
            raise exceptions.HttpNotAllowed("Invalid method (%s) for this controller (%s)."
                                            % (self.request.method, self.__class__.__name__))
        return self._m2m_methods()[self.request.method](field)