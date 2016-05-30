from django import template
from copy import copy
from molo.yourwords.models import (YourWordsCompetition, ThankYou,
                                   YourWordsCompetitionIndexPage)

register = template.Library()


@register.inclusion_tag(
    'yourwords/your_words_competition_tag.html',
    takes_context=True
)
def your_words_competition(context):
    context = copy(context)
    locale_code = context.get('locale_code')
    page = YourWordsCompetitionIndexPage.objects.live().all().first()
    if page:
        competitions = (
            YourWordsCompetition.objects.live().child_of(page).filter(
                languages__language__is_main_language=True).specific())
    else:
        competitions = []

    context.update({
        'competitions': [
            a.get_translation_for(locale_code) or a for a in competitions]
    })
    return context


@register.assignment_tag(takes_context=True)
def load_thank_you_page_for_competition(context, competition):

    page = competition.get_main_language_page()
    locale = context.get('locale_code')

    qs = ThankYou.objects.live().child_of(page).filter(
        languages__language__is_main_language=True)

    if not locale:
        return qs

    if qs:
        return [a.get_translation_for(locale) or a for a in qs]
    else:
        return []
