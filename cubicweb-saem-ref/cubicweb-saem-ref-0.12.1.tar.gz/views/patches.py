# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
