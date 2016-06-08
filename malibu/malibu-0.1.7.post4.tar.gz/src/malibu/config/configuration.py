# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import io

from contextlib import closing
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from malibu.text import unicode_type, unicode2str


__doc__ = """
malibu.config.configuration
---------------------------

INI-style configuration implementation with some special features
to make configuration a little simpler.

"""


class ConfigurationSection(dict):
    """ The ConfigurationSection class is a modified dictionary that
        provides "helpers" to grab a configuration entry in it's correct
        "type" form.
    """

    def __init__(self):

        dict.__init__(self)

        self.mutable = True

    def __getitem__(self, key):

        try:
            return dict.__getitem__(self, key)
        except (IndexError, KeyError):
            raise KeyError("Unknown configuration key '%s'." % (key))

    def __setitem__(self, key, value):

        if self.mutable:
            self.update({key: value})
        else:
            raise AttributeError("This section is not mutable.")

    def set_mutable(self, mutable):
        """ Enforces immutability on a configuration section.
        """

        self.mutable = mutable

    def set(self, key, value):
        """ Allows programmatic setting of configuration entries.
        """

        return self.__setitem__(key, value)

    def get(self, key, default=None):
        """ The bare "get" on the underlying dictionary that returns the
            configuration entry in whatever form it was parsed as, typically
            a string.
        """

        try:
            return self.__getitem__(key)
        except IndexError:
            return default

    def get_list(self, key, delimiter=",", strip=True, default=[]):
        """ Attempts to take a something-delimited string and "listify" it.
            If an error occurs while attempting to listify, :param default:
            will be returned.
        """

        try:
            val = self.get(key)
            if isinstance(val, list):
                return val
            l = val.split(delimiter) if len(val) > 0 else default
            if strip:
                return [item.strip() for item in l]
            else:
                return l
        except:
            return default

    def get_string(self, key, default=""):
        """ Attempts to take the value stored and retrieve it safely as a
            string. If the value mapped to by :param key: is "!None", the
            object returned is NoneType.

            If an error occurs while trying to safely retrieve the string,
            :param default: is returned.
        """

        try:
            if str(self.get(key)) == '!None':
                return None
            return str(self.get(key)) or default
        except:
            return default

    def get_int(self, key, default=None):
        """ Attempts to fetch and intify the value mapped to by
            :param key:. If an error occurs while trying to intify the value,
            :param default: will be returned.
        """

        try:
            return int(self.get(key)) or default
        except:
            return default

    def get_bool(self, key, default=False):
        """ Attempts to safely fetch the value mapped to by :param key:.
            After successful retrieval, a conditional coercion to boolean
            is attempt. If the coercion to boolean fails, :param default: is
            returned.
        """

        try:
            val = self.get(key) or default
            if isinstance(val, bool):
                return val
            elif isinstance(val, unicode_type()):
                if val.lower() == 'true':
                    self.set(key, True)
                    return True
                elif val.lower() == 'false':
                    self.set(key, False)
                    return False
                else:
                    return default
            elif isinstance(val, int):
                if val == 1:
                    self.set(key, True)
                    return True
                elif val == 0:
                    self.set(key, False)
                    return False
                else:
                    return default
            else:
                print("get_bool: unknown value type")
                print("type(val) => ", type(val))
                print("unicode_type() => ", unicode_type())
                return default
        except:
            return default


class SectionPromise(object):
    """ this is a configuration section promise
        to make resolution of linked sections post-load
        easier.
    """

    promises = []

    def __init__(self, config, section, key, link):

        self.config = config
        self.section = section
        self.key = key
        self.link = link
        self.__fulfilled = False

        SectionPromise.promises.append(self)

    def __str__(self):
        """ Convert directly to a string for recreating the link
            during config write.  Better for serialization.
        """

        return '@' + self.link

    def resolve(self):
        """ Resolves a SectionPromise into the proper dictionary
            value.
        """

        if self.__fulfilled:
            return

        section = self.config.get_section(self.section)
        link = self.config.get_section(self.link)
        target = section.get(self.key)

        if isinstance(target, list):
            target.remove(self)
            target.append(link)
            section.set(self.key, target)
        else:
            section.set(self.key, link)

        # Preserve the promise for writing back out.
        section.set("_%s_promise" % (self.key), self)
        self.__fulfilled = True


