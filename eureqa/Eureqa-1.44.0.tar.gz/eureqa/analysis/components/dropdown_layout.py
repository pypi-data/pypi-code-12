from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class DropdownLayout(_Component):

    _component_type_str = 'DROPDOWN_LAYOUT'

    def __init__(self, label=None, padding=None, analysis=None, component_id=None, component_type=None):
        if label is not None:
            self._label = label

        if padding is not None:
            self._padding = padding

        # A place to put Components that don't have IDs yet,
        # until we're '_associate()'d with an Analysis so can go get IDs for them.
        self._queued_components = []

        super(DropdownLayout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)


    @property
    def label(self):
        """Text label for the Dropdown box

        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, val):
        self._label = val
        self._update()


    @property
    def padding(self):
        """Padding (spacing) for this Dropdown

        :rtype: int
        """
        return self._padding

    @padding.setter
    def padding(self, val):
        self._padding = val
        self._update()


    class _TitledComponent(object):
        """Internal class: Representation of one element in the dropdown

        :param str title: Title of the Component in the dropdown list
        :param eureqa.analysis.components._Component component: The Component

        :cvar title: Title of the Component in the dropdown list
        :cvar eureqa.analysis.components._Component component: The Component
        """
        def __init__(self, title, component):
            self.title = title
            self.component = component

        def _to_json(self):
            return { "value": self.title,
                     "component_id": self.component._component_id }

    @property
    def components(self):
        """Internal: Set of components represented in the dropdown

        :return: list() of `~eureqa.analysis.components._Component`
        """
        return [_Component._get(analysis=self._analysis,
                                component_id=x["component_id"]) for x in self._components]

    def _ensure_components_list(self):
        if not hasattr(self, "_components"):
            self._components = []

    def add_component(self, title, content):
        """
        Add a Component to the DropdownLayout
        :param title: Title of the Component in the dropdown list
        :param content: The Component
        """
        # If we don't have an Analysis yet, queue this Component to be saved later
        if not hasattr(self, "_analysis"):
            self._queued_components.append(DropdownLayout._TitledComponent(title, content))
            return

        self._ensure_components_list()
        self._components.append(DropdownLayout._TitledComponent(title, content)._to_json())

    def _associate(self, analysis):
        for c in self._queued_components:
            c.component._associate(analysis)

            self._ensure_components_list()
            self._components.append(c._to_json())

        self._queued_components = []

        super(DropdownLayout, self)._associate(analysis)

    def _fields(self):
        return super(DropdownLayout, self)._fields() + [ 'label', 'padding', 'components' ]
