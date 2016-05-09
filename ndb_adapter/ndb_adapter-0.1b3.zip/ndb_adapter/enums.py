from enum import Enum

from ndb_adapter.search_report import NDBStatusReport, CellDimensionsReport, CitationReport, RefinementDataReport, \
    NABackboneTorsionReport, BasePairParameterReport, BasePairStepParameterReport, DescriptorReport, SequencesReport, \
    RNA3DBasePairRelFreqReport, RNA3DBasePhosphateRelFreqReport, RNA3DBaseStackingRelFreqReport, RNA3DMotifReport


class ReportType(Enum):
    """Enum representing advanced search report type - can be used to annotate return type of advanced search report

    :cvar NDBStatus: NDB Status search report
    :cvar CellDimensions: Cell Dimensions search report
    :cvar Citation: Citation search report
    :cvar RefinementData: Refinement Data search report
    :cvar NABackboneTorsion: NA Backbone Torsion search report
    :cvar BasePairParameter: Base Pair Parameter search report
    :cvar BasePairStepParameter: Base Pair Step Parameter search report
    :cvar Descriptor: Descriptor search report
    :cvar Sequences: Sequences search report
    :cvar RNABasePairRelFreq: RNA 3D Base Pair Relative Frequency search report
    :cvar RNABasePhosphateRelFreq: RNA 3D Base Phosphate Relative Frequency search report
    :cvar RNABaseStackingRelFreq: RNA 3D Base Stacking Relative Frequency search report
    :cvar RNAMotif: RNA Motif search report
    """
    NDBStatus = NDBStatusReport
    CellDimensions = CellDimensionsReport
    Citation = CitationReport
    RefinementData = RefinementDataReport
    NABackboneTorsion = NABackboneTorsionReport
    BasePairParameter = BasePairParameterReport
    BasePairStepParameter = BasePairStepParameterReport
    Descriptor = DescriptorReport
    Sequences = SequencesReport
    RNABasePairRelFreq = RNA3DBasePairRelFreqReport
    RNABasePhosphateRelFreq = RNA3DBasePhosphateRelFreqReport
    RNABaseStackingRelFreq = RNA3DBaseStackingRelFreqReport
    RNAMotif = RNA3DMotifReport


class Polymer(Enum):
    """Enums to handle polymer in query

    :cvar All: all in query
    :cvar DNAOnly: DNA Only in query
    :cvar ProteinDNA: Protein DNA Complexes in query
    :cvar DrugDNA: Drug DNA Complexes in query
    :cvar HybridsChimera: Hybrids and Chimera in query
    :cvar PeptideNucleicAcid: Peptide Nucleic Acid / Mimetics in query
    """
    All = 'all'
    DNAOnly = 'onlyDna'
    ProteinDNA = 'protDna'
    DrugDNA = 'drugDna'
    HybridsChimera = 'hybNChimera'
    PeptideNucleicAcid = 'pepNucAcid'


class ProteinFunc(Enum):
    """Enums to handle protein function in query

    :cvar All: all in query
    :cvar Enzymes: enzymes function in query
    :cvar Structural: structural function in query
    :cvar Regulatory: regulatory function in query
    :cvar Other: other function in query
    """
    All = 'all'
    Enzymes = 'enzymes'
    Structural = 'structural'
    Regulatory = 'regulatory'
    Other = 'other'


class StructuralFeatures(Enum):
    """Enums to handle structural features in query

    :cvar All: all in query
    :cvar SingleStranded: Single Stranded feature in query
    :cvar A_DNA: aDNA feature in query
    :cvar B_DNA: bDNA feature in query
    :cvar Z_DNA: zDNA feature in query
    :cvar OtherDoubleHelical: Other Double Helical Structures feature in query
    :cvar TripleHelices: Triple Helices feature in query
    :cvar QuadrupleHelices: Quadruple Helices feature in query
    """
    All = 'all'
    SingleStranded = 'single'
    A_DNA = 'A'
    B_DNA = 'B'
    Z_DNA = 'Z'
    OtherDoubleHelical = 'other'
    TripleHelices = 'triple'
    QuadrupleHelices = 'quadruple'


