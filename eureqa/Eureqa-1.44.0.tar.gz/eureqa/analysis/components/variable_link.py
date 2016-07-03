from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class VariableLink(_Component):

    _component_type_str = 'VARIABLE_LINK'

    def __init__(self, datasource=None, variable_name=None, analysis=None, component_id=None, component_type=None):
        """
        Create a VariableLink component

        Common/expected usage is as follows:

        >>> vl = VariableLink(datasource=self._data_source, variable_name=self._variables[0])
        >>> analysis.create_html_card("Target variable is: {0}".format(analysis.html_ref(vl)))

        :param ~eureqa.DataSource datasource: datasource from which to find the variable
        :param str variable_name: name of the variable
        :param ~eureqa.analysis.Analysis analysis: (optional) Analysis to associate this Layout with
        :param str component_id: Internal, do not use
        :param str component_type: Internal, do not use
        """

        # implementation details:
        # self.datasource is a property, property
        # self._datasource is the actual datasource object (cache of the datasource) which may or may not be fetched
        # self._datasource_id a string, and its setting/handling is handled by the JsonRest implementation'

        if datasource is not None:
            self.datasource = datasource

        if variable_name is not None:
            self._variable_name = variable_name

        super(VariableLink, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :rtype: eureqa.DataSource
        """
        # Note that the _datasource field is set by the underlying _Component
        # based on the _datasource_id string
        return getattr(self, "_datasource", None)

    @datasource.setter
    def datasource(self, val):
        self._datasource = val
        self._datasource_id = val._data_source_id
        self._update()


    @property
    def variable_name(self):
        """The name of the variable from this datasource to link to

        :rtype: str
        """
        return self._variable_name

    @variable_name.setter
    def variable_name(self, val):
        self._variable_name = val
        self._update()

    def _fields(self):
        return super(VariableLink, self)._fields() + [ 'datasource_id', 'variable_name' ]
