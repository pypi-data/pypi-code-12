import sqlite3, unittest
from .helpers import get_sql_results, dict_factory
from ..src import get_base_model
from ..test import db_path

conn = None
Artist = None

def setup_module(module):
    global conn
    print ("") # this is to get a newline after the dots
    print ("getting connection")
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory

def teardown_module(module):
    print ("closing connection")
    conn.close()

def test_db_setup():
    cur = conn.cursor()
    cur.execute("select * from Artist")
    results = cur.fetchall()
    cur.close()
    assert(len(results)==275)

class TestSelectAll(unittest.TestCase):
    def setUp(self):
        global Artist
        # BaseModel.connection = conn
        BaseModel = get_base_model(conn)
        class Dummy(BaseModel):
            table_name = "Artist"
            pk = "ArtistId"
        Artist = Dummy

    def test_artists(self):
        self.assertEqual(len(Artist.all()), 275)
