"""
This module contains the 2 COBOL workspace:

    - project mode: with project support (you need to define which files are
      part of the project and how to compiler them)
    - single file mode: very similar to OpenCOBOLIDE's workspace: compile/run
      current editor.
"""


class CobolProjectWorkspace:
    @staticmethod
    def get_data():
        return {
            'name': 'COBOL (Project mode)',
            'description': 'COBOL workspace with project support',
            'plugins': [
                'FindReplace',
                'DocumentOutline',
                'OpenDocuments',
                'Terminal',
                'CobProjectManager',
                'CobOffsetCalculator',
                'CobFileIndicators'
            ]
        }


class CobolFileWorkspace:
    @staticmethod
    def get_data():
        return {
            'name': 'COBOL (File mode)',
            'description': 'Simple COBOL workspace (very similar to '
                           'OpenCobolIDE)',
            'plugins': [
                'FindReplace',
                'DocumentOutline',
                'OpenDocuments',
                'Terminal',
                'CobOffsetCalculator',
                'CobFileManager',
                'CobFileIndicators'
            ]
        }