class ExpMethod(Enum):
    """Enum to handle experimental method in query

    :cvar All: all in query
    :cvar XRAY: x-ray in query
    :cvar NMR: nmr in query
    """
    All = 'all'
    XRAY = 'x-ray'
    NMR = 'nmr'


class RnaStructures(Enum):
    """Enum to handle rna structures option in query

    :cvar All: all in query
    :cvar NonRedundant: no redundant in query
    """
    All = 'all'
    NonRedundant = 'nr'


class ResolutionCutoff(Enum):
    """Enum to handle resolution cutoff options in query

    :cvar All: all in query
    :cvar Empty: empty in query
    :cvar OneHalf: 1.5 in query
    :cvar Two: 2.0 in query
    :cvar TwoHalf: 2.5 in query
    :cvar Three: 3.0 in query
    :cvar ThreeHalf: 3.5 in query
    :cvar Four: 4.0 in query
    :cvar Twenty: 20.0 in query
    """
    Empty = ''
    All = 'all'
    OneHalf = '1.5'
    Two = '2.0'
    TwoHalf = '2.5'
    Three = '3.0'
    ThreeHalf = '3.5'
    Four = '4.0'
    Twenty = '20.0'


class RnaType(Enum):
    """Enum to handle rna type options in query

    :cvar All: all in query
    :cvar TRNA: tRNA in query
    :cvar TRNAFrag: tRNA fragment in query
    :cvar Ribosome: Ribosome in query
    :cvar Ribozyme: Ribozyme in query
    :cvar Harpin: Hairpin Ribozyme in query
    :cvar Hammerhead: Hammerhead Ribozyme in query
    :cvar Group1Intron: Group I intron Ribozyme in query
    :cvar Group2Intron: Group II intron Ribozyme in query
    :cvar RnaseP: Rnase P Ribozyme in query
    :cvar Polymerase: Polymerase Ribozyme in query
    :cvar Ligase: Ligase Ribozyme in query
    :cvar Leadzyme: Leadzyme in query
    :cvar RibozymeFrag: Ribozyme fragment in query
    :cvar Virus: Virus in query
    :cvar ViralFrag: Viral fragment in query
    :cvar Riboswitch: Riboswitch in query
    :cvar RiboswitchFrag: Riboswitch fragment in query
    :cvar Aptamer: Aptamer in query
    :cvar Leadzyme: Leadzyme in query
    """
    All = 'all'
    TRNA = 'trna'
    TRNAFrag = 'trnaFr'
    Ribosome = 'ribosome'
    Ribozyme = 'ribozyme'
    Harpin = 'hairpin'
    Hammerhead = 'hammhd'
    Group1Intron = 'gr1In'
    Group2Intron = 'gr2In'
    RnaseP = 'rnase'
    Polymerase = 'polymerase'
    Ligase = 'ligase'
    Leadzyme = 'leadzyme'
    RibozymeFrag = 'ribozymeFr'
    Virus = 'virus'
    ViralFrag = 'viralfr'
    Riboswitch = 'riboswitch'
    RiboswitchFrag = 'riboswitchFr'
    Aptamer = 'aptamer'
    Telomerase = 'telomerase'
    SmallNucleotideFrag = 'singleStranded'
    DoubleHelices = 'duplex'
    TripleHelices = 'triplexes'
    QuadrupleHelices = 'quadruplexes'


class YesNoIgnore(Enum):
    """Enum to handle "yes", "no", "ignore" in query

    :cvar Yes: yes in query
    :cvar No: no in query
    :cvar Ignore: ignore in query
    """
    Yes = 'Y'
    No = 'N'
    Ignore = 'Ignore'


class AndOr(Enum):
    """Enum to handle "and", "or" in query

    :cvar And: and in query
    :cvar Or: or in query
    """
    And = "AND"
    Or = "OR"


