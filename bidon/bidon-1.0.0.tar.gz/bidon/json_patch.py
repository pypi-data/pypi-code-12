"""Apply patches to a parsed json document.

Add { op: "add", path: "/a/b/c", value: v }
  Add value v to /a/b at index c. If /a/b is a list, c must be an integer, and
  v will be inserted at c. To append a value to list, use a trailing / in the
  path.

Remove { op: "remove", path: "/a/b/c" }
  Remove the key c from dictionary /a/b, or the item at index c from list /a/b.

Replace { op: "replace", path: "/a/b/c", value: v, src: k }
  Replace the item at c on /a/b with v. If check is specified, the patch will
  fail if the existing value at c is not k.

Merge { op: "merge", path: "/a/b/c", value: { k0: v0, k1: v1, ..., kn: vn } }
  This will create or replace all k0 - kn on c. It can be used to group
  multiple adds and replaces, or can act as an upsert.

Copy { op: "copy", path: "/b/c/d", src: "/a/b/c" }
  Copy the value at /a/b/c to d on /b/c.

Move { op: "move", path: "/b/c/d", src: "/a/b/c" }
  Equivalent to a copy from 'src' to 'path' followed by a remove at 'path'.

Test { op: "test", path: "/a/b/c" [, value: v] }
  Test that the index c on /a/b is specified. If value is given, check
  additionally that the value at c on /a/b equals v

Set Remove { op: "setremove", path: "/a/b", value: v }
  Remove v from the list at /a/b, if v is in /a/b.

Set Add { op: "setadd", path: "/a/b", value: v }
  Add v to the list at /a/b if it doesn't already exist in the list.

All paths must conform to RFC 6901.

Inspiration from http://jsonpatch.com with additional features to handle
certain types of concurrent editing.
"""
from collections import namedtuple

from bidon.util import try_parse_int


_NO_VAL = object()
_PATH_SEP = "/"
Patch = namedtuple("Patch", ["op", "path", "value", "src"])
Patch.__new__.__defaults__ = (_NO_VAL, _NO_VAL)


class JSONPathError(Exception):
  """Instances of this Error are thrown when json_patch cannot understand a path in a given context.
  """
  pass


class JSONPatchError(Exception):
  """Instances of this Error are thrown when json_patch is unable to perform a requested action."""
  pass


def add(parent, idx, value):
  """Add a value to a dict."""
  if isinstance(parent, dict):
    if idx in parent:
      raise JSONPatchError("Item already exists")
    parent[idx] = value
  elif isinstance(parent, list):
    if idx == "" or idx == "~":
      parent.append(value)
    else:
      parent.insert(int(idx), value)
  else:
    raise JSONPathError("Invalid path for operation")


def remove(parent, idx):
  """Remove a value from a dict."""
  if isinstance(parent, dict):
    del parent[idx]
  elif isinstance(parent, list):
    del parent[int(idx)]
  else:
    raise JSONPathError("Invalid path for operation")


def replace(parent, idx, value, check_value=_NO_VAL):
  """Replace a value in a dict."""
  if isinstance(parent, dict):
    if idx not in parent:
      raise JSONPatchError("Item does not exist")
  elif isinstance(parent, list):
    idx = int(idx)
    if idx < 0 or idx >= len(parent):
      raise JSONPatchError("List index out of range")
  if check_value is not _NO_VAL:
    if parent[idx] != check_value:
      raise JSONPatchError("Check value did not pass")
  parent[idx] = value


def merge(parent, idx, value):
  """Merge a value."""
  target = get_child(parent, idx)
  for key, val in value.items():
    target[key] = val


def copy(src_parent, src_idx, dest_parent, dest_idx):
  """Copy an item."""
  if isinstance(dest_parent, list):
    dest_idx = int(dest_idx)
  dest_parent[dest_idx] = get_child(src_parent, src_idx)


def move(src_parent, src_idx, dest_parent, dest_idx):
  """Move an item."""
  copy(src_parent, src_idx, dest_parent, dest_idx)
  remove(src_parent, src_idx)


