import unittest
from os import getcwd, path
from io import BytesIO
from ndb_adapter import report_parser, NDBStatusReport


class ReportParserTests(unittest.TestCase):

    def test_parse_to_table(self):
        to_test = "one\ntwo\nthree"
        table = report_parser.parse_to_table(to_test)
        self.assertEqual(table, ["one", "two", "three"])

    def test_parse_csv(self):
        to_test = ["NDB ID,PDB ID,Title,Authors,Initial Deposition Date,NDB Release Date",
                   "5DG7,5DG7,\"CRYSTAL STRUCTURE OF HUMAN DNA POLYMERASE ETA INSERTING dTTP ACROSS" +
                   "A DNA TEMPLATE CONTAINING 1,N6-ETHENODEOXYADENOSINE LESION\",\"Patra, A., Su, Y.," +
                   " Zhang, Q., Johnson, K.M., Guengerich, F.P., Egli, M.\",2015-08-27,2016-06-08",
                   "5DG8,5DG8,\"CRYSTAL STRUCTURE OF HUMAN DNA POLYMERASE ETA INSERTING dAMPNPP ACROSS" +
                   "A DNA TEMPLATE CONTAINING 1,N6-ETHENODEOXYADENOSINE LESION\",\"Patra, A., Su, Y.," +
                   "Zhang, Q., Johnson, K.M., Guengerich, F.P., Egli, M.\",2015-08-27,2016-06-08"]
        result = report_parser.parse_csv(table=to_test, result_class=NDBStatusReport)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ndb_id, "5DG7")
        self.assertEqual(result[1].release_date, "2016-06-08")

    def test_parse_xls(self):
        with open(getcwd() + path.sep + "test.xls", "rb") as file:
            result = report_parser.parse_xls(BytesIO(file.read()))
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0].ndb_id, "5DG7")
            self.assertEqual(result[1].release_date, "2016-06-08")

if __name__ == '__main__':
    unittest.main()
