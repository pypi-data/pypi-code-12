# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""

import model
import app.resources as rc
import tran


class Schema(model.TComponent):
    """Implements c++ class representation"""
    folder_container = True
    diagram_container = True
    table_container = True

    # visual methods
    @tran.TransactionalMethod('move schema {}')
    def drop(self, to):
        """Drops schema inside project or another folder """
        return False
        target = to.inner_schema_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._memberPrefix = kwargs.get('prefix', '')
        super(Schema, self).__init__(**kwargs)

    def CreateTables(self, conn):
        """Create tables for the schema from database"""
        try:
            conn.query('SHOW TABLES FROM `{}`'.format(self.name))
            data = conn.store_result()
            if data:
                kwargs = {'parent': self}
                for i in range(0, data.num_rows()):
                    kwargs['name'] = data.fetch_row()[0][0]
                    model.database.Table(**kwargs)
                del data
                for table in self[model.database.Table]:
                    table.CreateFields(conn)
            return True
        except:
            return False

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['prefix'] = self._memberPrefix
        kwargs.update(super(Schema, self).get_kwargs())
        return kwargs

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        super(Schema, self).OnUndoRedoRemoving()

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(Schema, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        for dia in self.project(model.ClassDiagram):
            # Check if inherit is in
            elem = dia.FindElement(self)
            if elem is not None:
                dia.SaveState()
                dia.RemoveElement(elem)
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Schema, self).Delete()

    def OnUndoRedoChanged(self):
        """Update from app"""
        project = self.project
        #update class diagrams
        dias = project(model.ClassDiagram)
        for dia in dias:
            # Check if class is in
            elem = dia.FindElement(self)
            if elem is not None:
                elem.Layout()
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Schema, self).OnUndoRedoChanged()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('database_schema')

    @property
    def tree_label(self):
        """Get tree label"""
        return self.name

    @property
    def inner_schema(self):
        """Get the inner schema"""
        return self

    @property
    def outer_schema(self):
        """Get the outer class container"""
        return self