def test(parent, idx, value=_NO_VAL):
  """Check to see if an item exists."""
  try:
    val = get_child(parent, idx)
  except Exception:
    return False

  if value is _NO_VAL:
    return True
  return val == value


def set_remove(parent, idx, value):
  """Remove an item from a list."""
  lst = get_child(parent, idx)
  if value in lst:
    lst.remove(value)


def set_add(parent, idx, value):
  """Add an item to a list if it doesn't exist."""
  lst = get_child(parent, idx)
  if value not in lst:
    lst.append(value)


def get_children(parent, idx):
  """Gets the child at parent[idx], or all the children if idx == "*"."""
  if isinstance(parent, dict):
    if idx in parent:
      yield parent[idx]
    else:
      raise JSONPathError("Invalid path at {0}".format(idx))

  elif isinstance(parent, list):
    if idx == "*":
      yield from parent
    else:
      is_int, i = try_parse_int(idx)

      if is_int and i >= 0 and i < len(parent):
        yield parent[i]
      else:
        raise JSONPathError("Invalid list index: {0}".format(i))

  else:
    raise JSONPathError("Type {0} does not have children".format(type(parent).__name__))


def get_child(parent, idx):
  """Get the first child according to idx."""
  return next(get_children(parent, idx))


def parse_path(path):
  """Parse a rfc 6901 path."""
  if not path:
    raise ValueError("Invalid path")

  if isinstance(path, str):
    if path == "/":
      raise ValueError("Invalid path")
    if path[0] != "/":
      raise ValueError("Invalid path")
    return path.split(_PATH_SEP)[1:]
  elif isinstance(path, (tuple, list)):
    return path
  else:
    raise ValueError("A path must be a string, tuple or list")


def resolve_path(root, path):
  """Resolve a rfc 6901 path, returning the parent and the last path part."""
  path = parse_path(path)

  parent = root

  for part in path[:-1]:
    parent = get_child(parent, rfc_6901_replace(part))

  return (parent, rfc_6901_replace(path[-1]))


def find(root, path):
  """Get the (first) child at path from root."""
  return get_child(*resolve_path(root, path))


def find_all(root, path):
  """Get all children that satisfy the path."""
  path = parse_path(path)

  if len(path) == 1:
    yield from get_children(root, path[0])
  else:
    for child in get_children(root, path[0]):
      yield from find_all(child, path[1:])


def rfc_6901_replace(path):
  """Implements rfc 6901 escape code replacement."""
  return path.replace("~1", "/").replace("~0", "~")


def apply_patch(document, patch):
  """Apply a Patch object to a document."""
  # pylint: disable=too-many-return-statements
  op = patch.op
  parent, idx = resolve_path(document, patch.path)
  if op == "add":
    return add(parent, idx, patch.value)
  elif op == "remove":
    return remove(parent, idx)
  elif op == "replace":
    return replace(parent, idx, patch.value, patch.src)
  elif op == "merge":
    return merge(parent, idx, patch.value)
  elif op == "copy":
    sparent, sidx = resolve_path(document, patch.src)
    return copy(sparent, sidx, parent, idx)
  elif op == "move":
    sparent, sidx = resolve_path(document, patch.src)
    return move(sparent, sidx, parent, idx)
  elif op == "test":
    return test(parent, idx, patch.value)
  elif op == "setremove":
    return set_remove(parent, idx, patch.value)
  elif op == "setadd":
    return set_add(parent, idx, patch.value)
  else:
    raise JSONPatchError("Invalid operator")


def apply_patches(document, patches):
  """Serially apply all patches to a document."""
  for i, patch in enumerate(patches):
    try:
      result = apply_patch(document, patch)
      if patch.op == "test" and result is False:
        raise JSONPatchError("Test patch {0} failed. Cancelling entire set.".format(i + 1))
    except Exception as ex:
      raise JSONPatchError("An error occurred with patch {0}: {1}".format(i + 1, ex)) from ex