class DnaRnaEither(Enum):
    """Enum to handle "dna", "rna", "either" in query

    :cvar DNA: dna in query
    :cvar RNA: rna in query
    :cvar Either: either in query
    """
    DNA = 'DNA'
    RNA = 'RNA'
    Either = 'EITHER'


class GreaterLower(Enum):
    """Enum to handle ">=", "<=" in query

    :cvar GreaterEqual: >= in query
    :cvar LowerEqual: <= in query
    """
    GreaterEqual = 'gtEq'
    LowerEqual = 'ltEq'


class GreaterLowerEqual(Enum):
    """Enum to handle ">=", "<=", "==" in query

    :cvar GreaterEqual: >= in query
    :cvar LowerEqual: <= in query
    :cvar Equal: == in query
    """
    Equal = 'eq'
    GreaterEqual = 'gtEq'
    LowerEqual = 'ltEq'


class DrugBinding(Enum):
    """Enum to handle nucleic acid drug bindings options in query

    :cvar Empty: empty value in query
    :cvar Intercalation: Intercalation in query
    :cvar OutsideBinder: Outside binder in query
    :cvar IntercalationCovalent: Intercalation, covalent in query
    :cvar OutsideBinderCovalent: Outside binder, covalent in query
    :cvar MajorGrooveBinder: Major groove binder in query
    :cvar MinorGrooveBinder: Minor groove binder in query
    :cvar MajorGrooveBinderCovalent: Major groove binder, covalent in query
    :cvar MinorGrooveBinderCovalent: Minor groove binder, covalent in query
    :cvar BisIntercalation: Bis-Intercalation in query
    :cvar DoubleMajorGrooveBinder: Double major groove binder in query
    :cvar DoubleMinorGrooveBinder: Double minor groove binder in query
    :cvar CovalentMetalBonds: Covalent metal bonds in query
    """
    Empty = ''
    Intercalation = 'Intercalation'
    OutsideBinder = 'Outside binder'
    IntercalationCovalent = 'Intercalation, Covalent'
    OutsideBinderCovalent = 'Outside binder, Covalent'
    MajorGrooveBinder = 'Major Groove Binder'
    MinorGrooveBinder = 'Minor Groove Binder'
    MajorGrooveBinderCovalent = 'Major Groove Binder, Covalent'
    MinorGrooveBinderCovalent = 'Minor Groove Binder, Covalent'
    IntercalationMajorGrooveBinder = 'Intercalation, Major Groove Binder'
    IntercalationMinorGrooveBinder = 'Intercalation, Minor Groove Binder'
    BisIntercalation = 'Bis-Intercalation'
    DoubleMajorGrooveBinder = 'Double Major Groove Binder'
    DoubleMinorGrooveBinder = 'Double Minor Groove Binder'
    CovalentMetalBonds = 'Covalent Metal Bonds'


