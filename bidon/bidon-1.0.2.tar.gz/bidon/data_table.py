"""The data_table module contains the DataTable class and supporting functions."""
import re
from decimal import Decimal
from numbers import Number

from bidon.util.convert import to_compressed_string


_REPEATING_NUMBER_TRIM_RE = re.compile(r"((\d+?)\2{2,})")


def reduce_number(num):
  """Reduces the string representation of a number.

  If the number is of the format n.00..., returns n.
  If the decimal portion of the number has a repeating decimal, followed by up to two trailing
  numbers, such as:

  0.3333333

  or

  0.343434346

  It will return just one instance of the repeating decimals:

  0.3

  or

  0.34
  """
  parts = str(num).split(".")
  if len(parts) == 1 or parts[1] == "0":
    return int(parts[0])
  else:
    match = _REPEATING_NUMBER_TRIM_RE.search(parts[1])
    if match:
      from_index, _ = match.span()
      if from_index == 0 and match.group(2) == "0":
        return int(parts[0])
      else:
        return Decimal(parts[0] + "." + parts[1][:from_index] + match.group(2))
    else:
      return num


class DataTable(object):
  """This class contains methods for working with a table a cells. A cell is any object that holds
  values.

  Methods for interacting with the cells are passed in on the constructor."""
  def __init__(self, rows, get_cell_value=None, set_cell_value=None, is_cell_empty=None,
               clean_value=None):
    """Initializes a DataTable instance."""
    self.rows = rows
    self.nrows = len(rows)
    self.ncols = max([len(row) for row in rows]) if self.nrows != 0 else 0
    self._get_cell_value = get_cell_value
    self._set_cell_value = set_cell_value
    self._is_cell_empty = is_cell_empty
    self._clean_value = clean_value

  # TODO: coords is (col, row) in spreadsheet but (row, col) here. That should be changed...?"""
  def __getitem__(self, index):
    """Get the item at the given index.

    Index is a tuple of (row, col)
    """
    row, col = index
    return self.rows[row][col]

  def get_cell_value(self, cell):
    """Gets the value from the given cell."""
    if self._get_cell_value:
      return self._get_cell_value(cell)
    else:
      return cell

  def set_cell_value(self, row, index, value):
    """Sets the value for the cell at row[index]."""
    if self._set_cell_value:
      self._set_cell_value(row, index, value)
    else:
      row[index] = value

  def is_cell_empty(self, cell):
    """Checks if the cell is empty."""
    if cell is None:
      return True
    elif self._is_cell_empty:
      return self._is_cell_empty(cell)
    else:
      return cell is None

  def is_row_empty(self, row):
    """Returns True if every cell in the row is empty."""
    for cell in row:
      if not self.is_cell_empty(cell):
        return False
    return True

  def serialize(self, serialize_cell=None):
    """Returns a list of all rows, with serialize_cell or self.get_cell_value called on the cells of
    each.
    """
    if serialize_cell is None:
      serialize_cell = self.get_cell_value
    return [[serialize_cell(cell) for cell in row] for row in self.rows]

  def headers(self, serialize_cell=None):
    """Gets the first row of the data table, with serialize_cell or self.get_cell_value is called on
    each cell."""
    if serialize_cell is None:
      serialize_cell = self.get_cell_value
    return [serialize_cell(cell) for cell in self.rows[0]]

  def rows_to_dicts(self, serialize_cell=None):
    """Generates a sequence of dictionaries of {header[i] => row[i]} for each row."""
    if serialize_cell is None:
      serialize_cell = self.get_cell_value
    # keys = [serialize_cell(cell) for cell in self.rows[0]]
    keys = self.headers(serialize_cell)
    for row in self.rows[1:]:
      yield dict(zip(keys, [serialize_cell(cell) for cell in row]))

  def cleanup(self):
    """Cleans up the data table:

    It first calls clean_value passed to the constructor on each cell. Then it trims out empty
    rows and columns.
    """
    self.clean_values()
    self.trim_empty_rows()
    self.trim_empty_columns()
    return self

  def trim_empty_rows(self):
    """Remove all trailing empty rows."""
    if self.nrows != 0:
      row_index = 0
      for row_index, row in enumerate(reversed(self.rows)):
        if not self.is_row_empty(row):
          break
      self.nrows = len(self.rows) - row_index
      self.rows = self.rows[:self.nrows]
    return self

  def trim_empty_columns(self):
    """Removes all trailing empty columns."""
    if self.nrows != 0 and self.ncols != 0:
      last_col = -1
      for row in self.rows:
        for i in range(last_col + 1, len(row)):
          if not self.is_cell_empty(row[i]):
            last_col = i
      ncols = last_col + 1
      self.rows = [row[:ncols] for row in self.rows]
      self.ncols = ncols
    return self

  def clean_values(self):
    """Cleans the values in each cell. Calls either the user provided clean_value, or the
    class defined clean value.
    """
    for row in self.rows:
      for index, cell in enumerate(row):
        self.set_cell_value(row, index, self.clean_value(self.get_cell_value(cell)))
    return self

  def clean_value(self, value):
    """Cleans a value, using either the user provided clean_value, or cls.reduce_value."""
    if self._clean_value:
      return self._clean_value(value)
    else:
      return self.reduce_value(value)

  @classmethod
  def reduce_value(cls, value):
    """Cleans the value by either compressing it if it is a string, or reducing it if it is a
    number.
    """
    if isinstance(value, str):
      return to_compressed_string(value)
    elif isinstance(value, bool):
      return value
    elif isinstance(value, Number):
      return reduce_number(value)
    else:
      return value
