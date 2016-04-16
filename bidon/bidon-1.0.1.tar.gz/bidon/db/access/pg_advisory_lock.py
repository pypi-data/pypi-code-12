"""This module contains methods for working with Postgres advisory locks."""
from contextlib import contextmanager
from enum import Enum


__all__ = ["LockMode", "lock_key", "obtain_lock", "release_lock", "advisory_lock"]


class LockMode(Enum):
  """Contains the options for how to perform Postgres advisory locks."""
  wait = 0x01
  skip = 0x02
  error = 0x04


def lock_key(group_id, item_id, group_width=8):
  """Creates a lock ID where the lower bits are the group ID and the upper bits
  are the item ID. This allows the use of a bigint namespace for items, with a
  limited space for grouping.

  :group_id: an integer identifying the group. Must be less than
             2 ^ :group_width:
  :item_id: item_id an integer. must be less than 2 ^ (63 - :group_width:) - 1
  :gropu_width: the number of bits to reserve for the group ID.
  """
  if group_id >= (1 << group_width):
    raise Exception("Group ID is too big")
  if item_id >= (1 << (63 - group_width)) - 1:
    raise Exception("Item ID is too big")
  return (item_id << group_width) | group_id


def obtain_lock(dax, key, lock_mode=LockMode.wait, xact=False):
  """Runs sql to obtain a pg advisory lock.

  :dax: a DataAccess instance
  :key: either a big int or a 2-tuple of integers
  :lock_mode: a member of the LockMode enum
  :xact: a boolean, if True the lock will be automatically released at the end
         of the transaction and cannot be manually released.
  """
  lock_fxn = _lock_fxn("lock", lock_mode, xact)
  return dax.get_scalar(
    dax.callproc(lock_fxn, key if isinstance(key, (list, tuple)) else [key])[0])


def release_lock(dax, key, lock_mode=LockMode.wait):
  """Manually release a pg advisory lock.

  :dax: a DataAccess instance
  :key: either a big int or a 2-tuple of integers
  :lock_mode: a member of the LockMode enum
  """
  lock_fxn = _lock_fxn("unlock", lock_mode, False)
  return dax.get_scalar(
    dax.callproc(lock_fxn, key if isinstance(key, (list, tuple)) else [key])[0])


@contextmanager
def advisory_lock(dax, key, lock_mode=LockMode.wait, xact=False):
  """A context manager for obtaining a lock, executing code, and then releasing
  the lock.

  A boolean value is passed to the block indicating whether or not the lock was
  obtained.

  :dax: a DataAccess instance
  :key: either a big int or a 2-tuple of integers
  :lock_mode: a member of the LockMode enum. Determines how this function
              operates:
                - wait: the wrapped code will not be executed until the lock
                        is obtained.
                - skip: an attempt will be made to get the lock, and if
                        unsuccessful, False is passed to the code block
                - error: an attempt will be made to get the lock, and if
                         unsuccessful, an exception will be raised.
  :xact: a boolean, if True, the lock will be obtained according to lock_mode,
         but will not be released after the code is executed, since it will be
         automatically released at the end of the transaction.
  """
  if lock_mode == LockMode.wait:
    obtain_lock(dax, key, lock_mode, xact)
  else:
    got_lock = obtain_lock(dax, key, lock_mode, xact)
    if not got_lock:
      if lock_mode == LockMode.error:
        raise Exception("Unable to obtain advisory lock {}".format(key))
      else:
        # lock_mode is skip
        yield False
        return

  # At this point we have the lock
  try:
    yield True
  finally:
    if not xact:
      release_lock(dax, key, lock_mode)


def _lock_fxn(direction, lock_mode, xact):
  """Builds a pg advisory lock function name based on various options.

  :direction: one of "lock" or "unlock"
  :lock_mode: a member of the LockMode enum
  :xact: a boolean, if True the lock will be automatically released at the end
         of the transaction and cannot be manually released.
  """
  if direction == "unlock" or lock_mode == LockMode.wait:
    try_mode = ""
  else:
    try_mode = "_try"

  if direction == "lock" and xact:
    xact_mode = "_xact"
  else:
    xact_mode = ""

  return "pg{}_advisory{}_{}".format(try_mode, xact_mode, direction)
