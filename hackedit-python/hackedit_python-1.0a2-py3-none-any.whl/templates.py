"""
This module contains the COBOL templates provider plugin.
"""
import os
from hackedit import api


class PyTemplatesProvider(api.plugins.TemplateProviderPlugin):
    @staticmethod
    def get_label():
        return 'Python'

    @staticmethod
    def get_url():
        import hackedit_python
        path = os.path.join(os.path.dirname(hackedit_python.__file__), 'templates')
        return path
