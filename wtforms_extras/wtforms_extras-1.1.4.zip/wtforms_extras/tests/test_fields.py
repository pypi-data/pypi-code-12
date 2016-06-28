import unittest
from wtforms_extras import Renderer
from wtforms_extras.tests import form, TestForm, renderer


class FieldTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_render_text(self):
        self.assertIn('<input', renderer.field('text'))

    def test_render_textarea(self):
        self.assertIn('<textarea', renderer.field('textarea'))

    def test_render_boolean(self):
        self.assertIn('type="checkbox"', renderer.field('boolean'))

    def test_render_date(self):
        self.assertIn('<input', renderer.field('date'))

    def test_render_input(self):
        self.assertIn('<input', renderer.field('datetime'))

    def test_bootstrap(self):
        _renderer = Renderer(form, 'bootstrap')
        self.assertIn('form-group', _renderer.field('text'))
        self.assertNotIn('form-group has-error', _renderer.field('text'))

    def test_error(self):
        _form = TestForm()
        _form.validate()
        _renderer = Renderer(_form, 'bootstrap')
        self.assertIn('form-group has-error', _renderer.field('text'))