class SpaceGroup(Enum):
    """Enum to handle space group in query

    :cvar Empty: empty value in query
    :cvar B_2_21_2: 'B 2 21 2' in query
    :cvar C_1_2_1: 'C 1 2 1' in query
    :cvar C_2_2_2: 'C 2 2 2' in query
    :cvar C_2_2_21: 'C 2 2 21' in query
    :cvar F_2_2_2: 'F 2 2 2' in query
    :cvar F_2_3: 'F 2 3' in query
    :cvar F_4_3_2: 'F 4 3 2' in query
    :cvar H_3: 'H 3' in query
    :cvar H_3_2: 'H 3 2' in query
    :cvar I_2_2_2: 'I 2 2 2' in query
    :cvar I_2_3: 'I 2 3' in query
    :cvar I_21_21_21: 'I 21 21 21' in query
    :cvar I_21_3: 'I 21 3' in query
    :cvar I_4: 'I 4' in query
    :cvar I_4_2_2: 'I 4 2 2' in query
    :cvar I_4_3_2: 'I 4 3 2' in query
    :cvar I_41: 'I 41' in query
    :cvar I_41_2_2: 'I 41 2 2' in query
    :cvar P_minus1: 'P -1' in query
    :cvar P_1: 'P 1' in query
    :cvar P_1_1_21: 'P 1 1 21' in query
    :cvar P_1_2_1: 'P 1 2 1' in query
    :cvar P_2_2_21: 'P 2 2 21' in query
    :cvar P_2_21_21: 'P 2 21 21' in query
    :cvar P_2_3: 'P 2 3' in query
    :cvar P_21_2_21: 'P 21 2 21' in query
    :cvar P_21_21_2: 'P 21 21 2' in query
    :cvar P_21_21_21: 'P 21 21 21' in query
    :cvar P_21_3: 'P 21 3' in query
    :cvar P_3: 'P 3' in query
    :cvar P_3_1_2: 'P 3 1 2' in query
    :cvar P_3_2_1: 'P 3 2 1' in query
    :cvar P_31: 'P 31' in query
    :cvar P_31_1_2: 'P 31 1 2' in query
    :cvar P_31_2_1: 'P 31 2 1' in query
    :cvar P_32: 'P 31' in query
    :cvar P_32_1_2: 'P 31 1 2' in query
    :cvar P_32_2_1: 'P 31 2 1' in query
    :cvar P_4: 'P 4' in query
    :cvar P_4_2_2: 'P 4 2 2' in query
    :cvar P_4_21_2: 'P 4 21 2' in query
    :cvar P_41: 'P 41' in query
    :cvar P_41_2_2: 'P 41 2 2' in query
    :cvar P_41_21_2: 'P 41 21 2' in query
    :cvar P_42: 'P 42' in query
    :cvar P_42_2_2: 'P 42 2 2' in query
    :cvar P_42_21_2: 'P 42 21 2' in query
    :cvar P_43: 'P 43' in query
    :cvar P_43_2_2: 'P 43 2 2' in query
    :cvar P_43_21_2: 'P 43 21 2' in query
    :cvar P_6: 'P 6' in query
    :cvar P_6_2_2: 'P 6 2 2' in query
    :cvar P_61: 'P 61' in query
    :cvar P_61_2_2: 'P 61 2 2' in query
    :cvar P_62: 'P 62' in query
    :cvar P_62_2_2: 'P 62 2 2' in query
    :cvar P_63: 'P 63' in query
    :cvar P_63_2_2: 'P 63 2 2' in query
    :cvar P_64: 'P 64' in query
    :cvar P_64_2_2: 'P 64 2 2' in query
    :cvar P_65: 'P 65' in query
    :cvar P_65_2_2: 'P 65 2 2' in query
    :cvar R_3_2: 'R 3 2' in query
    """
    Empty = ''
    B_2_21_2 = 'B 2 21 2'
    C_1_2_1 = 'C 1 2 1'
    C_2_2_2 = 'C 2 2 2'
    C_2_2_21 = 'C 2 2 21'
    F_2_2_2 = 'F 2 2 2'
    F_2_3 = 'F 2 3'
    F_4_3_2 = 'F 4 3 2'
    H_3 = 'H 3'
    H_3_2 = 'H 3 2'
    I_2_2_2 = 'I 2 2 2'
    I_2_3 = 'I 2 3'
    I_21_21_21 = 'I 21 21 21'
    I_21_3 = 'I 21 3'
    I_4 = 'I 4'
    I_4_2_2 = 'I 4 2 2'
    I_4_3_2 = 'I 4 3 2'
    I_41 = 'I 41'
    I_41_2_2 = 'I 41 2 2'
    I_41_3_2 = 'I 41 3 2'
    P_minus1 = 'P -1'
    P_1 = 'P 1'
    P_1_1_21 = 'P 1 1 21'
    P_1_2_1 = 'P 1 2 1'
    P_1_21_1 = 'P 1 21 1'
    P_2_2_21 = 'P 2 2 21'
    P_2_21_21 = 'P 2 21 21'
    P_2_3 = 'P 2 3'
    P_21_2_21 = 'P 21 2 21'
    P_21_21_2 = 'P 21 21 2'
    P_21_21_21 = 'P 21 21 21'
    P_21_3 = 'P 21 3'
    P_3 = 'P 3'
    P_3_1_2 = 'P 3 1 2'
    P_3_2_1 = 'P 3 2 1'
    P_31 = 'P 31'
    P_31_1_2 = 'P 31 1 2'
    P_31_2_1 = 'P 31 2 1'
    P_32 = 'P 32'
    P_32_1_2 = 'P 32 1 2'
    P_32_2_1 = 'P 32 2 1'
    P_4 = 'P 4'
    P_4_2_2 = 'P 4 2 2'
    P_4_21_2 = 'P 4 21 2'
    P_41 = 'P 41'
    P_41_2_2 = 'P 41 2 2'
    P_41_21_2 = 'P 41 21 2'
    P_41_3_2 = 'P 41 3 2'
    P_42 = 'P 42'
    P_42_2_2 = 'P 42 2 2'
    P_42_21_2 = 'P 42 21 2'
    P_42_3_2 = 'P 42 3 2'
    P_43 = 'P 43'
    P_43_2_2 = 'P 43 2 2'
    P_43_21_2 = 'P 43 21 2'
    P_43_3_2 = 'P 43 3 2'
    P_6 = 'P 6'
    P_6_2_2 = 'P 6 2 2'
    P_61 = 'P 61'
    P_61_2_2 = 'P 61 2 2'
    P_62 = 'P 62'
    P_62_2_2 = 'P 62 2 2'
    P_63 = 'P 63'
    P_63_2_2 = 'P 63 2 2'
    P_64 = 'P 64'
    P_64_2_2 = 'P 64 2 2'
    P_65 = 'P 65'
    P_65_2_2 = 'P 65 2 2'
    R_3_2 = 'R 3 2'


