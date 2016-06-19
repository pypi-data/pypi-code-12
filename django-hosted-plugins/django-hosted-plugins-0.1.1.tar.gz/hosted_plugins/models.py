from collections import OrderedDict
from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Platform(models.Model):
    platform = models.SlugField(max_length=255)
    plugin = models.SlugField(max_length=255)
    
    def __str__(self):
        return self.plugin + ' for ' + self.platform

@python_2_unicode_compatible
class Update(models.Model):
    MAX_VERSION_LENGTH = 32
    ARCHIVE_ZIP = 1
    ARCHIVE_TARGZ = 2
    ARCHIVE_TYPE = OrderedDict([
        (ARCHIVE_ZIP, 'zip'),
        (ARCHIVE_TARGZ, 'tar.gz'),
    ])
    platform = models.ForeignKey('hosted_plugins.Platform', related_name='updates')
    min_reqd = models.CharField(max_length=MAX_VERSION_LENGTH)
    max_tested = models.CharField(max_length=MAX_VERSION_LENGTH, blank=True, default='')
    version = models.CharField(max_length=MAX_VERSION_LENGTH)
    release_date = models.DateTimeField(default=timezone.now)
    docs = models.ManyToManyField('hosted_plugins.Documentation', related_name='updates', blank=True)
    archive_type = models.SmallIntegerField(choices=ARCHIVE_TYPE.items())
    filesize = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return '%(plugin)s v%(version)s for %(platform)s v%(min_reqd)s-v%(max_tested)s' % {
            'plugin': self.platform.plugin,
            'version': self.version,
            'platform': self.platform.platform,
            'min_reqd': self.min_reqd,
            'max_tested': self.max_tested
        }
    
    @property
    def url(self):
        if not hasattr(self, '_cached_url'):
            self._cached_url = reverse('hosted-plugins:update-detail', kwargs={
                'platform': self.platform.platform.lower(),
                'pk': self.id,
                'plugin': self.platform.plugin.lower(),
                'version': self.version,
                'download': self.ARCHIVE_TYPE[self.archive_type]
            })
        return self._cached_url
    
    @property
    def filename(self):
        if not hasattr(self, '_cached_filename'):
            self._cached_filename = '%(plugin)s-%(version)s.%(download)s' % {
                'plugin': self.platform.plugin.lower(),
                'version': self.version,
                'download': self.ARCHIVE_TYPE[self.archive_type]
            }
        return self._cached_filename
    
    @property
    def mime_type(self):
        if self.archive_type==self.ARCHIVE_ZIP:
            return 'application/zip'
        elif self.archive_type==self.ARCHIVE_TARGZ:
            return 'application/x-gzip'
        else:
            return 'application/octet-stream'

@python_2_unicode_compatible
class Checksum(models.Model):
    CHECKSUM_CRC32 = 1
    CHECKSUM_MD5 = 2
    CHECKSUM_SHA1 = 3
    CHECKSUM_SHA256 = 4
    CHECKSUM_TYPE = OrderedDict([
        (CHECKSUM_CRC32, 'crc32'),
        (CHECKSUM_MD5, 'md5'),
        (CHECKSUM_SHA1, 'sha1'),
        (CHECKSUM_SHA256, 'sha256'),
    ])
    update = models.ForeignKey('hosted_plugins.Update', related_name='checksums')
    checksum_type = models.SmallIntegerField(choices=CHECKSUM_TYPE.items())
    checksum = models.CharField(max_length=64)
    
    def __str__(self):
        return '%(checksum_type)s:%(checksum)s' % {
            'checksum_type': self.CHECKSUM_TYPE[self.checksum_type],
            'checksum': self.checksum,
        }

@python_2_unicode_compatible
class Documentation(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    content = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title + self.created_on.strftime(" (%Y-%m-%d %H:%M:%S)")
