import json

from django.core.management.base import BaseCommand, CommandError

from story.models import Story


class Command(BaseCommand):
    help = 'Exports a story for the cordova app'

    def add_arguments(self, parser):
        parser.add_argument('story_id', type=int)

    def handle(self, *args, **options):
        try:
            story = Story.objects.get(pk=options['story_id'])
        except Story.DoesNotExist:
            raise CommandError('Story ID "%s" does not exist'.format(
                options['story_id']))

        with open("client/www/story.json", "w") as fh:
            fh.write(story.to_json())
