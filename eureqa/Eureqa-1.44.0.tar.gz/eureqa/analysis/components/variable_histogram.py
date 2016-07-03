from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class VariableHistogram(_Component):

    _component_type_str = 'VARIABLE_HISTOGRAM'

    def __init__(self, datasource_id=None, search_id=None, analysis=None, component_id=None, component_type=None):
        super(VariableHistogram, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if datasource_id is not None:
            self._datasource_id = datasource_id

        if search_id is not None:
            self._search_id = search_id


    @property
    def datasource_id(self):
        return self._datasource_id

    @datasource_id.setter
    def datasource_id(self, val):
        self._datasource_id = val
        self._update()

        
    @property
    def search_id(self):
        return self._search_id

    @search_id.setter
    def search_id(self, val):
        self._search_id = val
        self._update()

        

    def _fields(self):
        return super(VariableHistogram, self)._fields() + [ 'datasource_id', 'search_id' ]

