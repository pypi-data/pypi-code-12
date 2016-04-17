"""Contains the TransferTracker class and related classes and functions."""
from bidon.db.access import ModelAccess, ModelBase
from bidon.util import utc_now


__all__ = ["TransferTracker"]


class Relation(ModelBase):
  """A model that keeps track of table transfer completions."""
  table_name = "relations"
  timestamps = None
  attrs = dict(name=None, completed_at=None)


class Transfer(ModelBase):
  """A model that relates the old ID of a moved model to its new ID."""
  table_name = "transfers"
  timestamps = None
  primary_key_name = ("relation_id", "old_id")
  primary_key_is_auto = False
  attrs = dict(relation_id=None, old_id=None, new_id=None)


class TransferTracker(object):
  """The TransferTracker class keeps track of data being transferred from one database or table to
  another. Specifically, it makes it possible to record the old and new ids for a relation, and
  query for the new ID.
  """
  def __init__(self, data_access_core):
    """Initialize the TransferTracker class."""
    self.data_access = ModelAccess(data_access_core)

  def open(self, autocommit=False):
    """Call-through to data_access.open."""
    self.data_access.open(autocommit=autocommit)
    return self

  def close(self, commit=True):
    """Call-through to data_access.close."""
    self.data_access.close(commit=commit)
    return self

  def commit(self):
    """Call-through to data_access.commit."""
    self.data_access.commit()
    return self

  def rollback(self):
    """Call-through to data_access.rollback."""
    self.data_access.rollback()
    return self

  def setup(self):
    """Creates the default relations and transfers tables. The SQL used may not work on all
    databases. (It was written for SQLite3)
    """
    cmds = [
      """
        create table if not exists relations (
          id integer not null primary key,
          name text not null unique,
          completed_at datetime
        );
      """,
      """
        create table if not exists transfers (
          relation_id integer not null references relations (id) on delete cascade,
          old_id text not null,
          new_id text,
          primary key (relation_id, old_id)
        );
      """,
      """
        create index if not exists transfers_relation_id_idx on transfers (relation_id);
      """
    ]

    for cmd in cmds:
      self.data_access.execute(cmd)
    self.data_access.commit()
    return self

  def cleanup(self):
    """Cleanup the database, calling vacuum and analyze."""
    self.data_access.execute("vacuum")
    self.data_access.execute("analyze")

  def reset(self, relation_name=None):
    """Reset the transfer info for a particular relation, or if none is given, for all relations.
    """
    if relation_name is not None:
      self.data_access.delete("relations", dict(name=relation_name))
    else:
      self.data_access.delete("relations", "1=1")
    return self

  def start_transfer(self, relation_name):
    """Write records to the data source indicating that a transfer has been started for a particular
    relation.
    """
    self.reset(relation_name)
    relation = Relation(name=relation_name)
    self.data_access.insert_model(relation)
    return relation

  def register_transfer(self, relation, old_id, new_id):
    """Register the old and new ids for a particular record in a relation."""
    transfer = Transfer(relation_id=relation.id, old_id=old_id, new_id=new_id)
    self.data_access.insert_model(transfer)
    return transfer

  def complete_transfer(self, relation, cleanup=True):
    """Write records to the data source indicating that a transfer has been completed for a
    particular relation.
    """
    relation.completed_at = utc_now().isoformat()
    self.data_access.update_model(relation)
    if cleanup:
      self.cleanup()
    return relation

  def is_transfer_complete(self, relation_name):
    """Checks to see if a tansfer has been completed."""
    phold = self.data_access.sql_writer.to_placeholder()
    return self.data_access.find_model(
      Relation,
      ("name = {0} and completed_at is not null".format(phold), [relation_name])) is not None

  def get_new_id(self, relation_name, old_id, strict=False):
    """Given a relation name and its old ID, get the new ID for a relation. If strict is true, an
    error is thrown if no record is found for the relation and old ID.
    """
    record = self.data_access.find(
      "relations as r inner join transfers as t on r.id = t.relation_id",
      (("r.name", relation_name), ("t.old_id", old_id)),
      columns="new_id")
    if record:
      return record[0]
    else:
      if strict:
        raise KeyError("{0} with id {1} not found".format(relation_name, old_id))

  def id_getter(self, relation_name, strict=False):
    """Returns a function that accepts an old_id and returns the new ID for the enclosed relation
    name."""
    def get_id(old_id):
      """Get the new ID for the enclosed relation, given an old ID."""
      return self.get_new_id(relation_name, old_id, strict)
    return get_id