class RFactor(Enum):
    """Enum to handle R-factor in query

    :cvar Empty: empty value in query
    :cvar R_10: 0.10 in query
    :cvar R_15: 0.15 in query
    :cvar R_20: 0.20 in query
    :cvar R_25: 0.25 in query
    :cvar R_30: 0.30 in query
    :cvar R_35: 0.35 in query
    """
    Empty = ''
    R_10 = '0.10'
    R_15 = '0.15'
    R_20 = '0.20'
    R_25 = '0.25'
    R_30 = '0.30'
    R_35 = '0.35'


class BasePair(Enum):
    """Enum for base pair interaction options in query. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#bp

    :cvar Empty: empty value in query
    :cvar CWW: (cis Watson-Crick/Watson-Crick) in query
    :cvar TWW: (trans Watson-Crick/Watson-Crick) in query
    :cvar CWH: (cis Watson-Crick/Hoogsteen) in query
    :cvar TWH: (trans Watson-Crick/Hoogsteen) in query
    :cvar CWS: (cis Watson-Crick/Sugar Edge) in query
    :cvar TWS: (trans Watson-Crick/Sugar Edge) in query
    :cvar CHH: (cis Hoogsteen/Hoogsteen) in query
    :cvar THH: (trans Hoogsteen/Hoogsteen) in query
    :cvar CHS: (cis Hoogsteen/Sugar Edge) in query
    :cvar THS: (trans Hoogsteen/Sugar Edge) in query
    :cvar CSS: (cis Sugar Edge/Sugar Edge) in query
    :cvar TSS: (trans Sugar Edge/Sugar Edge) in query
    """
    Empty = ''
    CWW = 'cWW'
    TWW = 'tWW'
    CWH = 'cWH'
    TWH = 'tWH'
    CWS = 'cWS'
    TWS = 'tWS'
    CHH = 'cHH'
    THH = 'tHH'
    CHS = 'cHS'
    THS = 'tHS'
    CSS = 'cSS'
    TSS = 'tSS'


