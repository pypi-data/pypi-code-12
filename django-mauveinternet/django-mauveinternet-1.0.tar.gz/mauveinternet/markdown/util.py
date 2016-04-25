import re

from django.db.models import TextField
from django.contrib.admin import ModelAdmin
from django import forms

from django.utils.functional import curry

class MarkdownTextField(TextField):
    """This class does nothing different as the current implementation
    of Django's ModelAdmin would override any custom .formfield() method.
    Instead this just flags a textfield as being formatted in Markdown
    syntax."""

    def contribute_to_class(self, cls, name):
        """Hook up events so we can access the instance."""
        super(MarkdownTextField, self).contribute_to_class(cls, name)
        setattr(cls, 'get_html_%s' % name, curry(self.get_html_FIELD, name))

    def get_html_FIELD(self, name, instance):
        from mauveinternet.markdown.templatetags.markdown import markdown
        return markdown(getattr(instance, name))

    def formfield(self, **kwargs):
        defaults = {
            'widget': MarkdownTextarea
        }
        defaults.update(kwargs)
        return super(MarkdownTextField, self).formfield(**defaults)


class MarkdownTextarea(forms.Textarea):
    """A textarea widget that adds Javascript toolbars and previews for editing
    Markdown code"""
    class Media:
        css = {
            'all': [
                'mimarkdown/css/markdownarea.css'
            ]
        }
        # Also requires 'js/lib/prototype.js', but adding this here will typically include it twice
        js = [
            'mimarkdown/js/livepipe/livepipe.js',
            'mimarkdown/js/livepipe/textarea.js',
            'mimarkdown/js/showdown.js',
            'mimarkdown/js/markdownarea.js'
        ]

    def __init__(self, attrs={}):
        super(MarkdownTextarea, self).__init__(attrs)
        self.attrs.update({'class': 'markdown'})


class MarkdownModelAdmin(ModelAdmin):
    """A modeladmin that detects MarkdownTextFields and replaces the
    admin widget with a MarkdownTextArea."""
    def formfield_for_dbfield(self, dbfield, **kwargs):
        if isinstance(dbfield, MarkdownTextField):
            return dbfield.formfield()
        return super(MarkdownModelAdmin, self).formfield_for_dbfield(dbfield, **kwargs)


def to_plain_text(source, base_url=None):
    if base_url is None:
        from django.contrib.sites.models import Site
        base_url = Site.objects.get_current().domain

    from mauveinternet.markdown.templatetags.markdown import lookup_link
    from urlparse import urljoin

    footnotes = []
    def sub(mo):
        text = mo.group('text')
        link = mo.group('link')
        if text.strip() == link.strip():
            return text
        if link.startswith('internal:'):
            footnotes.append('http://' + base_url + lookup_link(link))
        else:
            footnotes.append(urljoin('http://%s/' % base_url, link))
        return text + '[%d]' % len(footnotes)

    source = re.sub(r'\[(?P<text>.*?)\]\((?P<link>.*?)\)', sub, source)
    if footnotes:
        source = source.strip() + '\n'
        for i, f in enumerate(footnotes):
            source += '\n[%d] %s' % (i + 1, f)

    return source