class Configuration(object):
    """ Configuration class performs the loading, saving, and parsing
        of an INI-style configuration file with a few advanced features
        such as value typing, file inclusion, section references, and
        JSON-style list definition.
    """

    def __init__(self):
        """ initialise the container
            store in key:value format withing the certain category
        """

        self.__container = ConfigurationSection()

        self._filename = None

        self.loaded = False

    def __resolve_links(self):
        """ resolves all linked references (SectionPromise instances).
        """

        for promise in SectionPromise.promises:
            promise.resolve()

        SectionPromise.promises = []

    def add_section(self, section_name):
        """ Adds a new configuration section to the main dictionary.
        """

        section = ConfigurationSection()
        self.__container.set(section_name, section)

        return section

    def remove_section(self, section_name):
        """ Removes a section from the main dictionary.
        """

        del self.__container[section_name]

    @property
    def sections(self):
        """ Returns a list of all sections in the configuration.
        """

        return self.__container.keys()

    def has_section(self, section_name):
        """ Return if this configuration has a section named
            :param section_name:.
        """

        return section_name in self.__container

    def get_section(self, section_name):
        """ Return the internal ConfigurationSection representation of a
            set of configuration entries.

            :param str section_name: Section name to retrieve.
            :rtype: malibu.config.configuration.ConfigurationSection
            :return: ConfigurationSection or None
        """

        if self.__container.__contains__(section_name):
            return self.__container[section_name]
        else:
            return None

    def get_namespace(self, namespace):
        """ Returns a set of ConfigurationSection objects that are prefixed
            with the namespace specified above.

            If no configuration sections have the requested namespace, None
            is returned.

            :param str namespace: Namespace to find in section name.
            :rtype: set
            :return: dict or None
        """

        if not namespace:
            raise ValueError("Namespace can not be none")

        sections = {}

        for section_name in self.sections:
            if section_name.startswith(namespace + ":"):
                short_name = section_name.split(":")[1]
                sections.update({
                    short_name: self.get_section(section_name),
                })
            else:
                continue

        if len(sections) == 0:
            return {}
        else:
            return sections

    def unload(self):
        """ Unload an entire configuration
        """

        self.__container.clear()
        self.loaded = False

    def reload(self):
        """ Reload the configuration from the initially specified file
        """

        self.unload()
        self.load(self._filename)

    def save(self, filename=None):
        """ Write the loaded configuration into the file specified by
            :param filename: or to the initially specified filename.

            All linked sections are flattened into SectionPromise instances
            and written to the configuration properly.

            :raises ValueError: if no save filename available.
        """

        if filename is None:
            filename = self._filename

        if filename is None:
            raise ValueError('No filename specified and no stored filename.')

        with closing(io.open(filename, 'w')) as config:
            for section, smap in self.__container.items():
                config.write("[%s]\n" % (section))
                for key, value in smap.items():
                    if isinstance(value, list):
                        value = "+list:" + json.dumps(value)
                    elif isinstance(value, ConfigurationSection):
                        if "_%s_promise" % (key) in smap:
                            value = str(smap["_%s_promise" % (key)])
                        else:
                            value = str(value)
                    elif isinstance(value, SectionPromise):
                        continue
                    elif isinstance(value, io.TextIOBase):
                        value = "+file:" + value.name
                    else:
                        value = str(value)
                    config.write("%s = %s\n" % (key, value))
                config.write("\n")

    def load(self, filename):
        """ Loads a INI-style configuration from the given filename.
            If the file can not be opened from :param filename:,
            a ValueError is raised. Upon any other error,
            the exception is simply raised to the top.

            :raises ValueError: if no filename provided.
            :raises Exception: upon other error
        """

        try:
            fobj = io.open(filename, 'r')
            self._filename = filename
            self.load_file(fobj)
            fobj.close()
        except IOError:
            raise ValueError("Invalid filename '%s'." % (filename))
        except:
            raise

    def load_file(self, fobj):
        """ Performs the full load of the configuration file from
            the underlying file object. If a file object is not passed in
            :param fobj:, TypeError is raised.

            :raises TypeError: if :param fobj: is not a file type
        """

        if not fobj or not isinstance(fobj, io.IOBase):
            raise TypeError("Invalid file object.")

        if self.loaded:
            self.__container.clear()

        section_name = None
        option_key = None
        option_value = None

        for line in fobj.readlines():
            line = line.strip('\n').lstrip()

            if line.startswith('#') or line.startswith(';'):
                continue
            elif line.startswith('[') and line.endswith(']'):
                # This is the beginning of a section tag.
                section_name = line[1:-1]
                if not self.get_section(section_name):
                    self.add_section(section_name)
                continue
            elif '=' in line:
                s = line.split('=', 1)
                # strip whitespace
                option_key = s[0].strip()
                option_value = s[1].strip() if s[1] is not '' else None

                if option_value and option_value[-1] == ';':
                    option_value = option_value[0:-1]
                section = self.get_section(section_name)

                if not option_value:
                    section.set(option_key, option_value)
                    continue

                if option_value.startswith('+'):  # typed reference / variable
                    dobj_type = option_value.split(':')[0][1:]
                    if len(option_value.split(':')) > 2:
                        dobj_value = ':'.join(option_value.split(':')[1:])
                    else:
                        dobj_value = option_value.split(':')[1]

                    if dobj_type.lower() == 'file':
                        try:
                            section.set(option_key, io.open(dobj_value, 'r'))
                        except:
                            try:
                                section.set(
                                    option_key,
                                    io.open(dobj_value, 'w+'))
                            except:
                                section.set(option_key, None)
                    elif dobj_type.lower() in ["url", "uri"]:
                        try:
                            section.set(option_key, urlopen(dobj_value).read())
                        except:
                            raise
                        section.set(option_key, None)
                    elif dobj_type.lower() == 'list':
                        try:
                            dobj_list = json.loads('%s' % (dobj_value))
                            dobj_list = unicode2str(dobj_list)
                        except:
                            dobj_list = []
                        dobj_repl = []
                        for item in dobj_list:
                            if item.startswith(b'@'):
                                link_name = item[1:]
                                if not self.get_section(link_name):
                                    dobj_repl.append(
                                        SectionPromise(
                                            self,
                                            section_name,
                                            option_key,
                                            link_name))
                                else:
                                    link = self.get_section(link_name)
                                    dobj_repl.append(link)
                            else:
                                dobj_repl.append(item)
                        section.set(option_key, dobj_repl)
                    else:
                        section.set(option_key, option_value)
                elif option_value.startswith('@'):  # section reference
                    link_name = option_value[1:]
                    if not self.get_section(link_name):
                        section.set(
                            option_key,
                            SectionPromise(
                                self,
                                section_name,
                                option_key,
                                link_name))
                    else:
                        link = self.get_section(link_name)
                        section.set(option_key, link)
                else:
                    section.set(option_key, option_value)
                continue
            else:
                continue

        self.__resolve_links()
        self.loaded = True
