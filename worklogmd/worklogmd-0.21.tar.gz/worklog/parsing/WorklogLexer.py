# Generated from Worklog.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\16")
        buf.write("i\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3\2")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\4\3\4\3")
        buf.write("\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6")
        buf.write("\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3")
        buf.write("\7\3\7\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t")
        buf.write("\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\13\6\13\\\n\13\r\13")
        buf.write("\16\13]\3\f\6\fa\n\f\r\f\16\fb\3\r\6\rf\n\r\r\r\16\rg")
        buf.write("\2\2\16\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f")
        buf.write("\27\r\31\16\3\2\5\4\2\f\f\17\17\3\2\62;\5\2\13\f\17\17")
        buf.write("\"\"k\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2")
        buf.write("\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2")
        buf.write("\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\3\33")
        buf.write("\3\2\2\2\5#\3\2\2\2\7\'\3\2\2\2\t)\3\2\2\2\13\64\3\2\2")
        buf.write("\2\r=\3\2\2\2\17F\3\2\2\2\21M\3\2\2\2\23W\3\2\2\2\25[")
        buf.write("\3\2\2\2\27`\3\2\2\2\31e\3\2\2\2\33\34\7%\2\2\34\35\7")
        buf.write("\"\2\2\35\36\7Y\2\2\36\37\7g\2\2\37 \7g\2\2 !\7m\2\2!")
        buf.write("\"\7\"\2\2\"\4\3\2\2\2#$\7%\2\2$%\7%\2\2%&\7\"\2\2&\6")
        buf.write("\3\2\2\2\'(\7\"\2\2(\b\3\2\2\2)*\7/\2\2*+\7\"\2\2+,\7")
        buf.write("U\2\2,-\7v\2\2-.\7c\2\2./\7t\2\2/\60\7v\2\2\60\61\7\"")
        buf.write("\2\2\61\62\7B\2\2\62\63\7\"\2\2\63\n\3\2\2\2\64\65\7/")
        buf.write("\2\2\65\66\7\"\2\2\66\67\7G\2\2\678\7z\2\289\7v\2\29:")
        buf.write("\7t\2\2:;\7c\2\2;<\7\"\2\2<\f\3\2\2\2=>\7/\2\2>?\7\"\2")
        buf.write("\2?@\7N\2\2@A\7w\2\2AB\7p\2\2BC\7e\2\2CD\7j\2\2DE\7\"")
        buf.write("\2\2E\16\3\2\2\2FG\7\"\2\2GH\7*\2\2HI\7d\2\2IJ\7k\2\2")
        buf.write("JK\7|\2\2KL\7+\2\2L\20\3\2\2\2MN\7/\2\2NO\7\"\2\2OP\7")
        buf.write("U\2\2PQ\7v\2\2QR\7q\2\2RS\7r\2\2ST\7\"\2\2TU\7B\2\2UV")
        buf.write("\7\"\2\2V\22\3\2\2\2WX\7/\2\2XY\7\"\2\2Y\24\3\2\2\2Z\\")
        buf.write("\t\2\2\2[Z\3\2\2\2\\]\3\2\2\2][\3\2\2\2]^\3\2\2\2^\26")
        buf.write("\3\2\2\2_a\t\3\2\2`_\3\2\2\2ab\3\2\2\2b`\3\2\2\2bc\3\2")
        buf.write("\2\2c\30\3\2\2\2df\n\4\2\2ed\3\2\2\2fg\3\2\2\2ge\3\2\2")
        buf.write("\2gh\3\2\2\2h\32\3\2\2\2\6\2]bg\2")
        return buf.getvalue()


class WorklogLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    NL = 10
    NUM = 11
    STR = 12

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'# Week '", "'## '", "' '", "'- Start @ '", "'- Extra '", "'- Lunch '", 
            "' (biz)'", "'- Stop @ '", "'- '" ]

    symbolicNames = [ "<INVALID>",
            "NL", "NUM", "STR" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", 
                  "T__7", "T__8", "NL", "NUM", "STR" ]

    grammarFileName = "Worklog.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


