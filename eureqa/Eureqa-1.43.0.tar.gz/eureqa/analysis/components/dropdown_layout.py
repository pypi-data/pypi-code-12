from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class DropdownLayout(_Component):

    _component_type_str = 'DROPDOWN_LAYOUT'

    def __init__(self, label=None, padding=None, components=None, analysis=None, component_id=None, component_type=None):
        super(DropdownLayout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if label is not None:
            self._label = label

        if padding is not None:
            self._padding = padding

        if components is not None:
            self._components = components


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, val):
        self._label = val
        self._update()

        
    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, val):
        self._padding = val
        self._update()

        
    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, val):
        self._components = val
        self._update()

        

    def _fields(self):
        return super(DropdownLayout, self)._fields() + [ 'label', 'padding', 'components' ]