class BasePhosphate(Enum):
    """Enum for base phosphate interaction in query. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#bph

    :cvar Empty: empty values in query
    :cvar BPh_1: 1BPh (base-phosphate position 1) in query
    :cvar BPh_2: 2BPh (base-phosphate position 2) in query
    :cvar BPh_3: 3BPh (base-phosphate position 3) in query
    :cvar BPh_4: 4BPh (base-phosphate position 4) in query
    :cvar BPh_5: 5BPh (base-phosphate position 5) in query
    :cvar BPh_6: 6BPh (base-phosphate position 6) in query
    :cvar BPh_7: 7BPh (base-phosphate position 7) in query
    :cvar BPh_8: 8BPh (base-phosphate position 8) in query
    :cvar BPh_9: 9BPh (base-phosphate position 9) in query
    :cvar BPh_0: 0BPh (base-phosphate position 10) in query
    """
    Empty = ''
    BPh_1 = '1BPh'
    BPh_2 = '2BPh'
    BPh_3 = '3BPh'
    BPh_4 = '4BPh'
    BPh_5 = '5BPh'
    BPh_6 = '6BPh'
    BPh_7 = '7BPh'
    BPh_8 = '8BPh'
    BPh_9 = '9BPh'
    BPh_0 = '0BPh'


class BaseStack(Enum):
    """Enum for base stack interaction in query. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#bs

    :cvar Empty: empty value in query
    :cvar S_33: s33 (stack, 3′ face on 3′ face) in query
    :cvar S_35: s35 (stack, 3′ face on 5′ face) in query
    :cvar S_55: s55 (stack, 5′ face on 5′ face) in query
    """
    Empty = ''
    S_33 = 's33'
    S_35 = 's35'
    S_55 = 's55'


class InternalLoopMotif(Enum):
    """Enum for internal loop motif in query

    :cvar Empty: empty value in query
    :cvar All: all motifs in query
    :cvar SarcinRicin: Sarcin-ricin motif in query
    :cvar KinkTurn: Kink-turn motif in query
    :cvar CLoop: C-loop motif in query
    :cvar DoubleSheared: Double-sheared motif in query
    :cvar TripleSheared: Triple-sheared motif in query
    """
    Empty = ''
    All = 'All'
    SarcinRicin = 'Sarcin-ricin'
    KinkTurn = 'Kink-turn'
    CLoop = 'C-loop'
    DoubleSheared = 'Double-sheared'
    TripleSheared = 'Triple-sheared'


class HairpinLoopMotif(Enum):
    """Enum for hairpin loop motif in query

    :cvar Empty: empty value in query
    :cvar All: all motifs in query
    :cvar TLoop: T-loop motif in query
    :cvar GNRA: GNRA motif in query
    :cvar UNCG: UNCG motif in query
    """
    Empty = ''
    All = 'All'
    TLoop = 'T-loop'
    GNRA = 'GNRA'
    UNCG = 'UNCG'


