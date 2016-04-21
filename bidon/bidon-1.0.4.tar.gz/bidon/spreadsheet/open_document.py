"""The spreadsheet.open_document module contains the OpenDocument implementation for the
bidon.spreadsheet model. It requires the ezodf library.
"""
import re

import ezodf

from bidon.spreadsheet.base import CellMode, WorksheetBase, WorkbookBase


__all__ = ["OpenDocumentWorksheet", "OpenDocumentWorkbook"]


_DATE_REGEX = re.compile(r"^(\d{4})-(\d\d)-(\d\d)(?:T(\d\d):(\d\d):(\d\d)(?:\.\d+)?)?$")
_TIME_REGEX = re.compile(r"^PT(\d\d)H(\d\d)M(\d\d(?:\.\d+)?)S$")


class OpenDocumentWorksheet(WorksheetBase):
  """Specialization of WorksheetBase for working with OpenDocument Spreadsheet files."""
  def __init__(self, raw_sheet, ordinal):
    """Initialize the OpenDocumentWorksheet instance."""
    super().__init__(raw_sheet, ordinal)
    self.name = self.raw_sheet.name
    self.nrows = self.raw_sheet.nrows()
    self.ncols = self.raw_sheet.ncols()
    self._raw_rows = None

  def parse_cell(self, cell, coords, cell_mode=CellMode.cooked):
    """Parses a cell according to its cell.value_type."""
    # pylint: disable=too-many-return-statements
    if cell_mode == CellMode.cooked:
      if cell.covered or cell.value_type is None or cell.value is None:
        return None

      vtype = cell.value_type

      if vtype == 'string':
        return cell.value

      if vtype == 'float' or vtype == 'percentage' or vtype == 'currency':
        return cell.value

      if vtype == 'boolean':
        return cell.value

      if vtype == 'date':
        date_tuple = tuple([int(i) if i is not None else 0 \
                            for i in _DATE_REGEX.match(cell.value).groups()])
        return self.tuple_to_datetime(date_tuple)

      if vtype == 'time':
        hour, minute, second = _TIME_REGEX.match(cell.value).groups()
        # TODO: This kills off the microseconds
        date_tuple = (0, 0, 0, int(hour), int(minute), round(float(second)))
        return self.tuple_to_datetime(date_tuple)

      raise ValueError("Unhandled cell type: {0}".format(vtype))
    else:
      return cell

  def get_row(self, row_index):
    """Returns the row at row_index."""
    if self._raw_rows is None:
      self._raw_rows = list(self.raw_sheet.rows())
    return self._raw_rows[row_index]

  def merged_cell_ranges(self):
    """Generates the sequence of merged cell ranges in the format:

    ((col_low, row_low), (col_hi, row_hi))
    """
    for row_number, row in enumerate(self.raw_sheet.rows()):
      for col_number, cell in enumerate(row):
        rspan, cspan = cell.span
        if (rspan, cspan) != (1, 1):
          yield ((col_number, row_number), (col_number + cspan, row_number + rspan))


class OpenDocumentWorkbook(WorkbookBase):
  """Specialization of WorkbookBase for working with OpenDocument Spreadsheet files."""
  def __init__(self, filename):
    """Initializes the OpenDocumentWorkbook instance."""
    super().__init__(filename)
    self.workbook = ezodf.opendoc(self.filename)

  def iterate_sheets(self):
    """Generate the sequence of sheets in the workbook."""
    for sheet in self.workbook.sheets:
      yield sheet

  def get_worksheet(self, raw_sheet, index):
    """Creates an OpenDocumentWorkshet instance from the raw sheet."""
    return OpenDocumentWorksheet(raw_sheet, index)
