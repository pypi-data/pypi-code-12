import unittest
from datetime import date, time, datetime
from numbers import Number

from bidon.spreadsheet import Cell


class SpreadsheetTestCase(unittest.TestCase):
  def check_workbook(self, wb_class, open_args, ncols, nrows, date_type, time_type, datetime_type, has_merges, has_notes):
    wb = wb_class(*open_args)
    self.assertEqual(1, len(wb.sheets()))
    sh = wb.sheets(0)
    self.assertEqual(ncols, sh.ncols)
    self.assertEqual(nrows, sh.nrows)
    self.assertEqual(sh.get_cell((0, 0)), "Name")
    self.assertIsInstance(sh.get_cell((1, 1)), date_type)
    self.assertIsInstance(sh.get_cell((2, 1)), time_type)
    self.assertIsInstance(sh.get_cell((3, 1)), Number)
    self.assertIsInstance(sh.get_cell((4, 1)), datetime_type)
    if has_merges:
      merged_ranges = list(sh.merged_cell_ranges())
      self.assertEqual(3, len(merged_ranges))
      self.assertTrue(((0, 2), (2, 3)) in merged_ranges)
      self.assertTrue(((2, 2), (3, 4)) in merged_ranges)
      self.assertTrue(((3, 2), (5, 4)) in merged_ranges)
    if has_notes:
      self.assertIsNone(sh.get_note((0, 0)))
      self.assertIsNotNone(sh.get_note((0, 3)))
    return wb

  def test_xlsx(self):
    from bidon.spreadsheet.excel import ExcelWorkbook as WB
    wb = self.check_workbook(WB, ["tests/fixtures/test.xlsx", False], 5, 4, date, time, datetime, True, True)
    ct = wb.sheets(0).to_cell_table()
    self.assertEqual(4, len(ct))
    self.assertEqual(5, len(ct[0]))
    self.assertIsInstance(ct[0][0], Cell)
    self.assertEqual(ct[0][0].value, "Name")
    self.assertEqual(ct[3][0].note.strip(), "A comment my friends")

  def test_xls(self):
    from bidon.spreadsheet.excel import ExcelWorkbook as WB
    self.check_workbook(WB, ["tests/fixtures/test.xls", True], 5, 4, date, time, datetime, True, True)

  def test_ods(self):
    from bidon.spreadsheet.open_document import OpenDocumentWorkbook as WB
    self.check_workbook(WB, ["tests/fixtures/test.ods"], 6, 6, date, time, datetime, True, False)

  def test_csv(self):
    from bidon.spreadsheet.csv import CSVWorkbook as WB
    self.check_workbook(WB, ["tests/fixtures/test.csv"], 5, 4, str, str, str, False, False)

    import gzip
    with gzip.open("tests/fixtures/test.csv.gz", "rt") as rf:
      self.check_workbook(WB, [rf], 5, 4, str, str, str, False, False)

    self.check_workbook(WB, ["tests/fixtures/test.csv.gz"], 5, 4, str, str, str, False, False)
