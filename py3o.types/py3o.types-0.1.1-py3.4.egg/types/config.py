# -*- encoding: utf-8 -*-

from lxml import etree
import six
import zipfile

from py3o.types import Py3oInteger
from py3o.types import Py3oFloat
from py3o.types import Py3oDate
from py3o.types import Py3oTime
from py3o.types import Py3oDatetime

if six.PY3:  # pragma: no cover
    # in python 3 we want to emulate  binary files
    from six import BytesIO as StringIO
else:  # pragma: no cover
    # in python 2 we want to try and use the c Implementation if available
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO


class InvalidODFFile(Exception):
    u"""Exception raised for an invalid ODF file."""
    pass

InvalidODTFile = InvalidODFFile


class Py3oTypeConfig(object):
    """Configuration manager for py3o.types.

    :class:`~py3o.types.types.base.Py3oTypeMixin` subclasses in the 'types'
    class attribute are built according to the given configuration keys, to
    be used in the template's data source.
    This behavior can be extended by redefining the 'types' class attribute::

        class MyTypeConfig(Py3oTypeConfig):
            types = dict(Py3oTypeConfig.types,
                new_type=Py3oTypeMixinSubclassForNewType
            )

    The configuration is read-only. Configuration keys can be accessed,
    but not set or modified.
    """

    META_ARCNAME = 'meta.xml'

    META_ROOT_TAG_NS = 'office'
    META_ROOT_TAG_NAME = 'meta'

    META_VAR_TAG_NS = 'meta'
    META_VAR_TAG_NAME = 'user-defined'
    META_VAR_KEY_ATTRIBUTE = 'name'

    types = {
        'integer': Py3oInteger,
        'float': Py3oFloat,
        'date': Py3oDate,
        'time': Py3oTime,
        'datetime': Py3oDatetime,
    }

    def __init__(self, *args, **kwargs):
        self.config = kwargs
        self.types = {
            key: typ.get_type_for_config(kwargs)
            for key, typ in type(self).types.items()
        }

    @classmethod
    def get_meta_var_key_attribute(cls, nsmap):
        """Helper method to get the full name for meta:name attribute."""
        return '{{{}}}{}'.format(
            nsmap[cls.META_VAR_TAG_NS], cls.META_VAR_KEY_ATTRIBUTE
        )

    @classmethod
    def get_meta_tag(cls, nsmap):
        """Helper method to get the full name for <meta:user-defined> tags."""
        return '{{{}}}{}'.format(
            nsmap[cls.META_VAR_TAG_NS], cls.META_VAR_TAG_NAME
        )

    @classmethod
    def inspect_meta(cls, odf_file):
        """Helper method to get the root <office:meta> element."""

        try:
            odf_archive = zipfile.ZipFile(odf_file, 'r')
            meta_file = odf_archive.open(cls.META_ARCNAME)
            meta_tree = etree.parse(meta_file)
        except (zipfile.BadZipfile, KeyError) as e:  # pragma: no cover
            raise InvalidODFFile(six.text_type(e))
        except etree.XMLSyntaxError as e:  # pragma: no cover
            raise InvalidODFFile(u"Cannot parse XML in {}: {}".format(
                cls.META_ARCNAME, six.text_type(e)
            ))

        nsmap = meta_tree.getroot().nsmap
        root_tag = '{}:{}'.format(cls.META_ROOT_TAG_NS, cls.META_ROOT_TAG_NAME)
        meta_root = meta_tree.find(root_tag, nsmap)
        if meta_root is None:  # pragma: no cover
            raise InvalidODFFile(
                u"No {} element in {}".format(root_tag, cls.META_ARCNAME)
            )

        odf_archive.close()
        return meta_tree, meta_root, nsmap

    @classmethod
    def from_odf_file(cls, odf_file, defaults=None):
        """Extract the configuration from a given ODF file.

        The new :class:`Py3oTypeConfig` instance will use the configuration
        keys already present in the ODF file's metadata. A default value can
        be specified in case the key isn't present in the file.

        :param odf_file: The source ODF file as a file-like object.
        :param dict defaults: An optional mapping of default values.
        :returns: The extracted configuration.
        :rtype: Py3oTypeConfig
        """

        meta_tree, meta_root, nsmap = cls.inspect_meta(odf_file)
        meta_tag = cls.get_meta_tag(nsmap)
        meta_var_key = cls.get_meta_var_key_attribute(nsmap)

        meta_vars = meta_root.findall(meta_tag, nsmap)
        config = {
            var.get(meta_var_key): var.text for var in meta_vars
        }
        if defaults:
            config = dict(defaults, **config)

        return cls(**config)

    def apply_to_odf_file(self, in_file, out_file=None):
        """Insert the configuration keys into a ODF file's metadata.

        :param in_file: The target ODF file as a file-like object.
        :param out_file: a file-like object that will receive the result.
          If unspecified, the method will use a new in-memory file-like object.
        :returns: a file-like object that contains a replica of in_file,
          with the configuration keys set in its metadata.
        """

        if out_file is None:
            out_file = StringIO()

        meta_tree, meta_root, nsmap = self.inspect_meta(in_file)
        meta_tag = self.get_meta_tag(nsmap)
        meta_var_key = self.get_meta_var_key_attribute(nsmap)

        for old_var in meta_root.findall(meta_tag, nsmap):
            if old_var.get(meta_var_key) in self.config:
                meta_root.remove(old_var)

        for key, val in self.config.items():
            new_var = etree.SubElement(
                meta_root, meta_tag, **{meta_var_key: key}
            )
            new_var.text = six.text_type(val)

        meta_file = etree.tostring(meta_tree)

        in_archive = zipfile.ZipFile(in_file, 'r')
        out_archive = zipfile.ZipFile(out_file, 'w', allowZip64=True)

        for info_zip in in_archive.infolist():
            if info_zip.filename == self.META_ARCNAME:
                file_data = meta_file
            else:
                file_data = in_archive.read(info_zip.filename)
            out_archive.writestr(info_zip, file_data)

        out_archive.close()
        out_file.seek(0)
        return out_file

    def __getitem__(self, key):
        """Return the value of the configuration key.

        :param str key: The configuration key
        :returns: The configuration value
        :rtype: str
        """
        return self.config[key]

    def __getattr__(self, attr):
        """Return the :class:`Py3oTypeMixin` subclass for the requested type.

        :param str attr: The requested type.
         See :attr:`Py3oTypeConfig.types`
        :returns: the :class:`Py3oTypeMixin` subclass built by the config.
        :rtype: type
        """
        config_type = self.types.get(attr)
        if config_type is not None:
            return config_type
        else:
            raise AttributeError(attr)
