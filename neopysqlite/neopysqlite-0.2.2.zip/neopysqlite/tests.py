from neopysqlite import Pysqlite
import unittest
import os.path

# TODO: Pass database filename and tables names via argparse to run tests against a specific database

# set the DB as global to avoid initialising it each time
db = Pysqlite(database_name='test db', database_file='test.db')
test_rows = [
    ('', None),
    ('apple', 'juice'),
    ('lemon', 'lime')
]


class TestDBAccessible(unittest.TestCase):
    def test_db_exists(self):
        self.assertTrue(os.path.isfile('test.db'), msg='Database file does not exist')

    def test_db_accessible(self):
        self.assertTrue(os.access('test.db', os.R_OK), msg='Database file could not be accessed')


class TestDBNotEmpty(unittest.TestCase):
    def test_db_table_exists(self):
        # db = Pysqlite(database_name='test db', database_file='test.db')
        global db
        data = db.get_all_rows('sqlite_sequence')
        table_names = [field[0] for field in data]
        self.assertTrue('table_one' in table_names, msg='Table table_one does not exist')

    def test_db_not_empty(self):
        # db = Pysqlite(database_name='test db', database_file='test.db')
        global db
        data = db.get_all_rows('table_one')
        self.assertGreater(len(data), 0, msg='Test table_one is empty')


class TestDBTables(unittest.TestCase):
    def test_tables_exist(self):
        global db
        test_table_names = ['table_one', 'sqlite_sequence']
        table_names = db.get_table_names()
        self.assertEqual(table_names, test_table_names, msg='Tables returned: {} not as expected: {}'.format(
            table_names, test_table_names))

    """
    def test_contents_count(self):
        # db = Pysqlite(database_name='test db', database_file='test.db')
        global db
        data = db.get_db_data('table_one')
        self.assertEqual(len(data), 4, msg='Test contents not as expected')
    """


class TestDBInsertContents(unittest.TestCase):
    def test_insert_correct_row(self):
        global db
        db.insert_row(table='table_one', row_string='(NULL, ?, ?)', row_data=('lemon', 'lime'))
        data = db.get_all_rows('table_one')
        self.assertTrue(data[-1][1] == 'lemon', msg='Retrieved field 1 does not match given field 1')
        self.assertTrue(data[-1][2] == 'lime', msg='Retrieved field 2 does not match given field 2')


class TestDBDeleteContents(unittest.TestCase):
    def test_delete_inserted_row(self):
        global db
        # insert some test data
        db.insert_rows(table='table_one', row_string='(NULL, ?, ?)', row_data_list=test_rows)
        # delete just the first inserted row
        db.delete_rows(table='table_one', delete_string='something_not_null = ?', delete_value=('lemon',))
        data = db.get_all_rows(table='table_one')
        self.assertFalse(data[-1][1] == 'lemon', msg='Field not deleted properly')

    def test_delete_all(self):
        global db
        db.delete_all_rows(table='table_one')
        data = db.get_all_rows('table_one')
        self.assertEqual(data, [])


if __name__ == '__main__':
    unittest.main()
