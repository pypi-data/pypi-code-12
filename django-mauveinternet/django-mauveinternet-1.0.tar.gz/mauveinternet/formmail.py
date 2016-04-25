from django.contrib.sites.models import Site
from django import forms
if hasattr(forms, 'Manipulator'):
    try:
        from django import newforms as forms
    except ImportError:
        from django import forms
from django.core.mail import send_mail, mail_managers

def mail_form_to_managers(form, preamble=None, exclude=[]):
    """Sends an email to all members of the staff with ordered list of fields
    and values for any form that subclasses FormMail

    """
    site_name = Site.objects.get_current().name
    form_name = form.__class__.__name__
    subject = u'%s %s Submission' % (site_name, form_name)
    data = []
    if preamble:
        data = [preamble]

    for f in form:
        if f.name in exclude:
            continue
        try:
            val = form.cleaned_data[f.name]
        except KeyError:
            continue

        if isinstance(f.field, forms.ChoiceField):
            choices = dict(f.field.choices)
            data += [u'%s: %s' % (f.label, choices.get(val, val))]
        else:
            data += [u'%s: %s' % (f.label, val)]

    message = u'\n\n'.join(data)

    mail_managers(subject, message)
