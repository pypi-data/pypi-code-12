from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class VariableLink(_Component):

    _component_type_str = 'VARIABLE_LINK'

    def __init__(self, datasource_id=None, variable_name=None, analysis=None, component_id=None, component_type=None):
        super(VariableLink, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if datasource_id is not None:
            self._datasource_id = datasource_id

        if variable_name is not None:
            self._variable_name = variable_name


    @property
    def datasource_id(self):
        return self._datasource_id

    @datasource_id.setter
    def datasource_id(self, val):
        self._datasource_id = val
        self._update()

        
    @property
    def variable_name(self):
        return self._variable_name

    @variable_name.setter
    def variable_name(self, val):
        self._variable_name = val
        self._update()

        

    def _fields(self):
        return super(VariableLink, self)._fields() + [ 'datasource_id', 'variable_name' ]

