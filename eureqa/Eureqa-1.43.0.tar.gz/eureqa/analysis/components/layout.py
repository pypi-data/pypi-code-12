from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST


class Layout(_Component):

    class GridItem(object):
        def __init__(self, component=None, grid_unit=None, analysis=None):
            self.grid_unit = grid_unit
            self.component = component
            self._analysis = analysis

        def _to_json(self):
            return {
                "grid_unit": self.grid_unit,
                "component": self.component._component_id
            }

        def _from_json(self, body):
            if "grid_unit" in body:
                self.grid_unit = body["grid_unit"]
            if "component" in body:
                self.component = _Component(analysis=self._analysis, component_id=body["component"])._get_self()

        def _associate(self, analysis):
            self.component._associate(analysis)

    class Row(object):
        def __init__(self, analysis=None, grid_items=None, ):
            self.grid_items = grid_items if grid_items else []
            self._analysis = analysis

        def create_card(self, component, grid_unit="1"):
            self.grid_items.append(Layout.GridItem(component, grid_unit, self._analysis))
            return self.grid_items[-1]

        def _to_json(self):
            return [item._to_json() for item in self.grid_items]

        def _from_json(self, val):
            self.grid_items = []
            for item_json in val:
                item = Layout.GridItem(analysis=self._analysis)
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
        >>> layout.create_card(Centipede(...),   "1/4")    # Add a Centipede Component on the top left
        >>> layout.create_card(HtmlBlock(...),   "1/2")    # Add an HtmlBlock on the top center
        >>> layout.create_card(ScatterPlot(...), "1/4")    # Add a ScatterPlot on the top right
        >>> layout.add_row()                             # Add an additional row.  Start putting grid items into the new row.
        >>> layout.create_card(Table(...))                 # Add a Table to the row.  Takes up the whole row by default.
        >>> analysis.create_card(layout)                 # Add this Layout to an Analysis

        :param ~eureqa.analysis.Analysis analysis: (optional) Analysis to associate this Layout with
        :param list rows: (optional) List of :class:`~eureqa.analysis.components.Layout.Row` objects to add to this class initially
        """
        if rows is not None:
            self.rows = rows
        else:
            self.rows = []

        super(Layout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def current_row(self):
        # Break with convention:
        # 'self.rows' is not a property that points to 'self._rows
        if len(self.rows) == 0:
            self.rows = [ Layout.Row(analysis=getattr(self, "_analysis", None)) ]

        return self.rows[-1]

    def add_row(self):
        self.rows.append(Layout.Row(analysis=getattr(self, "_analysis", None)))
        return self.rows[-1]

    def create_card(self, component, grid_unit="1"):
        return self.current_row.create_card(component, grid_unit)

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
            row = Layout.Row(analysis=getattr(self, "_analysis", None))
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
