from mint import utils
from mint import exceptions
from django.contrib.auth.models import User as AuthUser


class BaseMixin(object):
    def _filter(self, queryset):
        return queryset

    def _pre_delete(self, model):
        pass

    def _post_delete(self):
        pass

    def _pre_create(self, model):
        pass

    def _post_create(self, model):
        pass

    def _pre_update(self, model):
        pass

    def _post_update(self, model):
        pass

    def _pre_return(self, model, out):
        pass

    def _pre_save(self, model):
        pass

    def _post_save(self, model):
        pass

    def _can_delete(self):
        return False

    def _can_create(self):
        return True

    def _iterate_and_serialize(self, model):
        out = []
        for m in model:
            out.append(self._serialize(m))
        return out

    def _get_serializer_fields(self):
        return []

    def _serialize(self, model):
        fields = self._get_serializer_fields()
        me = self.serializer(model, fields).pack()
        self._pre_return(model, me)
        return me

    def _get_name(self):
        return self.__class__.__name__

    def _format_plural(self, out, name=None):
        if not name:
            name = utils.camel_to_underscore(self._get_name())
        if name[-1:] != "s":
            name = "%ss" % name
        return {name: out}

    def _format_singular(self, out, name=None):
        if not name:
            name = utils.camel_to_underscore(self._get_name())
        if name[-1:] == "s":
            name = name[:-1]
        return {name: out}


class RootMixin(BaseMixin):
    def _get_root(self):
        self.model = self._filter(self.model)
        return self._format_plural(self._iterate_and_serialize(self.model))

    def _post_root(self):
        if not self._can_create():
            raise exceptions.HttpUnauthorized("You cannot delete this object")
        m = self.original_model()
        for key, value in self.args.items():
            if key == 'id':
                continue
            if hasattr(m, key):
                my_type = m._meta.get_field(key).get_internal_type()
                if my_type in ('DateTimeField', 'DateField'):
                    if value:
                        value = utils.datetime_from_string(value)
                elif hasattr(self.model, 'get_%s_display' % key):
                    values = dict((key, value) for (value, key) in self.model._meta.get_field(key).choices)
                    if value not in values:
                        raise exceptions.ParameterError("Invalid value for '%s' parameter.")
                    value = values[value]
                setattr(m, key, value)
        self._pre_create(m)
        self._pre_save(m)
        m.save()
        self._post_save(m)
        self._post_create(m)
        return self._format_singular(self._serialize(m))

    def _put_root(self):
        raise exceptions.HttpNotAllowed("Cannot PUT on root context")

    def _delete_root(self):
        raise exceptions.HttpNotAllowed("Cannot DELETE on root context")

    def _root_methods(self):
        return {
            'GET': self._get_root,
            'POST': self._post_root,
            'PUT': self._put_root,
            'DELETE': self._delete_root,
        }


class IDMixin(BaseMixin):
    def _get_by_id(self):
        return self._format_singular(self._serialize(self.model))

    def _post_by_id(self):
        raise exceptions.HttpNotAllowed("Cannot POST by ID")

    def _put_by_id(self):
        self._pre_update(self.model)
        for key, value in self.args.items():
            if key == 'id':
                continue
            if hasattr(self.model, key):
                my_type = self.model._meta.get_field(key).get_internal_type()
                if my_type in ('DateTimeField', 'DateField'):
                    value = utils.datetime_from_string(value)
                elif hasattr(self.model, 'get_%s_display' % key):
                    values = dict((key, value) for (value, key) in self.model._meta.get_field(key).choices)
                    if value not in values:
                        raise exceptions.ParameterError("Invalid value for '%s' parameter.")
                    value = values[value]
                setattr(self.model, key, value)
        self._pre_save(self.model)
        self.model.save()
        self._post_save(self.model)
        self._post_update(self.model)
        return self._format_singular(self._serialize(self.model))

    def _delete_by_id(self):
        if not self._can_delete():
            raise exceptions.HttpUnauthorized("You cannot delete this object")
        self._pre_delete(self.model)
        self.model.delete()
        self._post_delete()
        return True

    def _id_methods(self):
        return {
            'GET': self._get_by_id,
            'POST': self._post_by_id,
            'PUT': self._put_by_id,
            'DELETE': self._delete_by_id,
        }


class ManyToManyMixin(BaseMixin):
    def _get_m2m_field(self, field):
        model = getattr(self.model, field).all()
        return self._format_plural(self._iterate_and_serialize(model), name=field)

    def _post_m2m_field(self, field):
        instance = getattr(self.model, field)
        m = instance.model()
        if isinstance(m, AuthUser):
            if not hasattr(self, '_create_user'):
                raise AttributeError("Trying to create new user but controller does not implement 'create_user' "
                                     "method.")
            m = getattr(self, '_create_user')()
            instance.add(m)
            return self._format_singular(self._serialize(m), name=field)
        else:
            for key, value in self.args.items():
                if key == 'id':
                    continue
                if hasattr(m, key):
                    my_type = m._meta.get_field(key).get_internal_type()
                    if my_type in ('DateTimeField', 'DateField'):
                        value = utils.datetime_from_string(value)
                    setattr(m, key, value)
            self._pre_save(m)
            m.save()
            instance.add(m)
            self._post_save(m)
            return self._format_singular(self._serialize(m), name=field)

    def _put_m2m_field(self, field):
        raise exceptions.HttpNotAllowed("Cannot PUT on a Many to Many Field")

    def _delete_m2m_field(self, field):
        raise exceptions.HttpNotAllowed("Cannot DELETE on a Many to Many Field")

    def _m2m_methods(self):
        return {
            'GET': self._get_m2m_field,
            'POST': self._post_m2m_field,
            'PUT': self._put_m2m_field,
            'DELETE': self._delete_m2m_field,
        }


class FieldMixin(object):
    def _has_field(self, name):
        if 'fields' not in self.args:
            return True
        fields = self.args['fields'].split(",")
        return name in fields
