"""The spreadsheet.base module contains the base classes used by the different spreadsheet
implementations.
"""
from datetime import date, time, datetime
from enum import Enum


__all__ = ["CellMode", "Cell", "WorksheetBase", "WorkbookBase"]


class CellMode(Enum):
  """Enum of cell modes."""
  raw = 0x01
  cooked = 0x02


class Cell(object):
  """Represents a cell in a spreadsheet."""
  def __init__(self, value=None, note=None):
    """Initialize the cell instance."""
    self.value = value
    self.note = note

  def copy(self):
    """Copy the cell object."""
    return Cell(self.value, self.note)

  def __str__(self):
    """Returns a string representation of a cell object."""
    return "Cell(value={0}, note={1})".format(self.value, self.note)


class WorksheetBase(object):
  """The base class for all worksheets. For each implemented spreadsheet type, it is necessary to
  write a subclass of this class that implements the necessary methods."""
  def __init__(self, raw_sheet, ordinal):
    """Initialize the WorksheetBase instance."""
    self.raw_sheet = raw_sheet
    self.ordinal = ordinal
    self.name = None
    self.nrows = -1
    self.ncols = -1

  def to_cell_table(self, merged=True):
    """Returns a list of lists of Cells with the cooked value and note for each cell."""
    new_rows = []
    for row_index, row in enumerate(self.rows(CellMode.cooked)):
      new_row = []
      for col_index, cell_value in enumerate(row):
        new_row.append(Cell(cell_value, self.get_note((col_index, row_index))))
      new_rows.append(new_row)
    if merged:
      for cell_low, cell_high in self.merged_cell_ranges():
        anchor_cell = new_rows[cell_low[1]][cell_low[0]]
        for row_index in range(cell_low[1], cell_high[1]):
          for col_index in range(cell_low[0], cell_high[0]):
            # NOTE: xlrd occassionally returns ranges that don't have cells.
            try:
              new_rows[row_index][col_index] = anchor_cell.copy()
            except IndexError:
              pass
    return new_rows

  def rows(self, cell_mode=CellMode.cooked):
    """Generates a sequence of parsed rows from the worksheet. The cells are parsed according to the
    cell_mode argument.
    """
    for row_index in range(self.nrows):
      yield self.parse_row(self.get_row(row_index), row_index, cell_mode)

  def parse_row(self, row, row_index, cell_mode=CellMode.cooked):
    """Parse a row according to the given cell_mode."""
    return [self.parse_cell(cell, (col_index, row_index), cell_mode) \
            for col_index, cell in enumerate(row)]

  def get_cell(self, coords, cell_mode=CellMode.cooked):
    """Get a cell from the worksheet according to the given coords and parse it according to the
    given cell_mode. Coords is a tuple of (col, row).
    """
    return self.parse_cell(self.get_row(coords[1])[coords[0]], coords, cell_mode)

  def tuple_to_datetime(self, date_tuple):
    """Converts a tuple to a either a date, time or datetime object.

    If the Y, M and D parts of the tuple are all 0, then a time object is returned.
    If the h, m and s aprts of the tuple are all 0, then a date object is returned.
    Otherwise a datetime object is returned.
    """
    year, month, day, hour, minute, second = date_tuple
    if year == month == day == 0:
      return time(hour, minute, second)
    elif hour == minute == second == 0:
      return date(year, month, day)
    else:
      return datetime(year, month, day, hour, minute, second)

  def parse_cell(self, cell, coords, mode=CellMode.cooked):
    """Virtual method for parsing a cell. Must be overridden by subclasses."""
    raise NotImplementedError()

  def get_row(self, row_index):
    """Virtual method for getting a row, by index, from a worksheet. Must be overridden by
    subclasses.
    """
    raise NotImplementedError()

  def merged_cell_ranges(self):
    """Enumerates cell ranges as ((cell_low, row_low), (cell_high, row_high)). Can be overridden by
    subclasses."""
    return []

  def get_note(self, coords):
    """Coords are (col, row). Can be overridden by subclasses."""
    return None


class WorkbookBase(object):
  """The base class for all workbooks. For each implemented spreadsheet type, it is necessary to
  write a subclass of this class that implements the necessary methods."""
  def __init__(self, filename):
    """Initialize the WorkbookBase instance."""
    self.filename = filename
    self._sheets = None

  def sheets(self, index=None):
    """Return either a list of all sheets if index is None, or the sheet at the given index."""
    if self._sheets is None:
      self._sheets = [self.get_worksheet(s, i) for i, s in enumerate(self.iterate_sheets())]
    if index is None:
      return self._sheets
    else:
      return self._sheets[index]

  def iterate_sheets(self):
    """Virtual method to iterate through sheets. Must be overridden by child classes."""
    raise NotImplementedError()

  def get_worksheet(self, raw_sheet, index):
    """Virtual method to get a WorksheetBase class from a raw sheet. Must be overridden by child
    classes."""
    return WorksheetBase(raw_sheet, index)
