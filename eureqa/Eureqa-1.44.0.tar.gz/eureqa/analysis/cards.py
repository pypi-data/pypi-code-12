
from eureqa.utils.jsonrest import _JsonREST
from eureqa.analysis.components.base import _Component

class Card(_JsonREST):
    """
    :var bool collapse:  Whether the Item is currently collapsed or not
    """

    @property
    def collapse(self):
        """ Whether this item should be rendered as "collapsed" (with its content hidden)

        :rtype: bool
        """
        return self._collapse

    @collapse.setter
    def collapse(self, val):
        self._collapse = val
        self._update()

    def __init__(self,
                 analysis=None, item_id=None, component=None,
                 order_index=None, collapse=None):
        """ For internal use only """

        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if component is not None:
            self.component = component

        if item_id is not None:
            self._item_id = item_id
        if order_index is not None:
            self._order_index = order_index
        if collapse is not None:
            self._collapse = collapse

        if analysis is not None and component is not None:
            self._associate(analysis)

    def _associate(self, analysis):
        _JsonREST.__init__(self, analysis._eureqa)
        self._analysis = analysis
        self._analysis_id = analysis._id
        if getattr(self, "_default_component", None):
            self._default_component._associate(analysis)
            self._default_component_id = self._default_component._component_id
        # Create a matching object on the server
        self._create()

    def _fetch_component(self):
        if not getattr(self, "_default_component", None) and getattr(self, "_analysis", None):
            self.component = _Component._get(
                component_id=self._default_component_id,
                analysis=self._analysis)

    @property
    def component(self):
        return self._default_component

    @component.setter
    def component(self, val):
        assert not getattr(val, "_analysis", None) or not getattr(self, "_analysis", None) or val._analysis._id == self._analysis._id, \
            "Can't attach component to analysis '%s'; already attached to analysis '%s'" % (self._analysis._id, val._analysis._id)

        if getattr(self, "_analysis", None):
            val._associate(self._analysis)

        self._default_component = val
        if getattr(val, "_component_id", None):
            self._default_component_id = val._component_id
        self._update()

    # Wrap our contained Component's fields for backwards compatibility.
    #
    # Note that __getattr__ is called only if normal object access fails, but
    # __setattr__ and __delattr__ replace normal object access completely so
    # must invoke it explicitly as a base case.
    # (Python works this way as a common-case performance optimization.)
    def __getattr__(self, name):
        if "_default_component" not in self.__dict__:
            raise AttributeError("Field %s not found" % repr(name))
        component = super(Card, self).__getattribute__("_default_component")
        try:
            return getattr(component, name)
        except AttributeError, e:
            if component._component_type == "TITLED_LAYOUT":
                return getattr(component.content, name)
            raise e

    def __setattr__(self, name, value):
        if "_default_component" in self.__dict__:
            component = self.__dict__["_default_component"]
            if hasattr(component, name):
                return setattr(component, name, value)
            if component._component_type == "TITLED_LAYOUT" and \
                hasattr(component.content, name):
                return setattr(component.content, name, value)
        super(Card, self).__setattr__(name, value)

    def __delattr__(self, name):
        if "_default_component" in self.__dict__:
            component = self.__dict__["_default_component"]
            if name in component.__dict__:
                return delattr(component, name)
            if component._component_type == "TITLED_LAYOUT" and \
                name in component.content.__dict__:
                return delattr(component.content, name)
        super(Card, self).__delattr__(name)

    # List of fields on this object.
    # Typically used by code-autocomplete tools.
    def __dir__(self):
        fields = []
        fields += self.__dict__.keys()
        if hasattr(self, "_default_component"):
            fields += self._default_component.__dict__.keys()
            if hasattr(self._default_component, "_content_component"):
                fields += self._default_component.content.__dict__.keys()

        return sorted(set(self.__dict__.keys()))

    def _object_endpoint(self):
        return '/analysis/%s/items/%s' % (self._analysis._id, self._item_id)
    def _directory_endpoint(self):
        return '/analysis/%s/items' % (self._analysis._id)
    def _fields(self):
        return [ "analysis_id", "item_id", "default_component_id", "order_index", "collapse" ]

    def __repr__(self):
        try:
            component = self.component
        except AttributeError:
            component = getattr(self, "_default_component_id", "??")
        return "Card(component=%s, order_index=%s, collapse=%s, item_id=%s, analysis_id=%s)" % \
               (repr(getattr(self, "component", None)), repr(getattr(self, "_order_index", None)),
                repr(getattr(self, "collapse", None)), repr(getattr(self, "_item_id", None)),
                repr(getattr(self, "_analysis_id", None)))

    def _to_json(self):
        resp = super(Card, self)._to_json()

        if hasattr(self, "_analysis"):
            resp["analysis_id"] = self._analysis._id

        return resp

    def _from_json(self, body):
        if hasattr(self, "_analysis") and body.get("analysis_id"):
            assert body.get("analysis_id") == self._analysis._id, \
                "_from_json() can't de-serialize an Item that belongs to a different Analysis"


        super(Card, self)._from_json(body)

    @classmethod
    def _construct_from_json(cls, body, *args, **kwargs):
        ret = super(Card, cls)._construct_from_json(body, *args, **kwargs)
        ret._fetch_component()
        return ret

    def clone(self):
        # Make a copy of ourselves
        body = self._to_json()

        # Disassociate the copy from the current Analysis
        del body["analysis_id"]
        del body["item_id"]

        # Instantiate a new Item with this state
        new_item = Card._construct_from_json(body)

        # Handle Components
        if hasattr(self, "_default_component"):
            new_item.component = self.component.clone()

        return new_item

    def delete(self):
        if hasattr(self, "_default_component"):
            self._default_component.delete()
        self._delete()

    def move_above(self, other_card):
        """Moves this card above another card.

        :param eureqa.analysis_cards.AnalysisCard other_card: The other card above which to move this card.
        """

        other_card_order = other_card._order_index if hasattr(other_card, '_order_index') else other_card
        if other_card_order >= self._order_index:
            return
        self._order_index = other_card_order
        self._update()

    def move_below(self, other_card):
        """Moves this card below another card.

        :param eureqa.analysis_cards.AnalysisCard other_card: The other card object below which to move this card.
        """

        other_card_order = other_card._order_index if hasattr(other_card, '_order_index') else other_card
        if other_card_order <= self._order_index:
            return
        self._order_index = other_card_order
        self._update()
