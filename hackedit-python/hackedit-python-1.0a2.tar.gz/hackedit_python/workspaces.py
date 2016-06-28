class PythonWorkspace:
    @staticmethod
    def get_data():
        data = {
          'name': 'Python',
          'description': 'Default pure python workspace.',
          'plugins': [
            'FindReplace',
            'DocumentOutline',
            'OpenDocuments',
            'Terminal',
            'HtmlPreview',
            'PyRefactor',
            'PyRun',
            'PyContextMenus',
            'PyOpenModule',
            'PyCodeEditorIntegration',
            'CleanPycFiles',
            'PyConsole'
            ]
        }
        return data
