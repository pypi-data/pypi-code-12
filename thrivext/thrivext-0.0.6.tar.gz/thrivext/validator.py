import re
import subprocess as sp
from collections import defaultdict
import sys
from datatypes import *
from reporting import Report, Section, HtmlReportGenerator
import descriptions
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] [%(name)-0.50s.%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Validator(object):
    """
    Class for validating the BU-submitted artifacts. The Validator is a work in progress.
    Meaning, any additional validations will be added as separate validate_*() methods
    and invoked in the run() method.
    """

    # Class variables

    # Mapping of SQL types to Python types
    TYPEMAP = {
        "boolean": Boolean,
        "int": Integer,
        "bigint": Integer,
        "float": Float,
        "char": str,
        "varchar": str,
        "timestamp": Timestamp,
        "date": Date
    }

    # Delimiter separating consecutive fields in a Row
    DELIM = "\x01"

    # Regex for SHEBANG validation
    RE_SHEBANG = "^\s*#!\s*/usr/bin/python"

    # Regex for Varchar detection
    # RE_CHARTYPE = "VARCHAR\s*\(\s*[0-9]+\s*\)"
    RE_CHARTYPE = "(^\s*VARCHAR|^\s*CHAR)\s*\(\s*[0-9]+\s*\)"

    # Allowed types other than CHAR and VARCHAR. CHAR and VARCHAR are
    # handled separately
    ALLOWED_TYPES = ["TIMESTAMP", "INT", "BIGINT", "BOOLEAN", "FLOAT", "DATE"]

    def __init__(self, mapperfile, schemafile, datafile, reportfile):
        """
        Initialize the validator with mapper, schema and data files

        @type mapperfile: str
        @param mapperfile: Full or relative path to the mapper file

        @type schemafile: str
        @param schemafile: Full or relative path to the schema file

        @type datafile: str
        @param datafile: Full or relative path to the data file

        @type reportfile: str
        @param datafile: Full or relative path where the report file should be placed

        @rtype: None
        @return: None
        """

        self.datafile = datafile
        self.mapperfile = mapperfile
        self.reportfile = reportfile
        self.output = self.error = ""
        self.colcount = 0
        self.coltypes = dict()
        self._initialize(mapperfile, schemafile)

        # Instantiate a report object to aggregate results of different validations
        self.report = Report()

    def _initialize(self, mapperfile, schemafile):
        """
        Reads mapper.py and columns.csv and stores the content as strings

        @type mapperfile: str
        @param mapperfile: Full or relative path to the mapper file

        @type schemafile: str
        @param schemafile: Full or relative path to the schema file

        @rtype: None
        @return: None
        """
        with open(mapperfile, "r") as mf:
            self.mappercode = mf.read()

        with open(schemafile, "r") as sf:
            self.schemacode = sf.read()

        logger.debug("Initialized Validator")

    def _get_coltypes(self):
        """
        Reads the schema file and parses out the type of all columns.

        @rtype: None
        @return: None
        """
        try:
            colnum = 0
            for linenum, line in enumerate(self.schemacode.splitlines()):
                line = line.strip()
                if line != "":
                    # Column name and column type are assumed to be the first two
                    # space-separated strings
                    colname, coltype = line.split(" ", 1)
                    self.coltypes.update({colnum: coltype})

                    # Column number get updated only if a non-empty line is encountered
                    colnum += 1

            # Update self.colcount as a convenience variable
            self.colcount = len(self.coltypes.keys())
            logger.debug("Extracted column types from schema file")
        except Exception as ex:
            logger.error("Error in column type extraction. Message: %s" % ex.message)

    def _runmapper(self):
        """
        Runs mapper.py and populates the self.output and self.error fields. Currently the
        mapper output is stored fully into self.output. To handle more input data, the
        mapper running process has to be made more scalable by lazy generation of mapper
        output.

        @rtype: None
        @return: None
        """

        try:
            # Create a mapper sub-process
            mapper_process = sp.Popen("python %s " % self.mapperfile,
                                      stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE,
                                      shell=True, bufsize=0)

            # Send the data file through the mapper and construct output and error rows
            # TODO: Turn mapper outputs into generator objects to handle large data sizes
            with open(self.datafile, "r") as df:
                self.output, self.error = mapper_process.communicate(input=df.read())
            logger.debug("Ran mapper code on sample data")
        except Exception as ex:
            logger.error("Error running mapper on sample data. Message: %s" % ex.message)

    def _validate_shebang(self):
        """
        Validates that first nonempty line of mapper.py is a shebang and adds a section to
        the report

        @rtype: bool
        @return: True if validation passed, else false.
        """

        try:
            found = re.findall(Validator.RE_SHEBANG, self.mappercode)

            passed = found
            if passed:
                result, action, details = "PASS", "None", "None"
            else:
                result, action, details = "FAIL", descriptions.SHEBANG_ACTION, descriptions.SHEBANG_DETAILS

            self.report.add_section(
                Section(name="Shebang validation",
                        result=result,
                        action=action,
                        details=details)
            )

            return passed
        except Exception as ex:
            logger.error("Error in shebang validation. Message: %s" % ex.message)
            return False

    def _validate_coltypes(self):
        """
        Validates that column types in the schema file (column.csv) are of allowed types
        and adds a section to the report.

        @rtype: bool
        @return: True if validation passed, else false.
        """

        # Get data types of all columns from the schema file
        self._get_coltypes()

        msgs = []
        passed = True

        try:
            for colnum, coltype in self.coltypes.items():
                valid_ = True
                # If coltype is not in allowed then check if its CHAR_TYPE
                if coltype.upper() not in Validator.ALLOWED_TYPES:
                    if not bool(re.match(Validator.RE_CHARTYPE, coltype.upper())):
                        valid_ = False

                # Add details on each column in schema
                if valid_:
                    msgs.append(
                        "column number: %d, column type = %s, ok"
                            % (colnum, coltype)
                    )
                else:
                    passed &= False
                    msgs.append(
                        "column number: %d, column type = %s, not in allowed types"
                            % (colnum, coltype)
                    )

            schema_details = "\n".join(msgs)

            if passed:
                result, action, details = "PASS", "None", schema_details
            else:
                result, action, details = "FAIL", descriptions.COLUMN_TYPE_ACTION, \
                                          "%s\n%s" % (descriptions.COLUMN_TYPE_DETAILS, schema_details)

            # TODO Check if Vertica VARCHAR length is >65000

            self.report.add_section(
                Section(name="Column type validation",
                        result=result,
                        action=action,
                        details=details)
            )

            return passed
        except Exception as ex:
            logger.error("Error validating column types. Message: %s" % ex.message)
            return False

    def _validate_colcount(self):
        """
        Validates that all output rows generated by the mapper have identical number of
        fields. Adds a section to the report.

        @rtype: bool
        @return: True if validation passed, else false.
        """

        try:
            # Output statistics of field founts in each row
            field_counts = defaultdict(int)
            for row in self.output.splitlines():
                numfields = len(row.split(Validator.DELIM))
                field_counts[numfields] += 1

            # Convert the defaultdict to regular dict
            field_counts = dict(field_counts)

            # The output of processing is a dict with key = numfields and value = count of
            # rows in output with 'numfields' fields. Validation requires that
            # (1) numfields = number of columns in columns.csv and
            # (2) The field_counts dictionary contain only one key with value equaling the
            #     number of rows with that 'numfields' fields.

            msgs = []
            passed = True
            if len(field_counts.keys()) > 1:
                msgs.append("Column count not equal for all data rows")
                passed &= False

            numfields = int(field_counts.keys()[0])
            if numfields != self.colcount:
                msgs.append("Column count in data: %d\nColumn count in schema: %d"
                            % (numfields, self.colcount))
                passed &= False

            colcount_details = "\n".join(msgs)
            if passed:
                result, action, details = "PASS", "None", colcount_details
            else:
                result, action, details = "FAIL", descriptions.COLUMN_COUNT_ACTION, \
                                          "%s\n%s" % (descriptions.COLUMN_COUNT_DETAILS, colcount_details)

            self.report.add_section(
                Section(name="Column count validation",
                        result=result,
                        action=action,
                        details=details)
            )

            return passed
        except Exception as ex:
            logger.error("Error validating column count. Message: %s" % ex.message)
            return False

    def _validate_colvals(self):
        """
        Loops through the output rows and confirms that all fields of all rows are
        consistent with their stated data type. Adds a section to the report. The
        validation is strict; that is even if one column in any of the rows is inconsistent,
        the validation fails.

        @rtype: bool
        @return: True if validation passed, else false.
        """
        try:
            passed = True

            # Get standardized column types. That is, column types obtained after stripping
            # (nn) from VARCHAR(nn) and lowercasing.
            std_coltypes = dict()
            for colnum, coltype in self.coltypes.items():
                if bool(re.match(Validator.RE_CHARTYPE, coltype.upper())):
                    std_coltypes.update({colnum: "varchar"})
                else:
                    std_coltypes.update({colnum: coltype.lower()})

            # Loop through column values in each row and match types
            msgs = []
            for rownum, rowdata in enumerate(self.output.splitlines()):
                fields = rowdata.split(Validator.DELIM)
                for colnum, coldata in enumerate(fields):
                    datatype = std_coltypes[colnum]

                    # Accept if the value is empty. Required to handle null values.
                    if str(coldata) == "":
                        continue

                    if not isinstance(coldata, Validator.TYPEMAP[datatype]):
                        passed &= False
                        msgs.append("rownum: %d, colnum: %d, datatype: %s, value: %s"
                              % (rownum, colnum, datatype, coldata)
                        )

            colval_details = "\n".join(msgs)
            if passed:
                result, action, details = "PASS", "None", colval_details
            else:
                result, action, details = "FAIL", descriptions.COLUMN_VALUE_ACTION, \
                                          "%s\n%s" % (descriptions.COLUMN_VALUE_DETAILS,
                                                      colval_details)

            self.report.add_section(
                Section(name="Column value validation",
                        result=result,
                        action=action,
                        details=details)
            )

            return passed
        except Exception as ex:
            logger.error("Error validating column values. Message: %s" % ex.message)
            return False

    def _validate_exceptions(self):
        """
        Checks if the mapper.py code is enclosed in a global try/except block
        """
        pass

    def run(self):
        """
        Runs mapper, all the validations and outputs the final report.

        @rtype: None
        @return: None
        """

        # Validate the Shebang line
        if self._validate_shebang():
            logger.info("Validate shebang: success")
        else:
            logger.info("Validate shebang: fail")

        # Validate data types of columns
        if self._validate_coltypes():
            logger.info("Validate column types: success")
        else:
            logger.info("Validate column types: fail")

        # Run the mapper process. This populates self.output and self.error.
        self._runmapper()

        # Exit if mapper run failed to produce output.
        if self.output.strip() == "":
            logger.info("Mapper run did not produce any output. Exiting.")
            return

        # Validate column count in each row
        if self._validate_colcount():
            logger.info("Validate column count: success")
            colcount_passed = True
        else:
            colcount_passed = False
            logger.info("Validate column count: fail")

        # If the column count test passed, validate data types in each column of every
        # row. If the column count test hasnt passed, theres no use in running column
        # value/content test.
        if colcount_passed:
            if self._validate_colvals():
                logger.info("Validate column values: success")
            else:
                logger.info("Validate column values: fail")

        # Generate HTML report
        try:
            reporter = HtmlReportGenerator(self.report)
            reporter.generate(outfile=self.reportfile)
        except Exception as ex:
            logger.error("Error generating report file. Message: %s" % ex.message)