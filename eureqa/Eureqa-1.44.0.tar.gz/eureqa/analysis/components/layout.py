from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST


class Layout(_Component):

    class _GridItem(object):
        """ Internal implementation class """
        def __init__(self, component=None, grid_unit="1", analysis=None):
            self.grid_unit = grid_unit
            self.component = component
            if component is not None and hasattr(component, "_component_id"):
                self._component_id = component._component_id
            self._analysis = analysis

        def _to_json(self):
            return {
                "grid_unit": self.grid_unit,
                "component_id": self.component._component_id
            }

        def _from_json(self, body):
            if "grid_unit" in body:
                self.grid_unit = body["grid_unit"]
            if "component_id" in body:
                self._component_id = body["component_id"]
                if self._analysis is not None:
                    self.component = _Component(analysis=self._analysis, component_id=body["component_id"])._get_self()

        def _associate(self, analysis):
            if self.component is None:
                self.component = _Component(analysis=analysis, component_id=getattr(self, "_component_id", None))._get_self()
            self.component._associate(analysis)

    class _Row(object):
        """ Internal implementation class """
        def __init__(self, analysis=None, grid_items=None, ):
            self.grid_items = grid_items if grid_items else []
            self._analysis = analysis

        def create_card(self, component, grid_unit="1"):
            self.grid_items.append(Layout._GridItem(component, grid_unit, self._analysis))
            return self.grid_items[-1]

        def _to_json(self):
            return [item._to_json() for item in self.grid_items]

        def _from_json(self, val):
            self.grid_items = []
            for item_json in val:
                item = Layout._GridItem(analysis=self._analysis)
                item._from_json(item_json)
                self.grid_items.append(item)

        def _associate(self, analysis):
            for item in self.grid_items:
                item._associate(analysis)

    _component_type_str = 'GENERIC_LAYOUT'

    def __init__(self, rows=None, analysis=None, component_id=None, component_type=None):
        """
        Generic layout within an Analysis

        Describes a compartmentalized layout.
        Layout is split into rows.
        Each row contains one or more items; each item has a customizable width as a fraction of the width of the row.

        Common/expected usage is as follows:

        >>> layout = Layout()
        >>> layout.add_component(Centipede(...),   "1/4")    # Add a Centipede Component on the top left
        >>> layout.add_component(HtmlBlock(...),   "1/2")    # Add an HtmlBlock on the top center
        >>> layout.add_component(ScatterPlot(...), "1/4")    # Add a ScatterPlot on the top right
        >>> layout.add_row()                                 # Add an additional row.  Start putting grid items into the new row.
        >>> layout.add_component(Table(...))                 # Add a Table to the row.  Takes up the whole row by default.
        >>> analysis.add_component(layout)                   # Add this Layout to an Analysis

        :param ~eureqa.analysis.Analysis analysis: (optional) Analysis to associate this Layout with
        :param list rows: (optional) List of :class:`~eureqa.analysis.components.Layout.Row` objects to add to this class initially
        """
        if rows is not None:
            self.rows = rows
        else:
            self.rows = []

        super(Layout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def _current_row(self):
        # Break with convention:
        # 'self.rows' is not a property that points to 'self._rows
        if len(self.rows) == 0:
            self.rows = [ Layout._Row(analysis=getattr(self, "_analysis", None)) ]

        return self.rows[-1]

    def add_row(self):
        self.rows.append(Layout._Row(analysis=getattr(self, "_analysis", None)))
        return self.rows[-1]

    def add_component(self, component, grid_unit="1"):
        return self._current_row.create_card(component, grid_unit)

    def delete(self):
        for row in self.rows:
            for item in row.grid_items:
                item.component.delete()
        super(Layout, self).delete()

    def _to_json(self):
        ret = super(Layout, self)._to_json()
        ret["rows"] = [row._to_json() for row in self.rows]
        return ret

    def _from_json(self, body):
        super(Layout, self)._from_json(body)
        self.rows = []
        for row_json in body.get("rows", []):
            row = Layout._Row(analysis=getattr(self, "_analysis", None))
            row._from_json(row_json)
            self.rows.append(row)

    def _associate(self, analysis):
        super(Layout, self)._associate(analysis)
        for row in self.rows:
            row._associate(analysis)

    def _fields(self):
        # We only have one additional field, 'rows',
        # and we manage that field ourselves.
        return super(Layout, self)._fields()

    def _associate(self, analysis):
        for row in self.rows:
            row._associate(analysis)
        super(Layout, self)._associate(analysis)
