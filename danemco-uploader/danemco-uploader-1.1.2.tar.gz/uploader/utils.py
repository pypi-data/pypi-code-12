import os
import urlparse
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def _get_thumbnail_path(path, width=None, height=None):
    """ create thumbnail path from path and required width and/or height.

        thumbnail file name is constructed like this:
            <basename>_t_[w<width>][_h<height>].<extension>
    """

    # one of width/height is required
    assert (width is not None) or (height is not None)

    basedir = os.path.dirname(path) + '/'
    base, ext = os.path.splitext(os.path.basename(path))

    # make thumbnail filename
    th_name = base + '_t'
    if (width is not None) and (height is not None):
        th_name += '_w%d_h%d' % (width, height)
    elif width is not None:
        th_name += '%d' % width  # for compatibility with admin
    elif height is not None:
        th_name += '_h%d' % height
    th_name += ext

    return urlparse.urljoin(basedir, th_name)


def _get_path_from_url(url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ make filesystem path from url """

    if url.startswith(url_root):
        url = url[len(url_root):]  # strip media root url

    if url.startswith('/'):
        url = url[1:]

    return os.path.normpath(os.path.join(root, url))


def _get_url_from_path(path, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ make url from filesystem path """

    if path.startswith(root):
        path = path[len(root):]  # strip media root

    return urlparse.urljoin(root, path.replace('\\', '/'))


def _has_thumbnail(photo_url, width=None, height=None, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    # one of width/height is required
    assert (width is not None) or (height is not None)

    return os.path.isfile(_get_path_from_url(_get_thumbnail_path(photo_url, width, height), root, url_root))


def make_thumbnail(photo_url, width=None, height=None, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ create thumbnail """

    # one of width/height is required
    assert (width is not None) or (height is not None)

    if not photo_url:
        return None

    if isinstance(photo_url, InMemoryUploadedFile):
        temp_url = os.path.join(url_root, "temp", photo_url.name)
        th_url = _get_thumbnail_path(temp_url, width, height)
        th_path = _get_path_from_url(th_url, root, url_root)
        photo_path = photo_url  # _get_path_from_url(temp_url, root, url_root)
    else:
        temp_url = photo_url
        th_url = _get_thumbnail_path(photo_url, width, height)
        th_path = _get_path_from_url(th_url, root, url_root)
        photo_path = _get_path_from_url(photo_url, root, url_root)

    if os.access(th_path, os.R_OK):
        return th_url

    # make thumbnail

    # get original image size
    orig_w, orig_h = get_image_size(temp_url, root, url_root)
    if not isinstance(photo_url, InMemoryUploadedFile) and (orig_w is None) and (orig_h) is None:
        # something is wrong with image
        return photo_url

    # make proper size
    if (width is not None) and (height is not None):
        if (orig_w == width) and (orig_h == height):
            # same dimensions
            return None
        size = (width, height)
    elif width is not None:
        if orig_w == width:
            # same dimensions
            return None
        size = (width, orig_h)
    elif height is not None:
        if orig_h == height:
            # same dimensions
            return None
        size = (orig_w, height)

    try:
        try:
            os.makedirs(os.path.dirname(th_path))
        except Exception, ex:
            print ex
        img = Image.open(photo_path).copy()
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(th_path, quality=90)
    except Exception:
        # Exception('%s, %s, %s' % (photo_path, size, th_path))
        return photo_url

    return th_url


def get_image_size(photo_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ returns image size.

        image sizes are cached (using separate locmem:/// cache instance)
    """

    path = os.path.join(root, _get_path_from_url(photo_url, root, url_root))

    try:
        size = Image.open(path).size
    except Exception, err:
        # this goes to webserver error log
        import sys
        print >>sys.stderr, '[GET IMAGE SIZE] error %s for file %r' % (err, photo_url)
        return None, None

    return size
