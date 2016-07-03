from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST
import warnings

class TitledLayout(_Component):

    _component_type_str = 'TITLED_LAYOUT'

    def __init__(self, title=None, description=None, content=None, analysis=None, component_id=None, component_type=None):
        super(TitledLayout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

        if title is not None:
            self._title = title

        if description is not None:
            self._description = description

        if content is not None:
            self.create_card(content)


    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str"""
        return self._title

    @title.setter
    def title(self, val):
        self._title = val
        self._update()

        
    @property
    def description(self):
        """ The description of this card.

        :return: description of this card
        :rtype: str"""
        return self._description

    @description.setter
    def description(self, val):
        self._description = val
        self._update()

        
    @property
    def content(self):
        """The Component that this TitledLayout is adding a title to.
        This field can't be assigned to; use 'create_card()' to
        assign a Component to this TitledLayout.

        :rtype: ~eureqa.analysis.components._Component"""
        if not hasattr(self, "_content_component"):
            self._content_component = _Component._get(analysis=self._analysis, component_id=self._content_component_id)
        return self._content_component

    def create_card(self, component):
        """
        Assign a Component to this TitledLayout

        :param component: Component to assign
        """
        # Add the new component to the analysis if we can
        if hasattr(self, "_analysis"):
            component._associate(self._analysis)

        # Set all local fields that we're able to set at this time
        self._content_component = component
        if hasattr(self, "_content_component_id"):
            del self._content_component_id
        if hasattr(component, "_component_id"):
            self._content_component_id = component._component_id

        # Save any updates to ourself
        self._update()

    def delete(self):
        if hasattr(self, "_content_component"):
            self._content_component.delete()
        super(TitledLayout, self).delete()

    def clone(self):
        clone = super(TitledLayout, self).clone()
        clone.add_component(self.content.clone())
        return clone

    def _associate(self, analysis):
        if hasattr(self, "_content_component") and not hasattr(self._content_component, "_component_id"):
            self._content_component._associate(analysis)
            self.create_card(self._content_component)
        super(TitledLayout, self)._associate(analysis)
    
    def _fields(self):
        return super(TitledLayout, self)._fields() + [ 'title', 'description', 'content_component_id' ]

