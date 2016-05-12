from datetime import datetime, timedelta
from django import forms
from django.forms.widgets import DateTimeInput


class PurgeForm(forms.Form):
    timestamp = forms.DateTimeField(
        label='purge entries older than (YYYY-MM-DD hh:mm:ss):',
        widget=DateTimeInput(
            format='%Y-%m-%d %H:%M:%S',
        ),
        initial=datetime.now() - timedelta(days=1))
