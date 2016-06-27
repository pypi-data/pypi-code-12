from django.contrib import admin
from django.db import models
from django.views.generic import TemplateView
from django.db.models import fields

from .models import App, Model, Field

class AppView(TemplateView):
    def __init__(self, *args, **kwargs):
        super(AppView, self).__init__(*args, **kwargs)



