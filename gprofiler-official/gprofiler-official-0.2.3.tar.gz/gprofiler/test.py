import argparse
import re
import os
import subprocess
import sys
import unittest
import warnings

from gprofiler import GProfiler

class TestGProfilerOutputCached(unittest.TestCase):

    """
    A helper class for conveniently invoking the CLI tool, caching
    output for identical command lines.
    """

    TOOLPATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "gprofiler.py")
    DEVNULL = open(os.devnull, "w")
    CACHE = {}

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run_cli_tool(self, cmdline, columns=None):
        cmdline = self.TOOLPATH + " " + re.sub(r"\s+", " ", cmdline).strip()

        try:
            return self.CACHE[cmdline]
        except KeyError:
            pass

        res = subprocess.check_output(cmdline, shell=True) #, stderr=self.DEVNULL)
        lines = filter(lambda x: len(x) > 0, res.split("\n"))
        lines = map(lambda x: map(lambda y: y.strip(), x.split("\t")), lines)

        self.CACHE[cmdline] = lines
        return lines

class TestGProfilerOutput(TestGProfilerOutputCached):

    """
    Test cases for the GProfiler class. The g:GOSt interface is tested
    via the gprofiler.py CLI tool (TestGProfilerOutputCached class) to test
    the whole pipeline. Attempts to test whether the options to the tool /
    methods work correctly, not so much that upstream g:Profiler works
    correctly.
    """

    SCER_QUERY = "-o scerevisiae swi4 swi6 mbp1 mcm1 fkh1 fkh2 ndd1 swi5 ace2"
    SCER_BACKGROUND = """
        SNR53 SNR54 SNR55 SNR56 SNR57 SNR58 SNR59 SNR6 SNR61 SNR62 SNR63 SNR64 SNR65
        SNR66 SNR67 SNR68 SNR69 SNR70 SNR71 SNR72 SNR74 SNR75 SNR76 SNR77 SNR78 SNR8
        SNR86 SNR9 TG(CCC)D TG(CCC)O TL(GAG)G TLC1 TQ(CUG)M TR(ACG)J TR(CCG)L TR(CCU)J
        TS(AGA)D3 TT(CGU)K TX(XXX)D YAL001C YAL002W YAL003W YAL004W YAL005C YAL007C
        YAL008W YAL009W YAL010C YER111C YLR182W YDR146C"""
    HSAP_NUMERIC = """
        147290 120160 120215 182120 120150 120160 118661 120250 120215 605547 120215
        120190 610012 301870 610012 120130 118661 602514 118661 118661 602264 605261
        605399 135600 135600 120180 120180 135600"""

    QUERIES = [
        SCER_QUERY + " -a -H -E -e -f \"GO KEGG\" -b \"" + SCER_BACKGROUND + "\"",
        SCER_QUERY + " -a --min-set-size=10 --max-set-size=100 --min-isect-size=2",
        SCER_QUERY + " -a -p 0.9",
        SCER_QUERY,
        "-o hsapiens --numeric-ns=MIM_GENE_ACC " + HSAP_NUMERIC,
        "-o hsapiens -a -r X:0:500000"
    ]

    FIELD_LABELS = (
        "query", "significant", "p_value", "T", "Q", "Q&T", "precision", "recall", "term_id",
        "domain", "group", "description", "depth", "intersection", "evcodes"
    )

    # Query 0

    def test_all_results(self):
        self.succeeded = False

        def callback(f):
            if (re.search("biological_process", f["description"])):
                self.assertAlmostEqual(float(f["p_value"]), 1.0)
                self.succeeded = True
                return False
            return True

        self._foreach_result_line(0, callback)

        if (not self.succeeded):
            self.fail("No \"biological_process\" term in result")

    def test_source_filter(self):
        self._foreach_result_line(0, lambda f:
            self.assertRegexpMatches(f["term_id"], r"^(GO|KEGG)\:"))

    def test_hier_sorting(self):
        self.succeeded = False

        def callback(f):
            if (int(f["depth"]) != 1):
                self.succeeded = True
                return False

        self._foreach_result_line(0, callback)

        if (not self.succeeded):
            self.fail("No hierarchical sorting detected in result")

    def test_evcodes(self):
        res = self._run_query(0)
        self.assertRegexpMatches(res[0][14], r"^[A-Z]+")

    def test_noiea(self):
        self._foreach_result_line(0, lambda f:
            self.assertNotRegexpMatches(f["evcodes"], r"\bIEA\b"))

    def test_background(self):
        self._foreach_result_line(0, lambda f:
            self.assertRegexpMatches(f["intersection"], r"^(SWI\d,?)+$"))

    # Query 1

    def test_max_set_size(self):
        self._foreach_result_line(1, lambda f:
            self.assertLessEqual(int(f["T"]), 100))

    def test_min_set_size(self):
        self._foreach_result_line(1, lambda f:
            self.assertGreaterEqual(int(f["T"]), 10))

    def test_min_isect_size(self):
        self._foreach_result_line(1, lambda f:
            self.assertGreaterEqual(int(f["Q&T"]), 2))

    # Query 2

    def test_max_p_value(self):
        self._foreach_result_line(2, lambda f:
            self.assertLessEqual(float(f["p_value"]), 0.9))

    # Query 3

    def test_hier_filtering(self):

        """
        Assert that stronger hierarchical filtering produces less than or
        equal number of results compared to the previous level. A warning is
        generated if the sequence is not strictly monotonically decreasing.
        """

        results = self._run_query(3, "--hier-filtering=moderate", "--hier-filtering=strong")

        n_terms_normal = len(results[0])
        n_terms_mod = len(results[1])
        n_terms_str = len(results[2])

        self.assertGreaterEqual(n_terms_normal, n_terms_mod)
        self.assertGreaterEqual(n_terms_mod, n_terms_str)

        if (n_terms_normal == n_terms_mod or n_terms_mod == n_terms_str):
            warnings.warn("n_normal_results > n_moderate_results > n_strong_results is not true")

    def test_domain_size(self):
        self._assert_diff(*(self._run_query(3, "--domain-size=known")))

    def test_underrep(self):
        self._assert_diff(*(self._run_query(3, "--underrep")))

    def test_correction_method(self):
        res_gscs_fdr = self._run_query(3, "--correction-method=fdr")
        res_gscs_bonf = self._run_query(3, "--correction-method=bonferroni")

        res_gscs = res_gscs_fdr[0]
        res_fdr = res_gscs_fdr[1]
        res_bonf = res_gscs_bonf[1]

        self._assert_diff(res_gscs, res_fdr)
        self._assert_diff(res_gscs, res_bonf)
        self._assert_diff(res_fdr, res_bonf)

    # Query 4

    def test_numeric_namespace(self):
        
        # Assert numeric NS query returns at least 10 terms.
        
        res = self._run_query(4)
        self.assertGreaterEqual(len(res), 10)

    # Query 5

    def test_region_query(self):

        # Assert region query returns at least 10 terms.

        res = self._run_query(5)
        self.assertGreaterEqual(len(res), 10)

    # Private methods

    def _run_query(self, i, *extra):

        """
        Run a query from QUERIES with index i and return the result. Any
        number of extra string arguments may be passed. In such case, len(extra)
        additional queries are run, with the argument appended to the command
        line. A list of results is returned.
        """

        query = self.QUERIES[i]
        results = self.run_cli_tool(query)

        if (extra):
            results = [results]

            for param in (extra):
                this_query = query + " " + param
                results.append(self.run_cli_tool(this_query))

        return results

    def _foreach_result_line(self, res, callback, *extra):

        """
        Invoke the callback for each result line, passing a dict of the
        fields, labeled according to FIELD_LABELS; and any extra parameters. If
        the callback returns False, the method returns immediately. res may be
        an integer, in this case the query with the given index is run
        automatically.
        """

        if (type(res) is int):
            res = self._run_query(res)

        for line in res:
            fields = {}

            for i, v in enumerate(line):
                fields[self.FIELD_LABELS[i]] = v
            if (callback(fields, *extra) == False):
                return

    def _assert_diff(self, res1, res2):

        """
        Assert that two results are different by comparing term IDs and
        associated p-values.
        """

        term2pval1 = {}
        term2pval2 = {}

        def callback(f, term2pval):
            term2pval[f["term_id"]] = f["p_value"]

        self._foreach_result_line(res1, callback, term2pval1)
        self._foreach_result_line(res2, callback, term2pval2)

        self.assertNotEqual(term2pval1, term2pval2)

def get_tests_to_run():
    tests = []
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--tests", default=None, help="Comma-separated list of test IDs to run")
    args = parser.parse_args()

    if (args.tests):
        tests = map(lambda x: x.strip(), args.tests.split(","))
    return tests

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests_to_run = get_tests_to_run()
    test_methods = []
    suite = None

    if (tests_to_run):
        for tid in (tests_to_run):
            test_methods.append("TestGProfilerOutput.test_" + tid)
        suite = loader.loadTestsFromNames(test_methods, module=sys.modules[__name__])
    else:
        suite = loader.loadTestsFromTestCase(TestGProfilerOutput)

    unittest.TextTestRunner(verbosity=2).run(suite)