class EnzymeFunction(Enum):
    """Enum for enzyme function in query

    :cvar Empty: empty value in query
    :cvar All: all functions in query
    :cvar Topoisomerase: topoisomerase function in query
    :cvar Synthetase: synthetase function in query
    :cvar Thrombin: thrombin function in query
    :cvar DNAPolymerase: DNA polymarase function in query
    :cvar DNAReverseTranscriptase: DNA polymerase / reverse transcriptase function in query
    :cvar DNAEndonuclease: DNA nuclease / endonucelase function in query
    :cvar DNAExonuclease: DNA nuclease / exonucelase function in query
    :cvar Glycosylase: glycosylase function in query
    :cvar Helicase: helicase function in query
    :cvar Kinase: kinase function in query
    :cvar Ligase: ligase function in query
    :cvar Lyase: lyase function in query
    :cvar MethylaseMethytransferase: methylase or methyltransferase function in query
    :cvar MRNACapping: mRNA capping function in query
    :cvar Phosphatase: phosphatase function in query
    :cvar Integrase: recombinase / integrase function in query
    :cvar Invertase: recombinase / invertase function in query
    :cvar Resolvase: recombinase / resolvase function in query
    :cvar Transposase: recombinase / transposase function in query
    :cvar RecombinaseOther: recombinase / other function in query
    :cvar RNAPolymerase: RNA polymerase function in query
    :cvar RNAEndonuclease: RNA nuclease / endonuclease function in query
    :cvar RNAExonuclease: RNA nuclease / exdonuclease function in query
    :cvar TRNAModifying: tRNA Modifying function in query
    :cvar Other: other function in query
    """
    Empty = ''
    All = 'ENZYME'
    Topoisomerase = 'TOPOISOMERASE'
    Synthetase = 'SYNTHETASE'
    Thrombin = 'THROMBIN'
    DNAPolymerase = 'DNA POLYMERASE'
    DNAReverseTranscriptase = 'DNA POLYMERASE/REVERSE TRANSCRIPTASE'
    DNAEndonuclease = 'DNA NUCLEASE/ENDONUCLEASE'
    DNAExonuclease = 'DNA NUCLEASE/EXONUCLEASE'
    Glycosylase = 'GLYCOSYLASE'
    Helicase = 'HELICASE'
    Kinase = 'KINASE'
    Ligase = 'LIGASE'
    Lyase = 'LYASE'
    MethylaseMethytransferase = 'METHYLASE OR METHYLTRANSFERASE'
    MRNACapping = 'MRNA CAPPING'
    Phosphatase = 'PHOSPHATASE'
    Integrase = 'RECOMBINASE/INTEGRASE'
    Invertase = 'RECOMBINASE/INVERTASE'
    Resolvase = 'RECOMBINASE/RESOLVASE'
    Transposase = 'RECOMBINASE/TRANSPOSASE'
    RecombinaseOther = 'RECOMBINASE/OTHER'
    RNAPolymerase = 'RNA POLYMERASE'
    RNAEndonuclease = 'RNA NUCLEASE/ENDONUCLEASE'
    RNAExonuclease = 'RNA NUCLEASE/EXONUCLEASE'
    TRNAModifying = 'TRNA MODIFYING'
    Other = 'OTHER'


class RegulatoryFunction(Enum):
    """Enum for regulatory functions in query

    :cvar Empty: empty value in query
    :cvar All: all functions in query
    :cvar DnaRepairActivator: DNA repair activator function in query
    :cvar DnaRepairRepressor: DNA repair repressor function in query
    :cvar RecombinationActivator: recombination activator function in query
    :cvar RecombinationReporessor: recombination reporessor function in query
    :cvar ReplicationActivator: replication factor / activator function in query
    :cvar ReplicationReporessor: replication factor / reporessor function in query
    :cvar SpliceosomalProtein: spliceosomal protein function in query
    :cvar TranscriptionActivatorRepressor: transcription factor / activator and repressor function in query
    :cvar TranscriptionActivator: transcription factor / activator function in query
    :cvar TranscriptionCoactivator: transcription factor / coactivator function in query
    :cvar TranscriptionCorepressor: transcription factor / corepressor function in query
    :cvar TranscriptionElongation: transcription factor / elongation function in query
    :cvar Transcription: transcription factor in general in query
    :cvar TranscriptionReporessor: transcription factor / repressor function in query
    :cvar TranscriptionTermination: transcription factor / termination function in query
    :cvar TranslationElongation: translation factor / elongation function in query
    :cvar TranslationInitiator: translation factor / initiator function in query
    :cvar TranslationTermination: translation factor / termination function in query
    """
    Empty = ''
    All = 'REGULATORY'
    DnaRepairActivator = 'DNA Repair Activator'
    DnaRepairRepressor = 'DNA Repair Repressor'
    RecombinationActivator = 'Recombination Activator'
    RecombinationReporessor = 'Recombination Repressor'
    ReplicationActivator = 'Replication Factor/Activator'
    ReplicationReporessor = 'Replication Factor/Repressor'
    SpliceosomalProtein = 'Spliceosomal Protein'
    TranscriptionActivatorRepressor = 'Transcription Factor/Activator And Repressor'
    TranscriptionActivator = 'Transcription Factor/Activator'
    TranscriptionCoactivator = 'Transcription Factor/Coactivator'
    TranscriptionCorepressor = 'Transcription Factor/Corepressor'
    TranscriptionElongation = 'Transcription Factor/Elongation'
    Transcription = 'Transcription Factor/General'
    TranscriptionReporessor = 'Transcription Factor/Repressor'
    TranscriptionTermination = 'Transcription Factor/Termination'
    TranslationElongation = 'Translation Factor/Elongation'
    TranslationInitiator = 'Translation Factor/Initiator'
    TranslationTermination = 'Translation Factor/Termination'


