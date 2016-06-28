import unittest
from deepthought.tests.DTTestCase import DTTestCase
from deepthought.core.DTModel import DTModel
from deepthought.utils.DTLog import DTLog
import json

class DTModelTest(DTTestCase):
    def initSQL(self,sql=""):
        return  sql + """
CREATE TABLE test_models (
	id integer PRIMARY KEY autoincrement,
	name text,
	status text
);
INSERT INTO test_models (id,name,status) VALUES (1,'A1','FAILURE');
INSERT INTO test_models (id,name,status) VALUES (2,'A2','SUCCESS');

CREATE TABLE table_a (
	id integer PRIMARY KEY autoincrement,
	name text
);
INSERT INTO table_a (id,name) VALUES (1,'A1');

CREATE TABLE table_b (
	id integer PRIMARY KEY autoincrement,
	name text,
	a_id int
);
INSERT INTO table_b (id,name,a_id) VALUES (1,'B1',1);
INSERT INTO table_b (id,name,a_id) VALUES (2,'B2',1);

CREATE TABLE table_a_to_b (
	id integer PRIMARY KEY autoincrement,
	name text,
	a_id int,
	b_id int
);
INSERT INTO table_a_to_b (id,name,a_id,b_id) VALUES (1,'AB1',1,1);
INSERT INTO table_a_to_b (id,name,a_id,b_id) VALUES (2,'AB2',1,2);

CREATE TABLE table_c (
	id integer PRIMARY KEY autoincrement,
	name text,
	b_id int
);
INSERT INTO table_c (id,name,b_id) VALUES (1,'C1',1);
INSERT INTO table_c (id,name,b_id) VALUES (2,'C2',1);
INSERT INTO table_c (id,name,b_id) VALUES (3,'C3',1);

CREATE TABLE table_d (
	id integer PRIMARY KEY autoincrement,
	name text,
	a_id int,
	a2_id int
);
INSERT INTO table_d (id,name,a_id,a2_id) VALUES (1,'D1',1,1);
INSERT INTO table_d (id,name,a_id,a2_id) VALUES (2,'D2',1,2);

CREATE TABLE table_aa (
	id integer primary key autoincrement,
	a_parent_id integer
);
INSERT INTO table_aa (id, a_parent_id) VALUES (3, 1);

CREATE TABLE table_aaa (
	id integer primary key autoincrement,
	aa_parent_id integer
);
INSERT INTO table_aaa (id, aa_parent_id) VALUES (4, 3);

CREATE TABLE table_e (
	id integer PRIMARY KEY autoincrement,
	name text,
	aa_id int
);
INSERT INTO table_e (id,name,aa_id) VALUES (1,'E1',3);
INSERT INTO table_e (id,name,aa_id) VALUES (2,'E2',3);
"""
    def testConstructor(self):
        test_str = '{"fruit": "apple", "color": "red"}'
        obj = DTModel(json.loads(test_str))
        self.assertEquals("apple",obj["fruit"])
        self.assertEquals("red",obj["color"])

    def testIsDirty(self):
        obj = TestModel(self.db.filter({"id":1}))
        self.assertFalse(obj.isDirty("new_key"))
        obj["new_key"] = "dirty"
        self.assertTrue(obj.isDirty("new_key"))

    def testSetToNull(self):
        obj = TestModel(self.db.filter({"id":1}))
        obj["name"] = None
        properties = obj.storageProperties(self.db)
        self.assertTrue("name" in properties and obj["name"] is None)

    def testUpsertFromStorage(self):
        #1. test recovery of parameters
        test = TestModel.upsert(self.db.filter({"id":1}),{})
        self.assertEquals("FAILURE",test["status"])
        test = TestModel.upsert(self.db.filter({"id":2}),{})
        self.assertEquals("SUCCESS",test["status"])

    def testUpsertSetter(self):
        # 1. test newly upserted setter
        test = TestModel.upsert(
            self.db.filter({1:0}),
            {"status":"FAILURE"}) #overridden by setter method
        self.assertEquals("SUCCESS",test["status"])
        # 2. test existing upsert setter
        test = TestModel.upsert(
            self.db.filter({"id":1}),
            {"status":"FAILURE"}) #overridden by setter method
        self.assertEquals("SUCCESS",test["status"])

    def testGetOne(self):
        # 1. test B.a_id->A
        test = ModelB(self.db.filter({"id":1}))
        self.assertEquals("A1",test["a"]["name"])
        # 2. test AB.a_id->A
        test = ModelAB(self.db.filter({"id":1}))
        self.assertEquals("A1",test["a"]["name"])

    def testGetMany(self):
        # 1. test A-B.a_id (one-to-many)
        test = ModelA(self.db.filter({"id":1}))
        self.assertEquals("B1",test["b_list"][0]["name"])
        self.assertEquals("B2",test["b_list"][1]["name"])

        # 2. test A->AB->B (many-to-many)
        test = ModelA(self.db.filter({"id":1}))
        self.assertEquals(2,len(test["b_list_weak"]))
        self.assertEquals("B1",test["b_list_weak"][0]["name"])
        self.assertEquals("B2",test["b_list_weak"][1]["name"])

        # 3. test A->AB->B->C (many-to-many+)
        test = ModelA(self.db.filter({"id":1}))
        self.assertEquals(3,len(test["c_list"]))
        self.assertEquals("C1",test["c_list"][0]["name"])
        self.assertEquals("C2",test["c_list"][1]["name"])
        self.assertEquals("C3",test["c_list"][2]["name"])

        # 4. test shortcut A->AB->C (many-to-many*)
        test = ModelA(self.db.filter({"id":1}))
        self.assertEquals("C1",test["c_list_optimized"][0]["name"])
        self.assertEquals("C2",test["c_list_optimized"][1]["name"])
        self.assertEquals("C3",test["c_list_optimized"][2]["name"])

        # 5. test A->D.a2_id
        test = ModelA(self.db.filter({"id":1}))
        self.assertEquals(1,len(test["d_list"]))
        self.assertEquals("D1",test["d_list"][0]["name"])

    def testSetOne(self):
        ModelA.upsert(self.db.qb().fail(),{"name":"testA"})
        test = ModelB(self.db.filter({"id":1}))
        test.setA("a",{"name":"testA"})
        self.assertEquals("testA",test["a"]["name"])

    def testUpsertManyByID(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(self.db.filter({"id":1}))
        # test A->B
        ModelA.upsert(a_filter,{"b_list":[1,3]})
        self.assertEquals("B1",test["b_list"][0]["name"])
        self.assertNotEquals("B2",test["b_list"][1]["name"])

    def testUpsertManyByIDBListWeak(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(self.db.filter({"id":1}))
        # 2. test A->AB->B
        ModelA.upsert(a_filter,{"b_list_weak":[1,3]})
        self.assertEquals("B1",test["b_list_weak"][0]["name"])
        self.assertNotEquals("B2",test["b_list_weak"][1]["name"])

    def testUpsertManyByIDCList(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(a_filter)
        # test A->AB->B->C
        ModelA.upsert(a_filter,{"c_list":[1,2,4]})

        self.assertEquals("C1",test["c_list"][0]["name"])
        self.assertEquals("C2",test["c_list"][1]["name"])
        self.assertEquals(4,test["c_list"][2]["id"])

    def testUpsertManyByIDOptimized(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(a_filter)
        # test A->AB->C (shortcut)
        ModelA.upsert(a_filter,{"c_list_optimized":[1,2,4]})
        self.assertEquals("C1",test["c_list_optimized"][0]["name"])
        self.assertEquals("C2",test["c_list_optimized"][1]["name"])
        self.assertEquals(4,test["c_list_optimized"][2]["id"])

    def testUpsertManyByIDDList(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(a_filter)
        # test A->D.a2_id
        ModelA.upsert(a_filter,{"d_list":[1,3]})
        self.assertEquals("D1",test["d_list"][0]["name"])
        self.assertNotEquals("D2",test["d_list"][1]["name"])

    def testUpsertManyByIDWithParams(self):
        a_filter = self.db.filter({"id":1})
        ModelA.upsert(a_filter,{"c_list":[
            {"id":1,"name":"C1"},
            {"id":2,"name":"C2"},
            {"id":3,"name":"C4"}
        ]})
        test = ModelA(a_filter)
        self.assertEquals("C1",test["c_list"][0]["name"])
        self.assertEquals("C2",test["c_list"][1]["name"])
        self.assertNotEquals("C3",test["c_list"][2]["name"])

    def testUpsertManyByParams(self):
        a_filter = self.db.filter({"id":1})
        test = ModelA(a_filter)
        ModelA.upsert(a_filter,{"c_list_tags":["C1","C2","C4"]})
        self.assertEquals("C1",test["c_list"][0]["name"])
        self.assertEquals("C2",test["c_list"][1]["name"])
        self.assertNotEquals("C3",test["c_list"][2]["name"])

    def testParent(self):
        aa_filter = ModelAA.isAQB(self.db.filter({"ModelAA.id":3}))
        test = ModelAA(aa_filter)
        self.assertEquals("A1",test["name"])

    def testGrandparent(self):
        aaa_filter = ModelAAA.isAQB(self.db.filter({"ModelAAA.id":4}))
        test = ModelAAA(aaa_filter)
        self.assertEquals("A1",test["name"])

    def testManyToManyViaParent(self):
        aa_filter = ModelAA.isAQB(self.db.filter({"ModelAA.id":3}))
        test = ModelAA(aa_filter)
        self.assertEquals("B1",test["b_list"][0]["name"])
        self.assertEquals("B2",test["b_list"][1]["name"])

    def testManyToManyViaGrandparent(self):
        aaa_filter = ModelAAA.isAQB(self.db.filter({"ModelAAA.id":4}))
        test = ModelAAA(aaa_filter)

        # this comes from the grandparent class
        self.assertEquals("B1",test["b_list"][0]["name"])
        self.assertEquals("B2",test["b_list"][1]["name"])

        # only the parent knows how to do this one-to-many
        self.assertEquals("E1",test["e_list"][0]["name"])
        self.assertEquals("E2",test["e_list"][1]["name"])

        #only

    def testClosure(self):
        a = ModelA(self.db.filter({"id":1}))
        default = {}
        closure,default = a.closure(["DTModelTest.ModelAB","DTModelTest.ModelB"],default)
        self.assertEquals({
            "ModelA":{'1':'1'},
            "ModelAB":{'1':'1','2':'1'},
            "ModelB":{'2':'2','1':'1'}
        },closure)

        a["b_list_weak"] = ["1"]
        b = ModelB(self.db.filter({"name": "B2"}))
        self.assertEquals(2,b["id"]) # make sure we haven't wiped out the B list

class TestModel(DTModel):
    storage_table = "test_models"
    status = None

    def setstatus(self,val):
        self.status = "SUCCESS"

class ModelA(DTModel):
    storage_table = "table_a"
    has_many_manifest = {
        "b_list":["DTModelTest.ModelB"],
        "b_list_weak":["DTModelTest.ModelAB","DTModelTest.ModelB"],
        "c_list":["DTModelTest.ModelAB","DTModelTest.ModelB","DTModelTest.ModelC"],
        "c_list_optimized":[("DTModelTest.ModelAB","b_id"),("DTModelTest.ModelC","b_id")],
        "d_list":[("DTModelTest.ModelD","a2_id")]
    }
    name = ""
    c_list = None
    b_list_weak = None
    d_list = None

    def clist(self):
        return self.getMany("c_list",self.db.qb().orderBy("ModelC.id"))

    def clistoptimized(self):
        return self.getMany("c_list_optimized",self.db.qb().orderBy("ModelC.id"))

    def cListTagBuilder(self,key,vals):
        out = []
        for i in vals:
            out.append({"name":i})
        return out

    def setclisttags(self,vals):
        return self.setMany("c_list",vals,self.cListTagBuilder)

class ModelB(DTModel):
    storage_table = "table_b"
    has_a_manifest = {
        "a":["DTModelTest.ModelA","a_id"]
    }
    has_many_manifest = {
        "c_list":["DTModelTest.ModelC"]
    }
    name = ""

class ModelAB(DTModel):
    storage_table = "table_a_to_b"
    has_a_manifest = {
        "a":["DTModelTest.ModelA","a_id"],
        "b":["DTModelTest.ModelB","b_id"]
    }
    name = ""
    a_id =0
    b_id =0

class ModelC(DTModel):
    storage_table = "table_c"
    has_a_manifest = {
        "b":["DTModelTest.ModelB","b_id"]
    }
    name = ""

class ModelD(DTModel):
    storage_table = "table_d"
    has_a_manifest = {
        "a":["DTModelTest.ModelA","a_id"],
        "a2":["DTModelTest.ModelA","a2_id"]
    }
    name = None
    a_id = None
    a2_id = None

class ModelAA(ModelA):
    storage_table = "table_aa"
    is_a_manifest = {"a_parent_id":"DTModelTest.ModelA"}
    has_many_manifest = {"e_list":["DTModelTest.ModelE"]}

class ModelAAA(ModelAA):
    storage_table = "table_aaa"
    is_a_manifest = {"aa_parent_id":"DTModelTest.ModelAA"}

class ModelE(DTModel):
    storage_table = "table_e"
    has_a_manifest = {
        "aa":["DTModelTest.ModelAA","aa_id"]
    }
    name = None
    aa = None

if __name__ == '__main__':
    unittest.main()
