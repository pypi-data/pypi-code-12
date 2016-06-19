from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class MagnitudeBar(_Component):

    _component_type_str = 'MAGNITUDE_BAR'

    def __init__(self, analysis=None, component_id=None, component_type=None):
        super(MagnitudeBar, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)


    def _fields(self):
        return super(MagnitudeBar, self)._fields() + [  ]

