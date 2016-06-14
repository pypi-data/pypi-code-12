# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""

@author: mel
"""
import model


class Note(model.TComponent):
    """Implements class representation"""
    def __init__(self, **kwargs):
        """Initialization method"""
        kwargs['visibleInTree'] = False
        super(Note, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(Note, self).get_kwargs())
        return kwargs

    def Delete(self):
        """Delete diagram objects"""
        #process diagrams
        dias = self.project(model.ClassDiagram)
        for dia in dias:
            # Check if inherit is in
            elem = dia.FindElement(self)
            if elem is not None:
                dia.SaveState()
                dia.RemoveElement(elem)
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Note, self).Delete()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #update class diagrams
        project = self.project
        if project is not None:
            dias = project(model.ClassDiagram)
            for dia in dias:
                # Check if class is in
                elem = dia.FindElement(self)
                if elem is not None:
                    elem.Layout()
                    if hasattr(dia, '_pane') and dia._pane is not None:
                        dia._pane.Refresh(False)
        super(Note, self).OnUndoRedoChanged()
