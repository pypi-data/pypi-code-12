from django.contrib import admin
from mauveinternet.markdown.util import MarkdownModelAdmin

from models import *

class InlineHelpAdmin(MarkdownModelAdmin):
    list_display = ['__unicode__', 'has_description']

admin.site.register(InlineHelp, InlineHelpAdmin)
