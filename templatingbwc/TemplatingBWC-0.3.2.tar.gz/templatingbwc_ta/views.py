from blazeweb.globals import user
from blazeweb.views import View
from blazeweb.utils import redirect

import templatingbwc_ta.forms as forms
import templatingbwc_ta.model.orm as orm
from compstack.common.lib.views import CrudBase
from compstack.datagrid.lib import DataGrid, Col, YesNo, DateTime
from compstack.sqlalchemy import db

class Login(View):
    def default(self):
        user.is_authenticated = True
        user.display_name = 'testuser'
        user.add_message('success', 'You have been logged in.')
        redirect('/')

class Logout(View):
    def default(self):
        user.is_authenticated = False
        user.display_name = None
        user.add_message('success', 'You have been logged out.')
        redirect('/')

class UserMessages(View):
    def default(self):
        types = 'error', 'warning', 'notice', 'success'
        for type in types:
            user.add_message(type, 'This is a %s message.' % type)
        self.render_template()

class Forms(View):
    def default(self):
        self.assign('form1', forms.Make())
        self.assign('form2', forms.Form2())
        self.render_template()

class MakeCrud(CrudBase):

    def init(self):
        CrudBase.init(self, 'Make', 'Makes', forms.Make, orm.Make)
        self.allow_anonymous = True
        self.add_processor('option')

    def prep_makes(self):
        count = orm.Make.count()
        if count != 5:
            orm.Make.delete_all()
            orm.Make.add(label=u'Ford')
            orm.Make.add(label=u'Chevy')
            orm.Make.add(label=u'Mercury')
            orm.Make.add(label=u'GMC')
            orm.Make.add(label=u'Honda')

    def auth_post(self, action=None, objid=None, option=None):
        self.option = option
        self.prep_makes()
        CrudBase.auth_post(self, action, objid)

    def manage_init_grid(self):
        dg = DataGrid(
            db.sess.execute,
            per_page = 10 if self.option == 'one-page' else 3,
            class_='datagrid'
            )
        dg.add_col(
            'id',
            orm.Make.id,
            inresult=True
        )
        dg.add_tablecol(
            Col('Actions',
                extractor=self.manage_action_links,
                width_th='8%'
            ),
            orm.Make.id,
            sort=None
        )
        dg.add_tablecol(
            Col('Label', class_td='ta-left'),
            orm.Make.label,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            YesNo('Active'),
            orm.Make.active_flag,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            DateTime('Created'),
            orm.Make.createdts,
            filter_on=True,
            sort='both'
        )
        dg.add_tablecol(
            DateTime('Last Updated'),
            orm.Make.updatedts,
            filter_on=True,
            sort='both'
        )
        return dg
