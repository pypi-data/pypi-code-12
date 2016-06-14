import unittest
from ndb_adapter.advanced_search_options import AdvancedSearchOptions
from ndb_adapter.dna_search_options import DnaSearchOptions
from ndb_adapter.rna_search_options import RnaSearchOptions
from ndb_adapter.enums import *


class SearchOptionsTests(unittest.TestCase):
    def test_advanced_search_options(self):
        opt = AdvancedSearchOptions()
        opt.set_dna(AndOr.Or, YesNoIgnore.Yes)
        opt.set_na_pattern(AndOr.And, "ACGT")
        opt.set_cell_resolution(AndOr.And, 1.1)
        self.assertEqual(opt.get_dna(), (AndOr.Or, YesNoIgnore.Yes))
        self.assertEqual(opt.get_na_pattern(), (AndOr.And, "ACGT"))
        self.assertEqual(opt.get_cell_resolution(), (AndOr.And, 1.1))
        self.assertEqual(opt.get()["q_seqnc"], "ACGT")

        opt.reset()
        self.assertEqual(opt.get_dna(), (AndOr.And, YesNoIgnore.Ignore))
        self.assertEqual(opt.get_na_pattern(), (AndOr.And, ""))

        opt = AdvancedSearchOptions(ReportType.CellDimensions)
        self.assertEqual(opt.get()["search_report"], ReportType.CellDimensions.value.report_type())

    def test_dna_search_options(self):
        opt = DnaSearchOptions()
        opt.set_filter_text("args")
        opt.set_protein_func(ProteinFunc.Regulatory)
        self.assertEqual(opt.get_filter_text(), "args")
        self.assertEqual(opt.get_protein_func(), ProteinFunc.Regulatory)
        self.assertEqual(opt.get()["strGalType"], "dna")

    def test_rna_search_options(self):
        opt = RnaSearchOptions()
        opt.set_filter_text("args")
        opt.set_non_redundant_list(RnaStructures.NonRedundant, ResolutionCutoff.Four)
        self.assertEqual(opt.get_filter_text(), "args")
        self.assertEqual(opt.get_non_redundant_list(), (RnaStructures.NonRedundant, ResolutionCutoff.Four))
        self.assertEqual(opt.get()["strGalType"], "rna")

if __name__ == '__main__':
    unittest.main()
