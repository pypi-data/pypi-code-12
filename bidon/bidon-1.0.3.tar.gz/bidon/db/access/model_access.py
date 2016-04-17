"""Contains ModelAccess class and helper methods."""
from bidon.util.date import local_now, utc_now
from .data_access import DataAccess, Upsert


class ModelAccess(DataAccess):
  """A model-based specialization of DataAccess

  Provides methods for CRUDing objects derived from bidon.db.model.ModelBase.
  """
  def _find_model(self, constructor, table_name, constraints=None, *, columns=None, order_by=None):
    """Calls DataAccess.find and passes the results to the given constructor."""
    data = self.find(table_name, constraints, columns=columns, order_by=order_by)
    return constructor(data) if data else None

  def _find_models(self, constructor, table_name, constraints=None, *, columns=None,
                   order_by=None, limiting=None):
    """Calls DataAccess.find_all and passes the results to the given constructor."""
    for record in self.find_all(table_name, constraints, columns=columns, order_by=order_by,
                                limiting=limiting):
      yield constructor(record)

  def find_model(self, constructor, constraints=None, *, columns=None, table_name=None,
                 order_by=None):
    """Specialization of DataAccess.find that returns a model instead of cursor object."""
    return self._find_model(constructor, table_name or constructor.table_name, constraints,
                            columns=columns, order_by=order_by)

  def find_models(self, constructor, constraints=None, *, columns=None, order_by=None,
                  limiting=None, table_name=None):
    """Specialization of DataAccess.find_all that returns models instead of cursor objects."""
    return self._find_models(
      constructor, table_name or constructor.table_name, constraints, columns=columns,
      order_by=order_by, limiting=limiting)

  def page_models(self, constructor, paging, constraints=None, *, columns=None, order_by=None):
    """Specialization of DataAccess.page that returns models instead of cursor objects."""
    records, count = self.page(constructor.table_name, paging, constraints, columns=columns,
                               order_by=order_by)
    return ([constructor(r) for r in records], count)

  def find_model_by_id(self, constructor, id_, *, columns=None):
    """Searches for a model by id, according to its class' primary_key_name.

    If primary_key_name is a tuple, id_ must be a tuple with a matching length.
    """
    return self.find_model(
      constructor, get_id_constraints(constructor.primary_key_name, id_), columns=columns)

  def refresh_model(self, model, *, overwrite=False):
    """Pulls the model's record from the database. If overwrite is True, the model values are
    overwritten and returns the model, otherwise a new model instance with the newer record is
    returned.
    """
    new_model = self.find_model_by_id(model.__class__, model.primary_key)
    if overwrite:
      model.update(new_model.to_dict(use_default_excludes=False))
      return model
    else:
      return new_model

  def update_model(self, model, *, include_keys=None):
    """Updates a model.

    :include_keys: if given, only updates the given attributes. Otherwise, updates all non-id
    attributes.
    """
    id_constraints = get_model_id_constraints(model)

    if include_keys is None:
      include_keys = set(
        model.attrs.keys()).difference(model.exclude_keys_sql).difference(id_constraints.keys())

    # If include_keys was not null but was empty
    if not include_keys:
      return model

    values = model.to_dict(include_keys=include_keys)
    returnings = []

    _, updated_ts = model.timestamps if model.timestamps else (None, None)

    if updated_ts and updated_ts not in values:
      values[updated_ts] = utc_now() if self.core.supports_timezones else local_now()
      returnings.append(updated_ts)

    returning = ", ".join(returnings)
    cr = self.update(model.table_name, values, id_constraints, returning=returning)

    if returning and self.core.supports_returning_syntax:
      rec = cr.fetchone()
      for idx, attr_name in enumerate(returnings):
        setattr(model, attr_name, rec[idx])

    return model

  def insert_model(self, model, *, upsert=None):
    """Inserts a record for the given model.

    If model's primary key is auto, the primary key will be set appropriately.
    """
    pkname = model.primary_key_name
    include_keys = set(model.attrs.keys()).difference(model.exclude_keys_sql)

    if model.primary_key_is_auto:
      if pkname in include_keys:
        include_keys.remove(pkname)
    else:
      if isinstance(pkname, str):
        include_keys.add(pkname)
      else:
        include_keys.update(set(pkname))

    data = model.to_dict(include_keys=include_keys)
    returnings = []

    if model.primary_key_is_auto:
      returnings.append(pkname)
    if model.timestamps:
      returnings.extend(ts_name for ts_name in model.timestamps if ts_name)

    returning = ", ".join(returnings)
    cr = self.insert(model.table_name, data, returning=returning, upsert=upsert)

    if self.core.supports_returning_syntax:
      if returning:
        rec = cr.fetchone()
        if rec:
          for idx, attr_name in enumerate(returnings):
            setattr(model, attr_name, rec[idx])
    else:
      if model.primary_key_is_auto:
        setattr(model, model.primary_key_name, cr.lastrowid)

    return model

  def delete_model(self, model_or_type, id_=None):
    """Deletes a model.

    :model_or_type: if a model, delete that model. If it is a ModelBase subclass, id_ must be
    specified, and the associated record is deleted.
    """
    if not id_:
      constraints = get_model_id_constraints(model_or_type)
    else:
      constraints = get_id_constraints(model_or_type.primary_key_name, id_)
    self.delete(model_or_type.table_name, constraints)

    return model_or_type

  def find_or_build(self, constructor, props):
    """Looks for a model that matches the given dictionary constraints. If it is not found, a new
    model of the given type is constructed and returned.
    """
    model = self.find_model(constructor, props)
    return model or constructor(**props)

  def find_or_create(self, constructor, props, *, comp=None):
    """Looks for a model taht matches the given dictionary constraints. If it is not found, a new
    model of the given type is created and saved to the database, then returned.
    """
    model = self.find_model(constructor, comp or props)
    if model is None:
      model = constructor(**props)
      self.insert_model(model)
    return model

  def find_or_upsert(self, constructor, props, *, comp=None, return_status=False):
    """This finds or upserts a model with an auto primary key, and is a bit more flexible than
    find_or_create.

    First it looks for the model matching either comp, or props if comp is None.

    If not found, it will try to upsert the model, doing nothing. If the returned model is new,
    meaning it's primary key is not set, then the upsert was unable to create the model, meaning
    there was a conflict. If there is a conflict, find model is run again, and this time it
    will succeed*. Otherwise, the constructed model is returned.

    *this is not entirely true. It's possible that the upsert returns with None, meaning that a
    record was created between the first find and the upsert, and then deleted between the upsert
    and the second find. This situation is out of the scope of this method. A possible solution
    would be to repeat the find/uspert cycle until a model can be returned, but I'm going to avoid
    that for simplicty for now.

    :param constructor: the model constructor
    :param props: the properties to construct the model with if not found
    :param comp: the properties to search for the model with. If None, props is used
    :param return_status: if True, a 2-tuple of (model, status) is returned, where status is what
                          occurred with the model. Either 'found', 'created' or 'duplicate'.
    """
    model = self.find_model(constructor, comp or props)
    status = _UPSERT_STATUS_FOUND

    if model is None:
      model = constructor(**props)
      status = _UPSERT_STATUS_CREATED
      self.insert_model(model, upsert=Upsert(Upsert.DO_NOTHING))
      if model.is_new:
        model = self.find_model(constructor, comp or props)
        status = _UPSERT_STATUS_DUPLICATE

    if return_status:
      return (model, status)
    else:
      return model


def get_model_id_constraints(model):
  """Returns constraints to target a specific model."""
  pkname = model.primary_key_name
  pkey = model.primary_key
  return get_id_constraints(pkname, pkey)


def get_id_constraints(pkname, pkey):
  """Returns primary key consraints.

  :pkname: if a string, returns a dict with pkname=pkey. pkname and pkey must be enumerables of
  matching length.
  """
  if isinstance(pkname, str):
    return {pkname: pkey}
  else:
    return dict(zip(pkname, pkey))


_UPSERT_STATUS_FOUND = "found"
_UPSERT_STATUS_CREATED = "created"
_UPSERT_STATUS_DUPLICATE = "duplicate"
