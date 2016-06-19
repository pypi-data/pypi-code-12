from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST
import warnings

class TitledLayout(_Component):

    _component_type_str = 'TITLED_LAYOUT'

    def __init__(self, title=None, description=None, content=None, analysis=None, component_id=None, component_type=None):
        super(TitledLayout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if title is not None:
            self._title = title

        if description is not None:
            self._description = description

        if content is not None:
            self.content_component = content


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
        """Whether the card is collapsed by default.

        :return: whether the card is collapsed by default
        :rtype: str"""
        if not hasattr(self, "_content_component"):
            self._content_component = _Component._get(analysis=self._analysis, component_id=self._content_component_id)
        return self._content_component

    @content.setter
    def content(self, val):
        self._content_component = val
        if hasattr(val, "_component_id"):
            self._content_component_id = val._component_id
        self._update()

    def delete(self):
        if hasattr(self, "_content_component"):
            self._content_component.delete()
        super(TitledLayout, self).delete()

    def clone(self):
        clone = super(TitledLayout, self).clone()
        clone.content = self.content.clone()
        return clone

    def _fields(self):
        return super(TitledLayout, self)._fields() + [ 'title', 'description', 'content_component_id' ]

