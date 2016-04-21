"""Contains the StreamWriter class."""
from collections import OrderedDict
from contextlib import contextmanager
from xml.sax.saxutils import XMLGenerator


def _normalize_name(name):
  """Returns a normalized element tag or attribute name. A tag name or attribute name can be given
  either as a string, or as a 2-tuple. If a 2-tuple, it is interpreted as (namespace, name) and is
  returned joined by a colon ":"

  :name: a string or a 2-tuple of strings
  """
  if isinstance(name, tuple):
    ns, nm = name
    return "{}:{}".format(ns, nm)
  else:
    return name


def _normalize_value(val, null):
  """Returns a normalized attribute value. A value can be either a string, or None. If None, the
  value of :null: will be returned instead.

  :val: a string or None
  :null: a string to be returned when :val: is None
  """
  if val is None:
    return null
  else:
    return str(val)


def _normalize_attrs(attrs, null=None):
  """Returns an OrderedDict of attirbutes with the keys normalized by _normalize_name and the values
  normalized by _normalize_value. The value of :null: is passed to _normalize_value. However, if
  :null: is None, any values that are None are left out of the returned dict.

  An OrderedDict is returned so that the attributes are always printed in the same order for similar
  objects.

  :attrs: a dict whose keys can be passed to _normalize_name and whose values can be passed to
          _normalize_value
  :null: either a string to be put in place of values that are None, or None, which will cause
         values that are None to be left out of the returned dict
  """
  if attrs:
    items = sorted((_normalize_name(k), _normalize_value(v, null)) for (k, v) in attrs.items())

    if null is None:
      return OrderedDict((k, v) for (k, v) in items if v is not None)
    else:
      return OrderedDict(items)
  else:
    return {}


class StreamWriter(object):
  """This class provides methods for writing out an XML tree in a stream, rather than building it
  up in memory and then dumping it. The API is low-level, but it allows for very low memory usage,
  which is necessary when generating large files.

  This is implemented as a thin wrapper around xml.sax.saxutils.XMLGenerator.
  """
  def __init__(self, out, encoding="UTF-8", indent=None):
    """Initializes the StreamWriter instance.

    :out: a file-like object that will be written to
    :encodig: the encoding for output. Defaults to UTF-8
    :indent: a whitespace string used for indenting new lines. If None (the default) then no
             extra whitespace will be added to the document.
    """
    self._writer = XMLGenerator(out, encoding)
    self._indent = indent
    self._open_elements = []

  def __enter__(self):
    """Entry point for use as a context manager."""
    self.start()
    return self

  def __exit__(self, ex_type, ex_val, ex_tb):
    """Exit point for use as a context manager."""
    if ex_type is None:
      self.end()

  def start(self):
    """Calls startDocument on the underlying XMLGenerator."""
    self._writer.startDocument()

  def end(self):
    """Closes any remaining open elements and calls endDocument on the underlying XMLGenerator."""
    while self._open_elements:
      self.close()

    self._writer.endDocument()

  def open(self, name, attrs=None, *, close=False):
    """Writes an opening element.

    :name: the name of the element
    :attrs: a dict of attributes
    :close: if True, close will be called immediately after writing the element
    """
    self._pad()
    self._writer.startElement(_normalize_name(name), _normalize_attrs(attrs))
    self._newline()
    self._open_elements.append(name)

    if close:
      self.close()

  def close(self, name=None):
    """Closes the most recently opened element.

    :name: if given, this value must match the name given for the most recently opened element. This
           is primarily here for providing quick error checking for applications
    """
    tag = self._open_elements.pop()
    if name is not None and name != tag:
      raise Exception("Tag closing mismatch")
    self._pad()
    self._writer.endElement(_normalize_name(tag))
    self._newline()

  def characters(self, characters):
    """Writes content for a tag.

    :characters: the characters to write
    """
    self._pad()
    self._writer.characters(str(characters))
    self._newline()

  def whitespace(self, whitespace):
    """Writes ignorable whitespace.

    :whitespace: the whitespace to write
    """
    self._writer.ignorableWhitespace(whitespace)

  @contextmanager
  def element(self, name, attrs=None):
    """This method is a context manager for writing and closing an element."""
    self.open(name, attrs)
    yield
    self.close()

  @contextmanager
  def no_inner_space(self, *, outer=True):
    """Default spacing for all things written is ignored in this context.

    :outer: boolean, if True the typical padding and newline are added before the first and after
            the last things written
    """
    if outer:
      self._pad()

    indent_was = self._indent
    self._indent = None

    try:
      yield
    finally:
      self._indent = indent_was

    if outer:
      self._newline()

  def content(self, name, attrs=None, characters=None):
    """Writes an element, some content for the element, and then closes the element, all without
    indentation.

    :name: the name of the element
    :attrs: a dict of attributes
    :characters: the characters to write
    """
    with self.no_inner_space(outer=True):
      with self.element(name, attrs):
        if characters:
          self.characters(characters)

  def _pad(self):
    """Pads the output with an amount of indentation appropriate for the number of open element.

    This method does nothing if the indent value passed to the constructor is falsy.
    """
    if self._indent:
      self.whitespace(self._indent * len(self._open_elements))

  def _newline(self):
    """Writes a newline to output.

    This method does nothing if the indent value passed to the constructor is falsy.
    """
    if self._indent:
      self.whitespace("\n")
