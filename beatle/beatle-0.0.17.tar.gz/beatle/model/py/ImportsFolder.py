# -*- coding: utf-8 -*-

import model
import app.resources as rc


class ImportsFolder(model.Folder):
    """Implements a Folder representation"""
    class_container = False
    type_container = False
    function_container = False
    variable_container = False
    module_container = False
    namespace_container = False
    function_container = False
    member_container = False
    import_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs['name'] = 'imports'
        super(ImportsFolder, self).__init__(**kwargs)
        self.update_container()

    def update_container(self):
        """Update the container info"""
        self.context_container = False
        self.folder_container = False
        self.diagram_container = False
        self.namespace_container = False

    def ExportPythonCode(self, wf):
        """Write code"""
        from Import import Import
        for x in self[Import]:
            x.ExportPythonCode(wf)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folderI")
