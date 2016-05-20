from timelines.registration import registry, TimelineAdapter
from .models import Photo


class PhotoAdapter(TimelineAdapter):
    def get_headline(self):
        return self.instance.title

    def get_clickthrough_url(self):
        return self.instance.get_absolute_url()

    def get_credit(self):
        return self.instance.taken_by

    def get_text(self):
        return self.instance.description

    def get_media_url(self):
        return self.instance.photo.url

    def get_thumbnail(self):
        return self.instance.photo.url

registry.register(Photo, PhotoAdapter)
