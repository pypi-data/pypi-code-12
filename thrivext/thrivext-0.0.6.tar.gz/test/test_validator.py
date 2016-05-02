import unittest
import tempfile
import os
from thrivext import validator
import thrivext.descriptions as descr

dirname = os.path.dirname(__file__)


def make_tempfile():
    PREFIX = "testvalidator"
    SUFFIX = ".tmp"
    DIR = "/tmp"

    tf = tempfile.NamedTemporaryFile(suffix=SUFFIX,
                                     prefix=PREFIX,
                                     dir=DIR)
    return tf


def swrite(fileobj, txt):
    fileobj.write(txt)
    fileobj.seek(0)


class TestValidator(unittest.TestCase):
    with open(os.path.join(dirname, "testmapper1.py"), "r") as mf:
        MAPPER_CODE_1 = mf.read()

    with open(os.path.join(dirname, "testschema_valid.csv"), "r") as sf:
        SCHEMA_CODE_VALID = sf.read()

    with open(os.path.join(dirname, "testschema_invalid.csv"), "r") as isf:
        SCHEMA_CODE_INVALID = isf.read()

    with open(os.path.join(dirname, "testdata1.txt"), "r") as df:
        DATA_1 = df.read()

    with open(os.path.join(dirname, "testdata1_parsed.txt"), "r") as pdf:
        PARSED_DATA_1 = pdf.read()

    with open(os.path.join(dirname, "testmapper_noshebang.py"), "r") as nsb:
        MAPPER_CODE_NOSHEBANG = nsb.read()

    def setUp(self):
        self.mapperfile = make_tempfile()
        self.schemafile = make_tempfile()
        self.datafile = make_tempfile()
        self.reportfile = make_tempfile()
        self.parsed_data_file = make_tempfile()

    def tearDown(self):
        self.mapperfile.close()
        self.schemafile.close()
        self.datafile.close()
        self.reportfile.close()
        self.parsed_data_file.close()

    def test_initialize(self):
        swrite(self.mapperfile, TestValidator.MAPPER_CODE_1)
        swrite(self.schemafile, TestValidator.SCHEMA_CODE_VALID)
        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)
        self.assertEqual(TestValidator.MAPPER_CODE_1, v.mappercode)
        self.assertEqual(TestValidator.SCHEMA_CODE_VALID, v.schemacode)

    def test_get_coltypes(self):
        swrite(self.mapperfile, TestValidator.MAPPER_CODE_1)
        swrite(self.schemafile, TestValidator.SCHEMA_CODE_VALID)
        coltypes_expected = {
            0: "boolean",
            1: "int",
            2: "bigint",
            3: "float",
            4: "char(10)",
            5: "varchar(10)",
            6: "timestamp",
            7: "date"
        }

        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)
        v._get_coltypes()

        self.assertEqual(coltypes_expected, v.coltypes)
        self.assertEqual(len(coltypes_expected.keys()), v.colcount)

    def test_runmapper(self):
        swrite(self.mapperfile, TestValidator.MAPPER_CODE_1)
        swrite(self.schemafile, TestValidator.SCHEMA_CODE_VALID)
        swrite(self.datafile, TestValidator.DATA_1)

        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)
        v._runmapper()
        output_expected = TestValidator.PARSED_DATA_1
        self.assertEqual(output_expected, v.output)
        self.assertEqual("error message", v.error)

    def test_validate_shebang(self):
        swrite(self.mapperfile, TestValidator.MAPPER_CODE_1)
        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)
        passed = v._validate_shebang()
        self.assertEqual(
            v.report.sections[0].result,
            "PASS"
        )

        self.assertEqual(
            v.report.sections[0].name.lower(),
            "shebang validation"
        )

        self.assertEqual(
            v.report.sections[0].action,
            "None"
        )

        self.assertEqual(
            v.report.sections[0].details,
            "None"
        )

    def test_validate_noshebang(self):
        swrite(self.mapperfile, TestValidator.MAPPER_CODE_NOSHEBANG)
        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)
        passed = v._validate_shebang()
        self.assertEqual(
            v.report.sections[0].result,
            "FAIL"
        )

        self.assertEqual(
            v.report.sections[0].name.lower(),
            "shebang validation"
        )

        self.assertEqual(
            v.report.sections[0].action,
            descr.SHEBANG_ACTION
        )

        self.assertEqual(
            v.report.sections[0].details,
            descr.SHEBANG_DETAILS
        )

    def test_validate_coltypes_valid(self):
        swrite(self.schemafile, TestValidator.SCHEMA_CODE_VALID)
        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)

        v._validate_coltypes()
        self.assertEqual(
            v.report.sections[0].result,
            "PASS"
        )

        self.assertEqual(
            v.report.sections[0].name,
            "Column type validation"
        )

        self.assertEqual(
            v.report.sections[0].action,
            "None"
        )

        # schema_details_expected = \
        self.assertEqual(
            v.report.sections[0].details,
            "column number: 0, column type = boolean, ok\n"
            + "column number: 1, column type = int, ok\n"
            + "column number: 2, column type = bigint, ok\n"
            + "column number: 3, column type = float, ok\n"
            + "column number: 4, column type = char(10), ok\n"
            + "column number: 5, column type = varchar(10), ok\n"
            + "column number: 6, column type = timestamp, ok\n"
            + "column number: 7, column type = date, ok"
        )

    def test_validate_coltypes_invalid(self):
        swrite(self.schemafile, TestValidator.SCHEMA_CODE_INVALID)
        v = validator.Validator(self.mapperfile.name,
                                self.schemafile.name,
                                self.datafile.name,
                                self.reportfile.name)

        v._validate_coltypes()
        self.assertEqual(
            v.report.sections[0].result,
            "FAIL"
        )

        self.assertEqual(
            v.report.sections[0].name,
            "Column type validation"
        )

        self.assertEqual(
            v.report.sections[0].action,
            descr.COLUMN_TYPE_ACTION
        )

        self.assertEqual(
            v.report.sections[0].details,
            descr.COLUMN_TYPE_DETAILS
            + "\n"
            + "column number: 0, column type = currency, not in allowed types\n"
            + "column number: 1, column type = bigfloat, not in allowed types"
        )

if __name__ == "__main__":
    unittest.main()
