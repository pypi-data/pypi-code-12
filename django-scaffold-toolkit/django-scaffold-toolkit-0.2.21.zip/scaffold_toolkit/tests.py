from django import forms
from django.test import TestCase

# Create your tests here.
from scaffold_toolkit.forms.kindeditor import KindEditor


class KindForm(forms.Form):
    editor = forms.CharField(widget=KindEditor)


class KindeditorTest(TestCase):
    def test_form(self):
        form = KindForm()
        # print(form.media)
        e = KindEditor()
        print(e.render('editor', ''))
