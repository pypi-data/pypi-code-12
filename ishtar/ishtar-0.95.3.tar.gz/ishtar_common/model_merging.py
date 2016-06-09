# from https://djangosnippets.org/snippets/2283/

from django.db import transaction
from django.db.models import get_models, Model
from django.contrib.contenttypes.generic import GenericForeignKey


@transaction.commit_on_success
def merge_model_objects(primary_object, alias_objects=[], keep_old=False):
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls,
    etc.) and migrate all of the related fields from the alias objects to the
    primary object.

    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    MERGE_FIELDS = ('merge_candidate', 'merge_exclusion')

    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, Model):
        raise TypeError('Only django.db.models.Model subclasses can be merged')

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError('Only models of same class can be merged')

    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should
    # provide a similar
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    for model in get_models():
        for field_name, field in filter(lambda x: isinstance(
                x[1], GenericForeignKey), model.__dict__.iteritems()):
            generic_fields.append(field)

    blank_local_fields = set()
    for field in primary_object._meta.local_fields:
        value = getattr(primary_object, field.attname)
        # string fields with only spaces are empty fields
        if isinstance(value, unicode) or isinstance(value, str):
            value = value.strip()
        if value in [None, '']:
            blank_local_fields.add(field.attname)

    # Loop through all alias objects and migrate their data to the primary
    # object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary
        # object.
        for related_object in alias_object._meta.get_all_related_objects():
            # The variable name on the alias_object model.
            alias_varname = related_object.get_accessor_name()
            # The variable name on the related model.
            obj_varname = related_object.field.name
            related_objects = getattr(alias_object, alias_varname)
            for obj in related_objects.all():
                setattr(obj, obj_varname, primary_object)
                obj.save()

        # Migrate all many to many references from alias object to primary
        # object.
        related_many_objects = \
            alias_object._meta.get_all_related_many_to_many_objects()
        related_many_object_names = set()
        for related_many_object in related_many_objects:
            alias_varname = related_many_object.get_accessor_name()
            obj_varname = related_many_object.field.name
            if alias_varname in MERGE_FIELDS or obj_varname in MERGE_FIELDS:
                continue

            if alias_varname is not None:
                # standard case
                related_many_objects = getattr(
                    alias_object, alias_varname).all()
                related_many_object_names.add(alias_varname)
            else:
                # special case, symmetrical relation, no reverse accessor
                related_many_objects = getattr(alias_object, obj_varname).all()
                related_many_object_names.add(obj_varname)
            for obj in related_many_objects.all():
                getattr(obj, obj_varname).remove(alias_object)
                getattr(obj, obj_varname).add(primary_object)

        # Migrate local many to many references from alias object to primary
        # object.
        for many_to_many_object in alias_object._meta.many_to_many:
            alias_varname = many_to_many_object.get_attname()
            if alias_varname in related_many_object_names or \
               alias_varname in MERGE_FIELDS:
                continue

            many_to_many_objects = getattr(alias_object, alias_varname).all()
            if alias_varname in blank_local_fields:
                blank_local_fields.pop(alias_varname)
            for obj in many_to_many_objects.all():
                getattr(alias_object, alias_varname).remove(obj)
                getattr(primary_object, alias_varname).add(obj)

        # Migrate all generic foreign key references from alias object to
        # primary object.
        for field in generic_fields:
            filter_kwargs = {}
            filter_kwargs[field.fk_field] = alias_object._get_pk_val()
            filter_kwargs[field.ct_field] = field.get_content_type(
                alias_object)
            for generic_related_object in field.model.objects.filter(
                    **filter_kwargs):
                setattr(generic_related_object, field.name, primary_object)
                generic_related_object.save()

        # Try to fill all missing values in primary object by values of
        # duplicates
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, '']:
                setattr(primary_object, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

        if not keep_old:
            alias_object.delete()
    primary_object.save()
    return primary_object
