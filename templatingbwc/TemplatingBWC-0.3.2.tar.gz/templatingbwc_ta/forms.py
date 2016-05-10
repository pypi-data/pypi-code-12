import datetime

from blazeweb.routing import url_for
from savalidation import ValidationError
from webhelpers.html.tags import link_to

from compstack.common.lib.forms import Form

class LookupMixin(object):
    def add_active_flag(self):
        return self.add_checkbox('active_flag', 'Active', defaultval=True)

    def add_label(self):
        return self.add_text('label', 'Label', required=True)

    def add_submit(self, crud_view=None):
        sg = self.add_elgroup('submit-group', class_='submit-only')
        sg.add_submit('submit')
        crud_view = crud_view or self.__class__.__name__ + 'Crud'
        sg.add_static('cancel', None, link_to('Cancel', url_for(crud_view, action='manage'), title='Go back to the manage page'))
        return sg

    def add_lookup_fields(self, crud_view=None):
        return self.add_label(), \
            self.add_active_flag(), \
            self.add_submit(crud_view)

class Make(Form, LookupMixin):
    def init(self):
        self.add_lookup_fields()

class Form2(Form):
    def init(self):
        el = self.add_button('button', 'Button', defaultval='PushMe')
        el = self.add_checkbox('checkbox', 'Checkbox')
        el = self.add_file('file', 'File')
        el = self.add_hidden('hidden', defaultval='my hidden val')
        el = self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.add_text('text', 'Text')
        el = self.add_password('password', 'Password')
        el.add_note('I have a note')
        el = self.add_confirm('confirm', 'Confirm Password', match='password')
        el.add_error('it did not match')
        el = self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        emel = self.add_email('email', 'Email', required=True)
        el = self.add_time('time', 'Time')
        el.add_note('I have two notes')
        el.add_note('my second note')
        el = self.add_url('url', 'URL')
        el.add_note('I have a note')
        el.add_error('test error')
        el.add_error('another test error')
        options = [('1', 'one'), ('2','two')]
        el = self.add_select('select', options, 'Select')
        el = self.add_mselect('mselect', options, 'Multi Select')
        el = self.add_textarea('textarea', 'Text Area')
        el = self.add_passthru('passthru', 123)
        el = self.add_fixed('fixed', 'Fixed', 'fixed val')
        el = self.add_static('static', 'Static', 'static val')
        el = self.add_header('header', 'header')

        # test element group with class attribute
        sg = self.add_elgroup('group')
        sg.add_text('ingroup1', 'ingroup1')
        sg.add_text('ingroup2', 'ingroup2')

        self.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.add_radio('r2', 'r2', defaultval='car', group='rgroup')

        self.add_radio('animal_dog', 'dog', defaultval='dog', group='animalgroup', label_after=True)
        self.add_radio('animal_cat', 'cat', defaultval='cat', group='animalgroup', label_after=True)

        el = self.add_reset('reset')
        el = self.add_submit('submit')
        el = self.add_cancel('cancel')
