
class Registry(object):
    """
    A Registry object encapsulates a mapping of Django Models to the
    Adapter for them.
    """
    def __init__(self):
        self._registry = {}

    def register(self, model, func):
        """
        Register a function to adapt the Model.
        """
        self._registry[model] = func

    def adapter_for_instance(self, model):
        try:
            return self._registry[model.__class__](model)
        except KeyError:
            return TimelineAdapter(model)


registry = Registry()


def autodiscover():
    try:
        from django.utils.module_loading import autodiscover_modules
    except ImportError:
        from .module_loading import autodiscover_modules

    autodiscover_modules('adapters', register_to=registry)


class TimelineAdapter(object):
    attributes = ['caption', 'clickthrough_url', 'credit', 'headline',
                  'media_url', 'text', 'thumbnail', ]

    def __init__(self, instance):
        from django.contrib.contenttypes.models import ContentType
        self.instance = instance
        if instance:
            self.content_type = ContentType.objects.get_for_model(self.instance)
            self.object_id = str(self.instance.pk)
        else:
            self.content_type = None
            self.object_id = None

    def get_caption(self):
        """
        The caption of the media provided by the `media_url` attribute.
        """
        return ''

    def get_clickthrough_url(self):
        """
        The URL of the object to view it in its entirety. If provided, automatically
        inserted into the `text` via the `CLICK_THROUGH_TEMPLATE` setting.
        """
        return ''

    def get_credit(self):
        """
        The credit or attribution for the media provided by the `media_url` attribute.
        """
        return ''

    def get_headline(self):
        """
        A headline or title for the slide
        """
        return ''

    def get_media_url(self):
        """
        The URL to the media. Accepted types are at http://timeline.knightlab.com/docs/media-types.html

        Currently accepted:
        * Any image URLs ending in .jpg, .gif, .png, .jpeg
        * <iframe> markup
        * <blockquote> markup
        * URLs from Vimeo, DailyMotion, Vine, YouTube, SoundCloud, Twitter,
        GoogleMaps, GooglePlus, Instagram, Flickr, Imgur, DocumentCloud,
        Wikipedia, Storify, Embedly
        """
        return ''

    def get_text(self):
        """
        The text of the slide
        """
        return ''

    def get_thumbnail(self):
        """
        The URL to an image to use as a thumbnail in the timeline
        """
        return ''

    def __getattr__(self, name):
        """
        Return either the overridden value, or the original value, or raise
        and AttributeError.
        """
        if name in self.attributes:
            if hasattr(self, "instance") and self.instance:
                value = getattr(self, "get_%s" % name)()
                if value:
                    return value
                value = getattr(self.instance, name, "--NOVALUE--")
                if value != "--NOVALUE--" and value:
                    return value
                return ''
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.instance, name))
