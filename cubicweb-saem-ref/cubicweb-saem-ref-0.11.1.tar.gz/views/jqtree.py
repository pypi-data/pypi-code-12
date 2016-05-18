# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref tree views using jqTree"""

from functools import wraps

from cubicweb import tags, uilib
from cubicweb.view import EntityView, View
from cubicweb.predicates import adaptable, match_form_params
from cubicweb.web.views import json


def json_entity(entity, on_demand=False):
    """Return the minimal JSON dict of an entity."""
    label = entity.view('jqtree.label')
    data = {'label': label,
            'id': entity.eid}
    if on_demand:
        data['load_on_demand'] = True
    return data


def itree_adaptable(func):
    """Decorator for a function taking an entity as argument, checking that
    the entity is adaptable as ITree and eventually calling it or not.
    """
    @wraps(func)
    def wrapper(entity):
        itree = entity.cw_adapt_to('ITree')
        if itree:
            return func(entity)
        return ()
    return wrapper


@itree_adaptable
def json_entity_children(entity):
    """Yield JSON data for children of a ITree adapted entity.

    Each data will have `load_on_demand` unless it is a leaf of the tree.
    """
    for child in entity.cw_adapt_to('ITree').iterchildren():
        ctree = child.cw_adapt_to('ITree')
        on_demand = ctree and not ctree.is_leaf()
        yield json_entity(child, on_demand=on_demand)


@itree_adaptable
def json_entity_parents(entity):
    """Return the JSON data of the full tree walked upstream from `entity`.

    Each node along the path from this entity to the root will have
    `load_on_demand == False` so that the tree is opened down to `entity`.
    """
    # initialize data for "previous" parent when walking up the tree.
    previous, previous_children = None, []
    data = None
    for parent in entity.cw_adapt_to('ITree').iterparents():
        # parent has to be strictly evaluated
        data = json_entity(parent, on_demand=False)
        data['children'] = []
        # fetch JSON for children of this parent, setting the previous
        # parent we're coming from as strict (load_on_demand=False).
        for child in json_entity_children(parent):
            if previous_children and child['id'] == previous:
                # remove load_on_demand as this is the branch we are
                # walking on.
                child.pop('load_on_demand', None)
                # add children of previous parent (which is a child of
                # this parent).
                child.setdefault('children', []).extend(previous_children)
            data['children'].append(child)
        # store this parent as the previous one for next iteration.
        previous, previous_children = parent.eid, data.get('children', [])
    return data


class JsonTreeView(json.JsonMixIn, EntityView):
    """JSON view for an entity adaptable as a ITree."""

    __regid__ = 'jqtree.json'
    __select__ = adaptable('ITree') & ~match_form_params('node')

    def entity_call(self, entity, **kwargs):
        # compute the parent JSON tree.
        data = json_entity_parents(entity)
        if not data:
            # if empty, just return the current entity JSON tree (with
            # children) as the entity is probably the root.
            data = json_entity(entity, on_demand=False)
            children = list(json_entity_children(entity))
            if children:
                data['children'] = children
        data['selected'] = entity.eid
        self.wdata([data])


class JsonTreeNodeView(json.JsonMixIn, View):
    """JSON view for a node of tree, returning the children of that node for
    lazy loading.
    """

    __regid__ = 'jqtree.json'
    __select__ = match_form_params('node')

    def call(self):
        eid = self._cw.form.pop('node')
        entity = self._cw.entity_from_eid(eid)
        children = list(json_entity_children(entity))
        self.wdata(children)


class JQTreeItemLabelView(EntityView):
    """View for the "label" of a node of a jqTree.

    Default to "oneline" view.
    """
    __regid__ = 'jqtree.label'

    def entity_call(self, entity):
        entity.view('oneline', w=self.w)


class JQTreeView(EntityView):
    """Tree view using jqTree library."""
    __regid__ = 'jqtree.treeview'
    __select__ = adaptable('ITree')

    def entity_call(self, entity, **kwargs):
        # TODO move jqTree js to its own file.
        self._cw.add_js(('cubes.saem_ref.js', 'tree.jquery.js'))
        self._cw.add_css(('jqtree.css'))
        divid = 'jqtree' + str(entity.eid)
        data_url = entity.absolute_url(vid='jqtree.json')
        self.w(tags.div(id=divid, **{'data-url': data_url}))
        self._cw.add_onload(uilib.js.saem.sedaTree(divid))
