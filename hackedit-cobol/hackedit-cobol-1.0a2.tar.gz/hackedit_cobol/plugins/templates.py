"""
This module contains the COBOL templates provider plugin.
"""
import os
from hackedit import api


class CobTemplatesProvider(api.plugins.TemplateProviderPlugin):
    @staticmethod
    def get_label():
        return 'COBOL'

    @staticmethod
    def get_url():
        import hackedit_cobol
        path = os.path.join(os.path.dirname(hackedit_cobol.__file__), 'templates')
        return path
