import uuid
import string
from base import _Component

def _gen_component_reference_str(component_id):
    return '<nutonian-component id="{0}" />'.format(component_id)

class _ComponentFormatter(string.Formatter):
    def __init__(self, set_component_id_func):
        self._component_definitions = []
        self._set_component_id = set_component_id_func

    def format_field(self, value, format_spec):
        if not isinstance(value, _Component):
            raise TypeError("Argument to format must be a Component")

        # keep track of all the components we have been asked to format
        comp_obj = value
        self._set_component_id(comp_obj)
        self._component_definitions.append(comp_obj._to_json())

        # replace the value to be formatted to a component reference and call parent class implementation
        new_value = _gen_component_reference_str(comp_obj._component_id)
        return super(_ComponentFormatter, self).format_field(new_value, format_spec)

def _set_component_id_via_uuid(comp_obj):
    comp_id = uuid.uuid4()
    comp_obj._component_id = str(comp_id)

class _SetComponentIDViaAnalysis(object):
    def __init__(self, analysis):
        self._analysis = analysis

    def __call__(self, comp_obj):
        self._analysis._associate(comp_obj)

class FormattedText(object):
    """ Return a formatted version of format_str, substituing format specifications with component references.
    """

    def __init__(self, format_str, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        # Do format in the c'tor so the format string is checked at construction time
        fmt = _ComponentFormatter(_set_component_id_via_uuid)
        self._component_references  = fmt.format(format_str, *args, **kwargs)
        self._component_definitions = fmt._component_definitions

    def _get_component_ref_and_defs(self, analysis = None):
        if analysis:  # only need to re-format if analysis is provided
            set_component_id_via_analysis = _SetComponentIDViaAnalysis(analysis)
            fmt = _ComponentFormatter(set_component_id_via_analysis)
            self._component_references  = fmt.format(format_str, *args, **kwargs)
            self._component_definitions = fmt._component_definitions

        return self._component_references, self._component_definitions

def _get_component_ref_and_defs_for_value(rendered_value, analysis = None):
    if isinstance(rendered_value, _Component):
        comp = rendered_value
        if analysis:
            comp._associate(analysis)
        else:
            comp._component_id = str(uuid.uuid4())
        return _gen_component_reference_str(comp._component_id), [comp._to_json()]
    elif isinstance(rendered_value, FormattedText):
        return rendered_value._get_component_ref_and_defs(analysis = analysis)
    else:
        return rendered_value, []
