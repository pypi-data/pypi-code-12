# -*- coding: utf-8 -*-
from congo.conf import settings
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

def get_model(constant_name):

    constant_value = getattr(settings, constant_name)

    try:
        return django_apps.get_model(constant_value)
    except AttributeError:
        raise ImproperlyConfigured("%s needs to be defined in settings as 'app_label.model_name'" % constant_name)
    except ValueError:
        raise ImproperlyConfigured("%s must be of the form 'app_label.model_name'" % constant_name)
    except LookupError:
        raise ImproperlyConfigured("%s refers to model '%s' that has not been installed" % (constant_name, constant_value))

class Iter(object):
    def __init__(self, queryset):
        self.obj_dict = {}
        self.id_list = []
        for obj in queryset:
            self.id_list.append(obj.id)
            self.obj_dict[obj.id] = obj

    def __iter__(self):
        return iter(self.id_list)

    def __len__(self):
        return len(self.id_list)

    def _object_passes_test(self, attr, value, operator):
        if operator == 'eq':
            return attr == value
        elif operator == 'neq':
            return attr != value
        elif operator == 'gte':
            return attr >= value
        elif operator == 'gt':
            return attr > value
        elif operator == 'lte':
            return attr <= value
        elif operator == 'lt':
            return attr < value
        elif operator == 'in':
            return attr in value
        return False

    def get_object(self, obj_id):
        try:
            return self.obj_dict[int(obj_id)]
        except KeyError:
            return None

    def get_objects(self):
        return [self.obj_dict[obj_id] for obj_id in self.id_list]

    def get_nested_objects(self, attr):
        result = []
        for obj_id in self.id_list:
            if hasattr(self.obj_dict[obj_id], attr):
                nested_obj = getattr(self.obj_dict[obj_id], attr)
                if nested_obj not in result:
                    result.append(nested_obj)
        return result

    def get_objects_by_id_list(self, id_list):
        id_list = map(lambda obj_id: int(obj_id), id_list)
        result = []
        for obj_id in filter(lambda obj_id: int(obj_id) in id_list, self.id_list):
            result.append(self.obj_dict[obj_id])

        return result

    def get_object_by_attr(self, attr, value, operator = 'eq'):
        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            if hasattr(obj, attr):
                if self._object_passes_test(getattr(obj, attr), value, operator):
                    return obj
        return None

    def get_object_by_attrs(self, attrs):
        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            valid = True
            for attr_dict in attrs:
                attr = attr_dict['attr']
                value = attr_dict['value']
                operator = attr_dict.get('operator', 'eq')

                if hasattr(obj, attr):
                    if not self._object_passes_test(getattr(obj, attr), value, operator):
                        valid = False
                else:
                    valid = False
            if valid:
                return obj
        return None

    def get_objects_by_attr(self, attr, value, operator = "eq"):
        result = []

        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            if hasattr(obj, attr):
                if self._object_passes_test(getattr(obj, attr), value, operator):
                    result.append(obj)
        return result

    def get_objects_by_attrs(self, attrs):
        result = []

        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            valid = True
            for attr_dict in attrs:
                attr = attr_dict['attr']
                value = attr_dict['value']
                operator = attr_dict.get('operator', 'eq')

                if hasattr(obj, attr):
                    if not self._object_passes_test(getattr(obj, attr), value, operator):
                        valid = False
                else:
                    valid = False
            if valid:
                result.append(obj)
        return result

    def get_next(self, obj_id):
        try:
            return self.obj_dict[self.id_list[self.id_list.index(int(obj_id)) + 1]]
        except IndexError:
            return None

    def get_prev(self, obj_id):
        try:
            prev_id = self.id_list.index(int(obj_id)) - 1
            if prev_id >= 0:
                return self.obj_dict[self.id_list[prev_id]]
            else:
                return None
        except IndexError:
            return None

    def get_index(self, obj_id, count_from_1 = False):
        index = self.id_list.index(int(obj_id))
        return index + 1 if count_from_1 else index

class Tree(Iter):
    def __init__(self, query):
        self.obj_dict = {}
        self.id_list = []
        self.root_id_list = []
        self.child_id_dict = {}
        for obj in query:
            self.id_list.append(obj.id)
            self.obj_dict[obj.id] = obj
            if obj.parent_id:
                if obj.parent_id in self.child_id_dict:
                    self.child_id_dict[obj.parent_id].append(obj.id)
                else:
                    self.child_id_dict[obj.parent_id] = [obj.id]
            else:
                self.root_id_list.append(obj.id)

    def get_root(self, obj_id, get_self = False):
        obj = self.get_object(obj_id)
        if not obj:
            return None
        while obj.parent_id:
            obj = self.get_parent(obj.id)
        if obj.id != int(obj_id) or get_self:
            return obj
        else:
            return None

    def get_roots(self):
        return self.get_objects_by_id_list(self.root_id_list)

    def get_parent(self, obj_id, get_self = False):
        obj = self.get_object(obj_id)
        if not obj:
            return None
        if obj.parent_id:
            return self.get_object(obj.parent_id)
        else:
            if get_self:
                return obj
            else:
                return None

    def get_parents(self, obj_id, get_self = False, reverse = True):
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result
        if get_self:
            result.append(obj)
        while obj.parent_id:
            obj = self.get_parent(obj.id)
            if obj:
                result.append(obj)
            else:
                break
        if reverse:
            result.reverse()
        return result

    def get_children(self, obj_id, get_self = False, get_nested = False):
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result
        if get_self:
            result.append(obj)
        if obj.id in self.child_id_dict:
            if get_nested:
                for child_id in self.child_id_dict[obj.id]:
                    result.append(self.get_object(child_id))
                    result += self.get_children(child_id, get_nested = True)
            else:
                result += self.get_objects_by_id_list(self.child_id_dict[obj.id])
        return result

    def get_siblings(self, obj_id, get_self = False):
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result
        if obj.parent_id:
            result += filter(lambda x: x != obj or get_self, self.get_children(obj.parent_id))
        else:
            result += filter(lambda x: x != obj or get_self, self.get_roots())
        return result
