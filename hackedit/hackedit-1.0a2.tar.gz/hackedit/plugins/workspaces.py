"""
This module contains the core builtin workspaces...
"""


class EmptyWorkspace:
    @staticmethod
    def get_data():
        return {
            'name': 'Empty',
            'description': 'Empty workspace',
            'plugins': [
            ]
        }


class GenericWorkspace:
    @staticmethod
    def get_data():
        return {
            'name': 'Generic',
            'description': 'Generic default workspace',
            'plugins': [
                'FindReplace',
                'DocumentOutline',
                'OpenDocuments',
                'Terminal'
            ]
        }
