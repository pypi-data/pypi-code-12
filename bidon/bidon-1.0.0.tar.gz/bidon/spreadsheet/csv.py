"""The spreadsheet.csv module contains the CSV implementation for the bidon.spreadsheet model."""
import csv
import gzip

from bidon.spreadsheet.base import CellMode, WorksheetBase, WorkbookBase


__all__ = ["CSVWorksheet", "CSVWorkbook"]


class CSVWorksheet(WorksheetBase):
  """Specialization of WorksheetBase for working with CSV documents."""
  def __init__(self, raw_sheet, ordinal):
    """Initialize the CSVWorksheet instance."""
    super().__init__(raw_sheet, ordinal)
    self.name = "Sheet 1"
    self.nrows = len(self.raw_sheet)
    self.ncols = max([len(r) for r in self.raw_sheet])

  def parse_cell(self, cell, coords, cell_mode=CellMode.cooked):
    """Tries to convert the value first to an int, then a float and if neither is
    successful it returns the string value.
    """
    try:
      return int(cell)
    except ValueError:
      pass
    try:
      return float(cell)
    except ValueError:
      pass
    # TODO Check for dates?
    return cell

  def get_row(self, row_index):
    """Returns the row at row_index."""
    return self.raw_sheet[row_index]


class CSVWorkbook(WorkbookBase):
  """Implementation of WorkbookBase for working with CSV documents."""
  def __init__(self, filename, *, is_gzipped=False):
    """Initialize the CSVWorkbook instance."""
    super().__init__(filename)
    self.is_gzipped = is_gzipped

  def iterate_sheets(self, *args, **kwargs):
    """Opens self.filename and reads it with a csv reader.

    If self.filename ends with .gz, the file will be decompressed with gzip before being passed
    to csv.reader. If the filename is not a string, it is assumed to be a file-like object which
    will be passed directly to csv.reader.
    """
    if isinstance(self.filename, str):
      if self.filename.endswith(".gz") or self.is_gzipped:
        with gzip.open(self.filename, "rt") as rfile:
          reader = csv.reader(rfile, *args, **kwargs)
          yield list(reader)
      else:
        with open(self.filename, "r") as rfile:
          reader = csv.reader(rfile, *args, **kwargs)
          yield list(reader)
    else:
      reader = csv.reader(self.filename, *args, **kwargs)
      yield list(reader)

  def get_worksheet(self, raw_sheet, index):
    """Creates a CSVWorksheet instance from the raw sheet."""
    return CSVWorksheet(raw_sheet, index)
