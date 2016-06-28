import unittest
from wtforms_extras import Renderer
from wtforms_extras.tests import form, renderer, TestForm


class FieldTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_render_form(self):
        self.assertIn('class="form-wrapper"', renderer())

    def test_render_bootstrap(self):
        _renderer = Renderer(form, 'bootstrap')
        self.assertIn('class="form-wrapper"', _renderer())

    def test_error(self):
        _form = TestForm()
        _form.validate()
        _renderer = Renderer(_form, 'bootstrap')
        self.assertIn('form-group has-error', _renderer())
