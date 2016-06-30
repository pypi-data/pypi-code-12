# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>

"""Module metadata manipulation library.

A python library for manipulation of the proposed module metadata format.

Example usage:

.. code:: python

    import modulemd
    mmd = modulemd.ModuleMetadata()
    mmd.load("metadata.yaml")
    mmd.add_module_license("ISC")
    mmd.components.rpms.clear_packages()
    mmd.components.rpms.add_package("example", multilib=["x86_64"])
    mmd.dump("out.yaml")
"""

import yaml

from modulemd.components import ModuleComponents
from modulemd.content import ModuleContent
from modulemd.rpms import ModuleRPMs
from modulemd.profile import ModuleProfile

supported_mdversions = ( 0, )

class ModuleMetadata(object):
    """Class representing the whole module."""

    def __init__(self):
        """Creates a new ModuleMetadata instance."""
        self.mdversion = max(supported_mdversions)
        self.name = ""
        self.version = ""
        self.release = ""
        self.summary = ""
        self.description = ""
        self.module_licenses = set()
        self.content_licenses = set()
        self.buildrequires = dict()
        self.requires = dict()
        self.community = ""
        self.documentation = ""
        self.tracker = ""
        self.xmd = dict()
        self.profiles = dict()
        self.components = None

    def load(self, f):
        """Loads a metadata file into the instance.

        :param str f: File name to load
        """
        with open(f, "r") as infile:
            data = infile.read()
        self.loads(data)

    def loads(self, s):
        """Loads metadata from a string.

        :param str s: Raw metadata in YAML
        :raises ValueError: If the metadata is invalid or unsupported.
        """
        yml = yaml.safe_load(s)
        if yml["document"] != "modulemd":
            raise ValueError("The supplied data isn't a valid modulemd document")
        if yml["version"] not in supported_mdversions:
            raise ValueError("The supplied metadata version isn't supported")
        self.mdversion = yml["version"]
        self.name = yml["data"]["name"]
        self.version = yml["data"]["version"]
        self.release = yml["data"]["release"]
        self.summary = yml["data"]["summary"]
        self.description = str(yml["data"]["description"]).strip()
        self.module_licenses = set(yml["data"]["license"]["module"])
        if "content" in yml["data"]["license"]:
            self.content_licenses = set(yml["data"]["license"]["content"])
        if "dependencies" in yml["data"]:
            if "buildrequires" in yml["data"]["dependencies"]:
                self.buildrequires = yml["data"]["dependencies"]["buildrequires"]
            if "requires" in yml["data"]["dependencies"]:
                self.requires = yml["data"]["dependencies"]["requires"]
        if "references" in yml["data"]:
            if "community" in yml["data"]["references"]:
                self.community = yml["data"]["references"]["community"]
            if "documentation" in yml["data"]["references"]:
                self.documentation = yml["data"]["references"]["documentation"]
            if "tracker" in yml["data"]["references"]:
                self.tracker = yml["data"]["references"]["tracker"]
        if "xmd" in yml["data"]:
            self.xmd = yml["data"]["xmd"]
        if "profiles" in yml["data"]:
            for profile in yml["data"]["profiles"].keys():
                self.profiles[profile] = ModuleProfile()
                if "rpms" in yml["data"]["profiles"][profile]:
                    self.profiles[profile].rpms = \
                        set(yml["data"]["profiles"][profile]["rpms"])
        if "components" in yml["data"]:
            self.components = ModuleComponents()
            if "rpms" in yml["data"]["components"]:
                self.components.rpms = ModuleRPMs()
                if "dependencies" in yml["data"]["components"]["rpms"]:
                    self.components.rpms.dependencies = \
                        yml["data"]["components"]["rpms"]["dependencies"]
                if "api" in yml["data"]["components"]["rpms"]:
                    self.components.rpms.api = \
                        set(yml["data"]["components"]["rpms"]["api"])
                if "packages" in yml["data"]["components"]["rpms"]:
                    for p, e in yml["data"]["components"]["rpms"]["packages"].items():
                        extras = dict()
                        extras["rationale"] = e["rationale"]
                        if "repository" in e:
                            extras["repository"] = e["repository"]
                        if "cache" in e:
                            extras["cache"] = e["cache"]
                        if "commit" in e:
                            extras["commit"] = e["commit"]
                        if "arches" in e:
                            extras["arches"] = e["arches"]
                        if "multilib" in e:
                            extras["multilib"] = e["multilib"]
                        self.components.rpms.add_package(p, **extras)
                if "filter" in yml["data"]["components"]["rpms"]:
                    self.components.rpms.filter = \
                        set(yml["data"]["components"]["rpms"]["filter"])

    def dump(self, f):
        """Dumps the metadata into the supplied file.

        :param str f: File name of the destination
        """
        data = self.dumps()
        with open(f, "w") as outfile:
            outfile.write(data)

    def dumps(self):
        """Dumps te metadata into a string.

        :rtype: str
        :raises Exception: If metadata validation fails
        """
        if not self.validate:
            raise Exception("Metadata validation failed")
        data = dict()
        # header
        data["document"] = "modulemd"
        data["version"] = self.mdversion
        # data
        data["data"] = dict()
        data["data"]["name"] = self.name
        data["data"]["version"] = self.version
        data["data"]["release"] = self.release
        data["data"]["summary"] = self.summary
        data["data"]["description"] = self.description
        data["data"]["license"] = dict()
        data["data"]["license"]["module"] = list(self.module_licenses)
        if self.content_licenses:
            data["data"]["license"]["content"] = list(self.content_licenses)
        if self.buildrequires or self.requires:
            data["data"]["dependencies"] = dict()
            if self.buildrequires:
                data["data"]["dependencies"]["buildrequires"] = self.buildrequires
            if self.requires:
                data["data"]["dependencies"]["requires"] = self.requires
        if self.community or self.documentation or self.tracker:
            data["data"]["references"] = dict()
            if self.community:
                data["data"]["references"]["community"] = self.community
            if self.documentation:
                data["data"]["references"]["documentation"] = self.documentation
            if self.tracker:
                data["data"]["references"]["tracker"] = self.tracker
        if self.xmd:
            data["data"]["xmd"] = self.xmd
        if self.profiles:
            data["data"]["profiles"] = dict()
            for profile in self.profiles.keys():
                if self.profiles[profile].rpms:
                    data["data"]["profiles"][profile] = dict()
                    data["data"]["profiles"][profile]["rpms"] = \
                        list(self.profiles[profile].rpms)
        if self.components:
            data["data"]["components"] = dict()
            if self.components.rpms:
                data["data"]["components"]["rpms"] = dict()
                data["data"]["components"]["rpms"]["dependencies"] = \
                    self.components.rpms.dependencies
                data["data"]["components"]["rpms"]["api"] = \
                    list(self.components.rpms.api)
                if self.components.rpms.packages:
                    data["data"]["components"]["rpms"]["packages"] = dict()
                    for p, e in self.components.rpms.packages.items():
                        extra = dict()
                        extra["rationale"] = e["rationale"]
                        if "commit" in e:
                            extra["commit"] = e["commit"]
                        if "repository" in e:
                            extra["repository"] = e["repository"]
                        if "cache" in e:
                            extra["cache"] = e["cache"]
                        if "arches" in e:
                            extra["arches"] = e["arches"]
                        if "multilib" in e:
                            extra["multilib"] = e["multilib"]
                        data["data"]["components"]["rpms"]["packages"][p] = \
                            extra
                if self.components.rpms.filter:
                    data["data"]["components"]["rpms"]["filter"] = \
                        list(self.components.rpms.filter)
        return yaml.dump(data)

    def validate(self):
        """Performs an in-depth validation of the metadata instance.

        :rtype: bool
        :raises TypeError: If properties are holding data of incorrect type
        :raises ValueError: If properties are holding invalid data
        """
        if not isinstance(self.mdversion, int):
            raise TypeError("mdversion must be an integer")
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not isinstance(self.version, str):
            raise TypeError("version must be a string")
        if not isinstance(self.release, str):
            raise TypeError("release must be a string")
        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        if not isinstance(self.module_licenses, set):
            raise TypeError("module_licenses must be a set")
        for l in self.module_licenses:
            if not isinstance(l, str):
                raise TypeError("module_licenses must be a set of strings")
        if not isinstance(self.content_licenses, set):
            raise TypeError("content_licenses must be a set")
        for l in self.content_licenses:
            if not isinstance(l, str):
                raise TypeError("content_licenses must be a set of strings")
        if not isinstance(self.buildrequires, dict):
            raise TypeError("buildrequires must be a dictionary")
        for n, v in self.buildrequires.items():
            if not isinstance(n, str) or not isinstance(v, str):
                raise TypeError("buildrequires keys and values must be strings")
        if not isinstance(self.requires, dict):
            raise TypeError("requires must be a dictionary")
        for n, v in self.requires.items():
            if not isinstance(n, str) or not isinstance(v, str):
                raise TypeError("requires keys and values must be strings")
        if not isinstance(self.community, str):
            raise TypeError("community must be a string")
        if not isinstance(self.documentation, str):
            raise TypeError("documentation must be a string")
        if not isinstance(self.tracker, str):
            raise TypeError("tracker must be a string")
        if not isinstance(self.xmd, dict):
            raise TypeError("xmd must be a dictionary")
        if not isinstance(self.profiles, dict):
            raise TypeError("profiles must be a dictionary")
        for p in self.profiles.keys():
            if not isinstance(p, str):
                raise TypeError("profiles keys must be strings")
            if not isinstance(self.profiles[p], ModuleProfile):
                raise TypeError("profiles values must be instances of ModuleProfile")
            if not isinstance(self.profiles[p].rpms, set):
                raise TypeError("profile rpms must be sets")
            for ps in self.profiles[p].rpms:
                if not isinstance(ps, str):
                    raise TypeError("profile rpms must be sets of strings")
        if not isinstance(self.components, ModuleComponents):
            raise TypeError("components must be an instance of ModuleComponents")
        if self.components.rpms:
            if not isinstance(self.components.rpms, ModuleRPMs):
                raise TypeError("rpms must be an instance of ModuleRPMs")
            if not isinstance(self.components.rpms.dependencies, bool):
                raise TypeError("rpms.dependencies must be a boolean")
            if not isinstance(self.components.rpms.api, set):
                raise TypeError("rpms.api must be a set")
            for a in self.components.rpms.api:
                if not isinstance(a, str):
                    raise TypeError("rpms.api must be a set of strings")
            if not isinstance(self.components.rpms.filter, set):
                raise TypeError("rpms.filter must be a set")
            for a in self.components.rpms.filter:
                if not isinstance(a, str):
                    raise TypeError("rpms.filter must be a set of strings")
            if self.components.rpms.packages:
                if not isinstance(self.components.rpms.packages, dict):
                    raise TypeError("rpms.packages must be a dictionary")
                for p, e in self.components.rpms.packages.items():
                    if not isinstance(p, str):
                        raise TypeError("rpms.packages keys must be strings")
                    if not isinstance(e, dict):
                        raise TypeError("rpms.packages values must dictionaries")
                    for k, v in e.items():
                        if not isinstance(k, str):
                            raise TypeError("rpms extras keys must be strings")
                        if k == "rationale" and v:
                            if not isinstance(v, str):
                                raise TypeError("rpms rationale must be a string")
                        if k == "commit" and v:
                            if not isinstance(v, str):
                                raise TypeError("rpms commit must be a string")
                        if k == "repository" and v:
                            if not isinstance(v, str):
                                raise TypeError("rpms repository must be a string")
                        if k == "cache" and v:
                            if not isinstance(v, str):
                                raise TypeError("rpms cache must be a string")
                        if k == "arches" and v:
                            if not isinstance(v, list):
                                raise TypeError("rpms arches must be a list")
                            for s in v:
                                if not isinstance(s, str):
                                    raise TypeError("arches must be a list of strings")
                        if k == "multilib" and v:
                            if not isinstance(v, list):
                                raise TypeError("rpms multilib must be a list")
                            for s in v:
                                if not isinstance(s, str):
                                    raise TypeError("multilib must be a list of strings")
        if not self.name:
            raise ValueError("name is required")
        if not self.version:
            raise ValueError("version is required")
        if not self.release:
            raise ValueError("release is required")
        if not self.summary:
            raise ValueError("summary is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.module_licenses:
            raise ValueError("at least one module license is required")
        if self.components.rpms:
            for p, e in self.components.rpms.packages.items():
                if not "rationale" in e:
                    raise ValueError(p, "has no rationale")
        # TODO: Validate dependency version formats
        return True

    @property
    def mdversion(self):
        """An int property representing the metadata format version used.

        This is automatically set to the highest supported version for
        new objects or set by the loaded document.  This value can be
        changed to one of the supported_mdversions to alter the output
        format.
        """
        return self._mdversion

    @mdversion.setter
    def mdversion(self, i):
        if i not in supported_mdversions:
            raise ValueError("Unsupported metadata version")
        self._mdversion = int(i)

    @property
    def name(self):
        """A string property representing the name of the module."""
        return self._name

    @name.setter
    def name(self, s):
        self._name = str(s)

    @property
    def version(self):
        """A string property representing the version of the module."""
        return self._version

    @version.setter
    def version(self, s):
        self._version = str(s)

    @property
    def release(self):
        """A string property representing the release of the module."""
        return self._release

    @release.setter
    def release(self, s):
        self._release = str(s)

    @property
    def summary(self):
        """A string property representing a short summary of the module."""
        return self._summary

    @summary.setter
    def summary(self, s):
        self._summary = str(s)

    @property
    def description(self):
        """A string property representing a detailed description of the
        module."""
        return self._description

    @description.setter
    def description(self, s):
        self._description = str(s)

    @property
    def module_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module itself."""
        return self._module_licenses

    @module_licenses.setter
    def module_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("module_licenses requires a set")
        self._module_licenses = set([str(x) for x in ss])

    def add_module_license(self, s):
        """Adds a module license to the set.

        :param str s: License name
        """
        self._module_licenses.add(str(s))

    def del_module_license(self, s):
        """Removes the supplied license from the module licenses set.

        :param str s: License name
        """
        self._module_licenses.discard(str(s))

    def clear_module_licenses(self):
        """Clears the module licenses set."""
        self._module_licenses.clear()

    @property
    def content_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module contents."""
        return self._content_licenses

    @content_licenses.setter
    def content_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("content_licenses requires a set")
        self._content_licenses = set([str(x) for x in ss])

    def add_content_license(self, s):
        """Adds a content license to the set.

        :param str s: License name
        """
        self._content_licenses.add(str(s))

    def del_content_license(self, s):
        """Removes the supplied license from the content licenses set.

        :param str s: License name
        """
        self._content_licenses.discard(str(s))

    def clear_content_licenses(self):
        """Clears the content licenses set."""
        self._content_licenses.clear()

    @property
    def requires(self):
        """A dictionary property representing the required dependencies of
        the module.

        Keys are the required module names (strings), values are their
        mininum required versions (also strings).
        """
        return self._requires

    @requires.setter
    def requires(self, d):
        if d and not isinstance(d, dict):
            raise TypeError("Incorrect data type passed for requires")
        self._requires = { str(k) : str(v) for k, v in d.items() }

    def add_requires(self, n, v):
        """Adds a required module dependency.

        :param str n: Required module name
        :param str v: Required module version
        """
        self._requires[str(n)] = str(v)

    update_requires = add_requires

    def del_requires(self, n):
        """Deletes the dependency on the supplied module.

        :param str n: Required module name
        """
        if str(n) in self._requires:
            del self._requires[str(n)]

    def clear_requires(self):
        """Removes all required runtime dependencies."""
        self._requires = dict()

    @property
    def buildrequires(self):
        """A dictionary property representing the required build dependencies
        of the module.

        Keys are the required module names (strings), values are their
        minimum required versions (also strings).
        """
        return self._buildrequires

    @buildrequires.setter
    def buildrequires(self, d):
        if d and not isinstance(d, dict):
            raise TypeError("Incorrect data type passed for buildrequires")
        self._buildrequires = { str(k) : str(v) for k, v in d.items() }

    def add_buildrequires(self, n, v):
        """Adds a module build dependency.

        :param str n: Required module name
        :param str v: Required module version
        """
        self._buildrequires[str(n)] = str(v)

    update_buildrequires = add_buildrequires

    def del_buildrequires(self, n):
        """Deletes the build dependency on the supplied module.

        :param str n: Required module name
        """
        if str(n) in self._buildrequires:
            del self._buildrequires[str(n)]

    def clear_buildrequires(self):
        """Removes all build dependencies."""
        self._buildrequires = dict()

    @property
    def community(self):
        """A string property representing a link to the upstream community
        for this module."""
        return self._community

    @community.setter
    def community(self, s):
        self._community = str(s)

    @property
    def documentation(self):
        """A string property representing a link to the upstream
        documentation for this module."""
        return self._documentation

    @documentation.setter
    def documentation(self, s):
        self._documentation = str(s)

    @property
    def tracker(self):
        """A string property representing a link to the upstream bug tracker
        for this module."""
        return self._tracker

    @tracker.setter
    def tracker(self, s):
        self._tracker = str(s)

    @property
    def xmd(self):
        """A dictionary property containing user-defined data."""
        return self._xmd

    @xmd.setter
    def xmd(self, d):
        if d and not isinstance(d, dict):
            raise TypeError("Incorrect data supplied for xmd")
        self._xmd = d

    @property
    def profiles(self):
        """A dictionary property representing the module profiles."""
        return self._profiles

    @profiles.setter
    def profiles(self, o):
        if not isinstance(o, dict):
            raise TypeError("Incorrect data types passed for profiles")
        self._profiles = o

    @property
    def components(self):
        """A ModuleComponents instance property representing the components
        defining the module."""
        return self._components

    @components.setter
    def components(self, o):
        if o and not isinstance(o, ModuleComponents):
            raise TypeError("Incorrect data type passed for components")
        self._components = o
