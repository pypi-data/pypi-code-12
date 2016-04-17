"""The spreadsheet.excel module contains the Excel implementation for the bidon.spreadsheet model
for working with .xls and .xlsx documents. It requires the xlrd library.
"""
import xlrd

from bidon.spreadsheet.base import CellMode, WorksheetBase, WorkbookBase


__all__ = ["ExcelWorksheet", "ExcelWorkbook"]


class ExcelWorksheet(WorksheetBase):
  """Specialization of WorksheetBase for working with excel documents."""
  def __init__(self, raw_sheet, ordinal, handle_ambiguous_date):
    """Initialize the ExcelWorksheet instance."""
    super().__init__(raw_sheet, ordinal)
    self.name = self.raw_sheet.name
    self.nrows = self.raw_sheet.nrows
    self.ncols = self.raw_sheet.ncols
    self.handle_ambiguous_date = handle_ambiguous_date

  def parse_cell(self, cell, coords, cell_mode=CellMode.cooked):
    """Parses a cell according to the cell.ctype."""
    # pylint: disable=too-many-return-statements
    if cell_mode == CellMode.cooked:
      if cell.ctype == xlrd.XL_CELL_BLANK:
        return None

      if cell.ctype == xlrd.XL_CELL_BOOLEAN:
        return cell.value

      if cell.ctype == xlrd.XL_CELL_DATE:
        if self.handle_ambiguous_date:
          try:
            return self._parse_date(cell.value)
          except xlrd.xldate.XLDateAmbiguous:
            return self.handle_ambiguous_date(cell.value)
        else:
          return self._parse_date(cell.value)

      if cell.ctype == xlrd.XL_CELL_EMPTY:
        return None

      if cell.ctype == xlrd.XL_CELL_ERROR:
        return cell.value

      if cell.ctype == xlrd.XL_CELL_NUMBER:
        return cell.value

      if cell.ctype == xlrd.XL_CELL_TEXT:
        return cell.value

      raise ValueError("Unhandled cell type {0}".format(cell.ctype))
    else:
      return cell

  def get_row(self, row_index):
    """Returns the row at row_index."""
    return self.raw_sheet.row(row_index)

  def merged_cell_ranges(self):
    """Generates the sequence of merged cell ranges in the format:

    ((col_low, row_low), (col_hi, row_hi))
    """
    for rlo, rhi, clo, chi in self.raw_sheet.merged_cells:
      yield ((clo, rlo), (chi, rhi))

  def get_note(self, coords):
    """Get the note for the cell at the given coordinates.

    coords is a tuple of (col, row)
    """
    col, row = coords
    note = self.raw_sheet.cell_note_map.get((row, col))
    return note.text if note else None

  def _parse_date(self, cell_value):
    """Attempts to parse a cell_value as a date."""
    date_tuple = xlrd.xldate_as_tuple(cell_value, self.raw_sheet.book.datemode)
    return self.tuple_to_datetime(date_tuple)


class ExcelWorkbook(WorkbookBase):
  """Specialization of WorkbookBase for working with Excel workbooks."""
  def __init__(self, filename, formatting_info=False, handle_ambiguous_date=None):
    """Initialize the ExcelWorkbook instance."""
    super().__init__(filename)
    self.workbook = xlrd.open_workbook(self.filename, formatting_info=formatting_info)
    self.handle_ambiguous_date = handle_ambiguous_date

  def iterate_sheets(self):
    """Generates the sequence of sheets in the workbook."""
    for sheet in self.workbook.sheets():
      yield sheet

  def get_worksheet(self, raw_sheet, index):
    """Creates an ExcelWorksheet instance from a raw sheet."""
    return ExcelWorksheet(raw_sheet, index, self.handle_ambiguous_date)
