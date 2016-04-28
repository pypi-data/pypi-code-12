from django.db import models
from .utils import make_thumbnail

UL_PATH = 'uploads/%Y/%m/%d/'


class ThumbnailSize(models.Model):
    name = models.CharField(max_length=30)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()

    def as_size(self):
        return u"%sx%s" % (self.width, self.height)

    def __unicode__(self):
        return u'%s (%ix%i)' % (self.name, self.width, self.height)

    class Meta:
        unique_together = (('height', 'width'),)
        ordering = ('width', 'height')


class Thumbnail(models.Model):
    upload = models.ForeignKey('ImageUpload')
    size = models.ForeignKey(ThumbnailSize)
    image = models.ImageField(upload_to='%simages/' % UL_PATH, max_length=255)

    def __unicode__(self):
        try:
            return u'%s (%ix%i)' % (self.upload,
                                    self.image.width,
                                    self.image.height)
        except:
            return u'%s (%s)' % (self.upload, self.size.name)

    class Meta:
        unique_together = (('upload', 'size'),)


class ImageUpload(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='%simages/' % UL_PATH, max_length=255)
    resize_image = models.ManyToManyField(ThumbnailSize, blank=True, help_text='Choose the size or sizes you would like the system to create for you. Choose none of the sizes to preserve the dimensions of the image you are uploading.')

    """
    def __init__(self, *args, **kwargs):
        super(ImageUpload, self).__init__(*args, **kwargs)

        if self.id and not self.original_name:
            self.original_name = self.image.name
            self.save()
    """

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.image.url


class FileUpload(models.Model):
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='%sfiles/' % UL_PATH, max_length=255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.file.url


def create_thumbnails(sender, instance, created, **kwargs):
    """
    Creates the thumbnails for an image upload
    """
    for size in instance.resize_image.all():
        tn = make_thumbnail(
            instance.image.url,
            width=size.width,
            height=size.height,
        )

        if tn:
            thumb, created = Thumbnail.objects.get_or_create(
                size=size,
                upload=instance,
            )

            thumb.image = tn
            thumb.save()


def force_thumbnails(sender, instance, **kwargs):
    """
    Forces an image upload to be resaved when it doesn't have any thumbnails
    """
    if instance.id and instance.thumbnail_set.count() == 0:
        instance.save()

models.signals.post_save.connect(create_thumbnails, sender=ImageUpload)
models.signals.post_init.connect(force_thumbnails, sender=ImageUpload)
