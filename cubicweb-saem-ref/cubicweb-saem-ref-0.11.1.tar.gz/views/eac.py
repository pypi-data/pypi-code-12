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
"""cubicweb-saem-ref views for agent entities (primary and edition)"""

import os.path

from cubicweb import tags
from cubicweb.view import View
from cubicweb.predicates import is_instance, match_user_groups, one_line_rset
from cubicweb.web import action, formfields as ff, formwidgets as fw, httpcache
from cubicweb.web.views import cwsources, forms, idownloadable

from cubes.skos import to_unicode
from cubicweb.dataimport.importer import HTMLImportLog

from cubes.saem_ref.dataimport import eac
from cubes.saem_ref.views import authority_form_value

_ = unicode


class EACImportMixin(object):
    __regid__ = 'saem_ref.eac-import'
    __select__ = match_user_groups('managers', 'users')


def authority_form_vocabulary(form, field):
    """Field vocabulary function returning the list of available authorities"""
    # filter out authorities without a naa
    rset = form._cw.execute('Any XN, X ORDERBY XN WHERE X is Authority, X ark_naa NA, X name XN')
    return [(name, unicode(eid)) for name, eid in rset]


class EACImportForm(EACImportMixin, forms.FieldsForm):
    """File import form for EAC-CPF"""
    filefield = ff.FileField(name='file', label=_('EAC-CPF file'),
                             required=True)
    authorityfield = ff.StringField(name='authority', required=True,
                                    choices=authority_form_vocabulary, sort=False,
                                    value=authority_form_value)
    form_buttons = [fw.SubmitButton(label=_('do_import'))]

    @property
    def action(self):
        return self._cw.build_url(vid=self.__regid__)


class EACImportView(EACImportMixin, View):
    """EAC-CPF import controller"""

    def call(self):
        self.w(tags.h1(self._cw._('Importing an Agent from a EAC-CPF file')))
        form = self._cw.vreg['forms'].select(self.__regid__, self._cw)
        if form.posting:
            posted = form.process_posted()
            authority = self._cw.cnx.entity_from_eid(posted['authority'])
            stream = posted['file']
            import_log = HTMLImportLog(os.path.basename(stream.filename))
            try:
                _, _, eid = self._cw.cnx.call_service(self.__regid__, stream=stream,
                                                      authority=authority,
                                                      import_log=import_log)
            except eac.InvalidXML as exc:
                msg = self._cw._('Invalid XML file')
                self.exception('error while importing %s', stream.filename)
                mtype = 'danger'
                import_log.record_fatal(
                    self._cw._('xml syntax error: ') + to_unicode(exc))
            except eac.MissingTag as exc:
                if exc.tag_parent:
                    err = self._cw._('Missing tag %(tag)s within element %(parent)s in XML file')
                    params = {'tag': exc.tag, 'parent': exc.tag_parent}
                    msg = err % params
                else:
                    err = self._cw._('Missing tag %(tag)s in XML file')
                    params = {'tag': exc.tag}
                    msg = err % params
                self.exception('error while importing %s', stream.filename)
                mtype = 'danger'
                import_log.record_fatal(err % params)
            except Exception as exc:  # pylint: disable=broad-except
                msg = self._cw._('EAC import failed')
                self.exception('error while importing %s', stream.filename)
                mtype = 'danger'
            else:
                agent = self._cw.find('Agent', eid=eid).one()
                msg = (self._cw._('EAC-CPF import completed: %s') %
                       agent.view('oneline'))
                mtype = 'success'
            self.w(tags.div(msg, klass="alert alert-%s" % mtype))
            if import_log.logs:
                self._cw.view('cw.log.table',
                              pyvalue=cwsources.log_to_table(
                                  self._cw, u''.join(import_log.logs)),
                              default_level='Warning', w=self.w)
        else:
            form.render(w=self.w)


#
# EAC export
#

class EACExportAction(action.Action):
    __regid__ = 'saem_ref.eac'
    __select__ = (action.Action.__select__
                  & one_line_rset()
                  & is_instance('Agent'))

    title = _('EAC export')
    category = 'moreactions'
    seda_download_vid = 'saem_ref.eac'

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.seda_download_vid)


class EACDownloadView(idownloadable.DownloadView):
    """EAC download view"""
    __regid__ = 'saem_ref.eac'
    __select__ = one_line_rset() & is_instance('Agent')

    http_cache_manager = httpcache.NoHTTPCacheManager
    adapter_id = 'EAC-CPF'

    def set_request_content_type(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.adapter_id)
        self._cw.set_content_type(adapter.content_type, filename=adapter.file_name,
                                  encoding=adapter.encoding, disposition='attachment')

    def call(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.adapter_id)
        self.w(adapter.dump())
