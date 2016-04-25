from django.shortcuts import get_object_or_404

from mauveinternet.shortcuts import template
from mauveinternet.help.models import *


def ajax_help(request, slug):
    """AJAX view serving just the content for the inline help item"""
    help = get_object_or_404(InlineHelp, slug=slug)
    return template(request, 'help/inline_help.html', help=help)


def quick_help(request, slug):
    """Standard fall-back view for inline help."""
    help = get_object_or_404(InlineHelp, slug=slug)
    return template(request, 'help/quick_help.html', help=help)
