from jinja2 import Environment, PackageLoader


class Section(object):
    """
    Class for representing a section of the report. Section captures the results and
    actions of a specification validation (for example Shebang). Report consists of
    several sections
    """
    def __init__(self, name, result="pass", action="", details=""):
        """
        Initialize a section instance with name, result, action and details

        @type name: str
        @param name: Name of the seciton

        @type result: str
        @param result: Result of validation with possible values: "pass" or "fail"

        @type action: str
        @param action: A possible action that might help pass the validation check

        @type details: str
        @param details: Place to write to details on this validation

        @rtype: None
        @return: None
        """
        self.name = name
        self.result = result
        self.details = details
        self.action = action


class Report(object):
    """
    Class for representing report of a validation action. A report is simply a collection
    of sections
    """
    def __init__(self):
        """
        Report is initialized with an empty list of sections

        @rtype: None
        @return: none
        """
        self.sections = []

    def add_section(self, section):
        """
        Adds 'section' to report

        @type section: Section
        @param section: A section, possibly populated with name, result, action, and details

        @rtype: None
        @return: None
        """
        if isinstance(section, Section):
            self.sections.append(section)


class ReportGenerator(object):
    """
    Base report generator class for factoring out common report generation code. Currently
    this includes only initialization, but has potential to expand later. Subclasses provide
    the generate() method which renders the report instance into the requested format.
    """

    # Default report file name
    DEFAULT_TEXT_OUTPUT = "./report.txt"
    DEFAULT_HTML_OUTPUT = "./report.html"

    def __init__(self, report):
        """
        Initializes report generator with instance of a Report.

        @type report: Report
        @param report: Report instance that will be rendered in requested format

        @rtype: None
        @return: None
        """
        self.report = report


class TextReportGenerator(ReportGenerator):
    """
    Class for rendering report into Text output format. Currently not implemented.
    """
    def generate(self, outfile=ReportGenerator.DEFAULT_TEXT_OUTPUT):
        """
        Renders self.report into text format

        @type outfile: str
        @param outfile: Full path of the output file.

        @rtype: None
        @return: None
        """

        pass


class HtmlReportGenerator(ReportGenerator):
    """
    Class for rendering report into HTML output format.
    """
    def generate(self, outfile=ReportGenerator.DEFAULT_HTML_OUTPUT):
        """
        Renders self.report into HTML format by populating a Jinja2 template.

        @type outfile: str
        @param outfile: Full path of the output file.

        @rtype: None
        @return: None
        """

        env = Environment(
            loader=PackageLoader("thrivext", "templates")
        )

        template = env.get_template("report_template.html")
        context = {
            "report": self.report
        }

        with open(outfile, "w") as fout:
            fout.write(template.render(context))