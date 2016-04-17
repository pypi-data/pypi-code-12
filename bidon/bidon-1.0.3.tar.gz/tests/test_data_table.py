import unittest
from datetime import date, time, datetime
from decimal import Decimal

from bidon.spreadsheet import Cell
from bidon.spreadsheet.csv import CSVWorkbook
from bidon.data_table import DataTable


def get_cell_value(cell):
    return cell.value


def set_cell_value(row, index, value):
    row[index].value = value


def is_cell_empty(cell):
    return cell.value is None


class DataTableTestCase(unittest.TestCase):
  def get_data(self):
    return CSVWorkbook("tests/fixtures/data-table.csv").sheets(0).to_cell_table()

  def get_data_table(self, data=None):
    return DataTable(data or self.get_data(), get_cell_value, set_cell_value, is_cell_empty)

  def test_index(self):
    data_table = self.get_data_table()
    self.assertEqual(data_table[(1, 0)].value, "Saturday Kids 5")

  def test_initialize(self):
    data_table = self.get_data_table()
    self.assertEqual(11, len(data_table.rows))
    self.assertEqual(11, data_table.nrows)
    self.assertEqual(4, data_table.ncols)

  def test_serialize(self):
    data_table = self.get_data_table()
    data = data_table.serialize(lambda c: c.value)
    self.assertEqual(data[0][0], "Name")
    self.assertEqual(data[1][1], "2014-09-20")

  def test_rows_to_dicts(self):
    data_table = self.get_data_table()
    dicts = list(data_table.rows_to_dicts(lambda c: c.value))
    self.assertEqual(dicts[0], dict(Name="Saturday Kids 5", Date="2014-09-20", Time="5:00 PM", Attendance=55))

  def test_trim_empty_rows(self):
    data = self.get_data()
    data.append([Cell() for i in data[0]])
    data_table = self.get_data_table(data)
    self.assertEqual(12, data_table.nrows)
    data_table.trim_empty_rows()
    self.assertEqual(11, data_table.nrows)
    self.assertEqual(11, len(data_table.rows))
    data.insert(0, [Cell() for i in data[0]])
    data.insert(5, [Cell() for i in data[0]])
    data_table = self.get_data_table(data)
    self.assertEqual(14, data_table.nrows)
    data_table.trim_empty_rows()
    self.assertEqual(13, data_table.nrows)
    self.assertEqual(13, len(data_table.rows))

  def test_trim_empty_columns(self):
    data = self.get_data()
    for row in data:
      row.extend([Cell(), Cell()])
      row.insert(0, Cell())
      row.insert(2, Cell())
    data_table = self.get_data_table(data)
    self.assertEqual(8, data_table.ncols)
    data_table.trim_empty_columns()
    self.assertEqual(6, data_table.ncols)
    self.assertEqual(6, len(data_table.rows[0]))

  def test_clean_values(self):
    data = [[" a  b  ", 3.898989, None], [None, None, None]]
    data_table = DataTable(data)
    data_table.clean_values()
    self.assertEqual(data_table.rows[0][0], "a b")
    self.assertEqual(data_table.rows[0][1], Decimal("3.89"))
    data_table.trim_empty_rows()
    data_table.trim_empty_columns()
    self.assertEqual(data_table.serialize(), [["a b", Decimal("3.89")]])
    data_table = DataTable(data)
    data_table.cleanup()
    self.assertEqual(data_table.serialize(), [["a b", Decimal("3.89")]])

  def test_empty_table(self):
    data = []
    data_table = DataTable(data)
    self.assertEqual(data_table.nrows, 0)
    self.assertEqual(data_table.ncols, 0)
    data_table.cleanup()
    data_table.serialize()