class StructuralFunction(Enum):
    """Enum for structural functions in query

    :cvar Empty: empty value in query
    :cvar All: all functions in query
    :cvar Chromosomal: chromosomal function in query
    :cvar Histone: histone function in query
    :cvar HMG: hmg function in query
    :cvar Ribonucleoprotein: ribonucleoprotein function in query
    :cvar RibosomalProtein: ribosomal protein function in query
    :cvar SignalRecognitionParticle: signal recognition particle function in query
    :cvar TelomereBinding: telomere binding function in query
    :cvar ViralCoat: viral coat function in query
    """
    Empty = ''
    All = 'STRUCTURAL'
    Chromosomal = 'Chromosomal'
    Histone = 'Histone'
    HMG = 'HMG'
    Ribonucleoprotein = 'Ribonucleoprotein'
    RibosomalProtein = 'Ribosomal Protein'
    SignalRecognitionParticle = 'Signal Recognition Particle'
    TelomereBinding = 'Telomere Binding'
    ViralCoat = 'Viral Coat'


class OtherFunction(Enum):
    """Enum for other functions in query

    :cvar Empty: empty value in query
    :cvar All: all functions in query
    :cvar Antibiotic: antibiotic function in query
    :cvar Antibody: antibody function in query
    :cvar Other: other function in query
    """
    Empty = ''
    All = 'OTHER'
    Antibiotic = 'Antibiotic'
    Antibody = 'Antibody'
    Other = 'Other'


class NaFeature(Enum):
    """Enum for nucleic acid feature in query

    :cvar Empty: empty value in query
    :cvar All: all features in query
    :cvar HairpinLoop: hairpin loop in query
    :cvar InternalLoop: internal loop in query
    :cvar Bulge: bulge in query
    :cvar Hammerhead: hammerhead in query
    :cvar ThreeWayJunction: three way junction in query
    :cvar FourWayJunction: four way (holliday) junction in query
    :cvar NonWatsonCrickBaseParing: non watson crick base paring in query
    :cvar MismatchBaseParing: mismatch base paring in query
    """
    Empty = ''
    All = 'loop'
    HairpinLoop = 'hairpin loop'
    InternalLoop = 'internal loop'
    Bulge = 'bulge'
    Hammerhead = 'hammerhead'
    ThreeWayJunction = 'three_way_junction'
    FourWayJunction = 'holliday_junction'
    NonWatsonCrickBaseParing = 'type_11_pair'
    MismatchBaseParing = 'mismat'


class StrandDescription(Enum):
    """Enum for strand description in query

    :cvar Empty: empty value in query
    :cvar DoubleHelix: double helix in query
    :cvar TripleHelix: triple helix in query
    :cvar QuadrupleHelix: quadruple helix in query
    """
    Empty = ''
    DoubleHelix = 'double helix'
    TripleHelix = 'triple helix'
    QuadrupleHelix = 'quadruple helix'


class ConformationType(Enum):
    """Enum for conformation type in query

    :cvar Empty: empty value in query
    :cvar All: all conformations in query
    :cvar A: A conformation in query
    :cvar B: B conformation in query
    :cvar RH: RH conformation in query
    :cvar T: T conformation in query
    :cvar U: U conformation in query
    :cvar Z: Z conformation in query
    """
    Empty = ''
    All = 'all'
    A = 'A'
    B = 'B'
    RH = 'RH'
    T = 'T'
    U = 'U'
    Z = 'Z'

