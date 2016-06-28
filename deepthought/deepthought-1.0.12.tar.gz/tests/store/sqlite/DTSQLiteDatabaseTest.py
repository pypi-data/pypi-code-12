import unittest
import tempfile
import os.path
from deepthought.store.sqlite.DTSQLiteDatabase import DTSQLiteDatabase

class DTSQLiteDatabaseTest(unittest.TestCase):
    db = None

    def setUp(self):
        self.db = DTSQLiteDatabase.init("CREATE TABLE test ( id int ); INSERT INTO test VALUES (1); INSERT INTO test VALUES (2);")

    def testDisconnect(self):
        unconnected_db = DTSQLiteDatabase()
        try:
            unconnected_db.disconnect()
            self.assertTrue(False,"Expected an exception for an unconnected store.")
        except:
            self.assertTrue(True)
        self.db.disconnect()
        try:
            self.db.query("SELECT * FROM test")
            self.assertTrue(False,"Expected to fail out on select.")
        except:
            self.assertTrue(True)

    def testConnect(self):
        path = os.path.abspath(os.path.dirname(__file__))+"/test.sqlite"
        if os.path.exists(path):
            os.unlink(path)
        dsn = "file:///"+path
        db = DTSQLiteDatabase(dsn)
        db.query("CREATE TABLE test ( id int ); INSERT INTO test VALUES (1); INSERT INTO test VALUES (2);")
        self.assertEquals(2,len(db.select("SELECT * FROM test")))
        os.unlink(path)

    def testQueryAndSelect(self):
        db = DTSQLiteDatabase.init()
        db.query("CREATE TABLE test ( id int ); INSERT INTO test VALUES (1); INSERT INTO test VALUES (44);")
        rows = db.select("SELECT * FROM test")
        self.assertEquals(2,len(rows))
        self.assertEquals(1,rows[0]["id"])
        self.assertEquals(44,rows[1]["id"])

    def testClean(self):
        val = "this unit's clean"
        self.assertEquals("this unit''s clean",self.db.clean(val))

    def testInsertAndLastID(self):
        db = DTSQLiteDatabase.init()
        self.assertEquals(0,db.lastInsertID())
        _id = self.db.insert("INSERT INTO test VALUES (3)")
        self.assertEquals(3,_id)
        self.assertEquals(_id,self.db.lastInsertID())

    def testPlaceholder(self):
        params = []
        self.assertEquals(":1",self.db.placeholder(params,"firstval"))
        self.assertEquals(":2",self.db.placeholder(params,"secondval"))
        self.assertEquals(2,len(params))

    def testPrepareStatements(self):
        name = "test_prepared_statement"
        self.db.prepareStatement("SELECT * FROM test",name)
        self.assertEquals("test_prepared_statement",name)
        name = None
        prepared,name = self.db.prepareStatement("SELECT * FROM test WHERE id=:1",name)
        self.assertIsNotNone(name)
        self.assertIsNotNone(prepared)
        try:
            params = [1]
            rows = self.db.execute(prepared,params)
            self.assertEquals(1,len(rows))
        except:
            self.assertTrue(False,"Unexpected exception during execute().")

    def testColumnsForTable(self):
        self.assertEquals(["id"],self.db.columnsForTable("test"))

    def testAllTables(self):
        self.assertEquals(["test"],self.db.allTables())

if __name__ == '__main__':
    unittest.main()
