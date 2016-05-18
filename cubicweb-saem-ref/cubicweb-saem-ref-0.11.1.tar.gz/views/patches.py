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
"""cubicweb-saem-ref monkeypatch of not-yet-integrated patches"""

from logilab.common.decorators import monkeypatch


# https://www.cubicweb.org/ticket/5352619 ##########################################################
# other part in site_cubicweb.py

from cubicweb import neg_role  # noqa
from cubicweb.web import ProcessFormError  # noqa
from cubicweb.web.views import editcontroller  # noqa

orig_insert_entity = editcontroller.EditController._insert_entity


@monkeypatch(editcontroller.EditController)
def _insert_entity(self, etype, eid, rqlquery):
    if getattr(rqlquery, 'canceled', False):
        return
    return orig_insert_entity(self, etype, eid, rqlquery)


orig_update_entity = editcontroller.EditController._update_entity


@monkeypatch(editcontroller.EditController)
def _update_entity(self, eid, rqlquery):
    if getattr(rqlquery, 'canceled', False):
        return
    return orig_update_entity(self, eid, rqlquery)


@monkeypatch(editcontroller.EditController)
def handle_formfield(self, form, field, rqlquery=None):
    eschema = form.edited_entity.e_schema
    try:
        for field, value in field.process_posted(form):
            if not ((field.role == 'subject' and field.name in eschema.subjrels) or
                    (field.role == 'object' and field.name in eschema.objrels)):
                continue
            rschema = self._cw.vreg.schema.rschema(field.name)
            if rschema.final:
                rqlquery.set_attribute(field.name, value)
            else:
                if form.edited_entity.has_eid():
                    origvalues = set(e.eid for e in form.edited_entity.related(field.name,
                                                                               field.role,
                                                                               entities=True))
                else:
                    origvalues = set()
                if value is None or value == origvalues:
                    continue  # not edited / not modified / to do later
                rdef = eschema.rdef(rschema, field.role)
                if not value and rdef.composite == neg_role(field.role):
                    # deleted composite relation, delete the subject entity
                    self.handle_composite_deletion(form, field, rqlquery)
                if rschema.inlined and rqlquery is not None and field.role == 'subject':
                    self.handle_inlined_relation(form, field, value, origvalues, rqlquery)
                elif form.edited_entity.has_eid():
                    self.handle_relation(form, field, value, origvalues)
                else:
                    form._cw.data['pending_others'].add((form, field))
    except ProcessFormError as exc:
        self.errors.append((field, exc))


@monkeypatch(editcontroller.EditController)
def handle_composite_deletion(self, form, field, rqlquery):
    """handle deletion of the entity when relation to its parent is removed
    """
    rql = 'DELETE %s X WHERE X eid %%(x)s' % form.edited_entity.cw_etype
    self.relations_rql.append((rql, {'x': form.edited_entity.eid}))
    rqlquery.canceled = True


# https://www.cubicweb.org/ticket/12512052 #########################################################
# this is not probably the right fix, see also https://www.cubicweb.org/ticket/12512176

from cubicweb.web import NoSelectableObject  # noqa
from cubicweb.web.views import ajaxcontroller  # noqa


@ajaxcontroller.ajaxfunc(output_type='xhtml')
def render(self, registry, oid, eid=None, selectargs=None, renderargs=None):
    if eid is not None:
        rset = self._cw.eid_rset(eid)
        # XXX set row=0
    elif self._cw.form.get('rql'):
        rset = self._cw.execute(self._cw.form['rql'])
    else:
        rset = None
    try:
        viewobj = self._cw.vreg[registry].select(oid, self._cw, rset=rset,
                                                 **ajaxcontroller.optional_kwargs(selectargs))
    except NoSelectableObject:
        return u''
    return self._call_view(viewobj, **ajaxcontroller.optional_kwargs(renderargs))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (render,))
    vreg.register_and_replace(render, ajaxcontroller.render)
