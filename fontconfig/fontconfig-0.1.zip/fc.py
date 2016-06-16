# -*- test-case-name: test_fc -*-
# Copyright (c) 2016 Marco Giusti
# See LICENSE for details.


from __future__ import print_function


__author__ = "Marco Giusti"
__version__ = "0.1"


import enum
from _fontconfig import ffi as _ffi
from _fontconfig import lib as _lib


class FcError(Exception):
    pass


class FtError(FcError):
    pass


class SetName(enum.IntEnum):
    system = _lib.FcSetSystem
    application = _lib.FcSetApplication


class MatchKind(enum.IntEnum):
    pattern = _lib.FcMatchPattern
    font = _lib.FcMatchFont
    scan = _lib.FcMatchScan


class FcTypes(enum.IntEnum):
    unknown = _lib.FcTypeUnknown
    void = _lib.FcTypeVoid
    integer = _lib.FcTypeInteger
    double = _lib.FcTypeDouble
    string = _lib.FcTypeString
    bool = _lib.FcTypeBool
    matrix = _lib.FcTypeMatrix
    charset = _lib.FcTypeCharSet
    ftface = _lib.FcTypeFTFace
    langset = _lib.FcTypeLangSet
    # convinient aliases
    int = _lib.FcTypeInteger
    str = _lib.FcTypeString
    float = _lib.FcTypeDouble


class PropertyName(enum.Enum):

    family = "family"
    style = "style"
    slant = "slant"
    weight = "weight"
    size = "size"
    aspect = "aspect"
    pixel_size = "pixelsize"
    spacing = "spacing"
    foundry = "foundry"
    antialias = "antialias"
    hinting = "hinting"
    hint_style = "hintstyle"
    vertical_layout = "verticallayout"
    autohint = "autohint"
    global_advance = "globaladvance"
    width = "width"
    file = "file"
    index = "index"
    ft_face = "ftface"
    rasterizer = "rasterizer"
    outline = "outline"
    scalable = "scalable"
    color = "color"
    scale = "scale"
    symbol = "symbol"
    dpi = "dpi"
    rgba = "rgba"
    minspace = "minspace"
    source = "source"
    charset = "charset"
    lang = "lang"
    fontversion = "fontversion"
    fullname = "fullname"
    familylang = "familylang"
    stylelang = "stylelang"
    fullnamelang = "fullnamelang"
    capability = "capability"
    fontformat = "fontformat"
    embolden = "embolden"
    embedded_bitmap = "embeddedbitmap"
    decorative = "decorative"
    lcd_filter = "lcdfilter"
    font_features = "fontfeatures"
    namelang = "namelang"
    prgname = "prgname"
    hash = "hash"
    postscript_name = "postscriptname"


def _fc_assert(ok, msg=None):
    if not ok:
        if msg is not None:
            raise FcError(msg)
        raise FcError()


def init_load_config():
    """
    Loads the default configuration file and returns the resulting
    configuration. Does not load any font information.

    :raises FcError:
    """

    fcconfig = _lib.FcInitLoadConfig()
    _fc_assert(fcconfig)
    return FcConfig(fcconfig)


def init_load_config_and_fonts():
    """
    Loads the default configuration file and builds information about the
    available fonts. Returns the resulting configuration.

    :raises FcError:
    """

    fcconfig = _lib.FcInitLoadConfigAndFonts()
    _fc_assert(fcconfig)
    return FcConfig(fcconfig)


def init():
    """
    Loads the default configuration file and the fonts referenced therein and
    sets the default configuration to that result. If the default configuration
    has already been loaded, this routine does nothing.

    :raises FcError:
    """

    _fc_assert(_lib.FcInit())


def fini():
    """
    Frees all data structures allocated by previous calls to fontconfig
    functions. Fontconfig returns to an uninitialized state, requiring a new
    call to one of the init* functions before any other fontconfig function may
    be called.
    """

    _lib.FcFini()


def get_version():
    """
    Returns the version number of the library in the form of:
    tuple(major, minor, revision)
    """

    version = _lib.FcGetVersion()
    major = version / 10000
    minor = (version % 10000) / 100
    revision = (version % 1000) % 100
    return (major, minor, revision)


def init_reinitialize():
    """
    Forces the default configuration file to be reloaded and resets the default
    configuration. Raises FcError if the configuration cannot be reloaded (due
    to configuration file errors, allocation failures or other issues) and
    leaves the existing configuration unchanged.

    :raises FcError:
    """

    _fc_assert(_lib.FcInitReinitialize())


def init_bring_up_to_date():
    """
    Checks the rescan interval in the default configuration, checking the
    configuration if the interval has passed and reloading the configuration if
    when any changes are detected. Raises FcError if the configuration cannot
    be reloaded (see init_reinitialize).

    :raises FcError:
    """

    _fc_assert(_lib.FcInitBringUptoDate())


def _get_obj(prop):
    assert isinstance(prop, (str, PropertyName))
    if isinstance(prop, str):
        try:
            prop = PropertyName[prop]
        except KeyError:
            raise TypeError(prop)
    return prop.value


class FcPattern(object):
    """
    Holds a set of names with associated value lists; each name refers to a
    property of a font. ``FcPattern``\ s are used as inputs to the matching
    code as well as holding information about specific fonts. Each property can
    hold one or more values; conventionally all of the same type, although the
    interface doesn't demand that.
    """

    _destroy = _lib.FcPatternDestroy

    @classmethod
    def name_parse(cls, name):
        """
        Converts name from the standard text format described above into a
        pattern.

        @type name: str
        :raises FcError:
        """

        fcpattern = _lib.FcNameParse(_ffi.new("const FcChar8 []", name))
        _fc_assert(fcpattern)
        return cls(fcpattern, _borrowed=False)

    @classmethod
    def build(cls, objects):
        """
        Builds a pattern using a list of (object, value). Each value to
        be entered in the pattern is specified with two arguments:

        1. Object name, a string describing the property to be added.

        2. Value, as passed to any of the FcPattern.add_<type>
           functions.

        Example::

            >>> pattern = FcPattern.build([("family", "Times")])
        """

        args = []
        for name, value in objects:
            name = _get_obj(name)
            args.append(_ffi.new("char []", name))
            typename = type(value).__name__
            try:
                args.append(_ffi.cast("int", FcTypes[typename]))
            except KeyError:
                raise TypeError("invalid object of type %s" % typename)
            if isinstance(value, str):
                args.append(_ffi.new("char []", value))
            elif isinstance(value, bool):
                args.append(_ffi.cast("bool", value))
            elif isinstance(value, int):
                args.append(_ffi.cast("int", value))
            elif isinstance(value, float):
                args.append(_ffi.cast("double", value))
            else:
                raise TypeError()
        args.append(_ffi.NULL)
        fcpattern = _lib.FcPatternBuild(_ffi.NULL, *args)
        _fc_assert(fcpattern)
        return cls(fcpattern, _borrowed=False)

    def __new__(cls, fcpattern=None, _borrowed=True):
        self = super(FcPattern, cls).__new__(cls)
        if fcpattern is None:
            fcpattern = _lib.FcPatternCreate()
            _fc_assert(fcpattern)
        elif _borrowed:
            _lib.FcPatternReference(fcpattern)
        self._fcpattern = fcpattern
        return self

    def __del__(self):
        self._destroy(self._fcpattern)

    def __eq__(self, other):
        if not isinstance(other, FcPattern):
            return NotImplemented
        return bool(_lib.FcPatternEqual(self._fcpattern, other._fcpattern))

    def __hash__(self):
        h = _lib.FcPatternHash(self._fcpattern)
        return int(_ffi.cast("unsigned int", h))

    def __copy__(self):
        """
        Copy this pattern, returning a new pattern that matches this
        one. Each pattern may be modified without affecting the other.
        """

        fcpattern = _lib.FcPatternDuplicate(self._fcpattern)
        _fc_assert(fcpattern)
        return self.__class__(fcpattern, _borrowed=False)

    def __format__(self, format_spec):
        """
        Converts given pattern into text described by the format
        specifier ``format_spec``.

        The format is loosely modeled after printf-style format string.
        The format string is composed of zero or more directives:
        ordinary characters (not "%"), which are copied unchanged to the
        output stream; and tags which are interpreted to construct text
        from the pattern in a variety of ways (explained below). Special
        characters can be escaped using backslash. C-string style
        special characters like \\n and \\r are also supported (this is
        useful when the format string is not a C string literal). It is
        advisable to always escape curly braces that are meant to be
        copied to the output as ordinary characters.

        Each tag is introduced by the character "%", followed by an
        optional minimum field width, followed by tag contents in curly
        braces ({}). If the minimum field width value is provided the
        tag will be expanded and the result padded to achieve the
        minimum width. If the minimum field width is positive, the
        padding will right-align the text. Negative field width will
        left-align. The rest of this section describes various supported
        tag contents and their expansion.

        A _simple_ tag is one where the content is an identifier. When
        simple tags are expanded, the named identifier will be looked up
        in *pattern* and the resulting list of values returned, joined
        together using comma. For example, to print the family name and
        style of the pattern, use the format "%{family} %{style}\\n". To
        extend the family column to forty characters use
        "%-40{family}%{style}\\n".

        Simple tags expand to list of all values for an element. To only
        choose one of the values, one can index using the syntax
        "%{elt[idx]}". For example, to get the first family name only,
        use "%{family[0]}".

        If a simple tag ends with "=" and the element is found in the
        pattern, the name of the element followed by "=" will be output
        before the list of values. For example, "%{weight=}" may expand
        to the string "weight=80". Or to the empty string if *pattern*
        does not have weight set.

        If a simple tag starts with ":" and the element is found in the
        pattern, ":" will be printed first. For example, combining this
        with the =, the format "%{:weight=}" may expand to ":weight=80"
        or to the empty string if *pattern* does not have weight set.

        If a simple tag contains the string ":-", the rest of the the
        tag contents will be used as a default string. The default
        string is output if the element is not found in the pattern. For
        example, the format "%{:weight=:-123}" may expand to
        ":weight=80" or to the string ":weight=123" if *pattern* does
        not have weight set.

        A *count* tag is one that starts with the character "#" followed
        by an element name, and expands to the number of values for the
        element in the pattern. For example, "%{#family}" expands to the
        number of family names *pattern* has set, which may be zero.

        A *sub-expression* tag is one that expands a sub-expression. The
        tag contents are the sub-expression to expand placed inside
        another set of curly braces.  Sub-expression tags are useful for
        aligning an entire sub-expression, or to apply converters
        (explained later) to the entire sub-expression output. For
        example, the format "%40{{%{family} %{style}}}" expands the
        sub-expression to construct the family name followed by the
        style, then takes the entire string and pads it on the left to
        be at least forty characters.

        A *filter-out* tag is one starting with the character "-" followed
        by a comma-separated list of element names, followed by a
        sub-expression enclosed in curly braces.  The sub-expression
        will be expanded but with a pattern that has the listed elements
        removed from it. For example, the format
        "%{-size,pixelsize{sub-expr}}" will expand "sub-expr" with
        *pattern* sans the size and pixelsize elements.

        A *filter-in* tag is one starting with the character "+" followed
        by a comma-separated list of element names, followed by a
        sub-expression enclosed in curly braces.  The sub-expression
        will be expanded but with a pattern that only has the listed
        elements from the surrounding pattern. For example, the format
        "%{+family,familylang{sub-expr}}" will expand "sub-expr" with a
        sub-pattern consisting only the family and family lang elements
        of *pattern*.

        A *conditional* tag is one starting with the character "?"
        followed by a comma-separated list of element conditions,
        followed by two sub-expression enclosed in curly braces. An
        element condition can be an element name, in which case it tests
        whether the element is defined in pattern, or the character "!"
        followed by an element name, in which case the test is negated.
        The conditional passes if all the element conditions pass. The
        tag expands the first sub-expression if the conditional passes,
        and expands the second sub-expression otherwise. For example,
        the format "%{?size,dpi,!pixelsize{pass}{fail}}" will expand to
        "pass" if *pattern* has size and dpi elements but no pixelsize
        element, and to "fail" otherwise.

        An *enumerate* tag is one starting with the string "[]" followed
        by a comma-separated list of element names, followed by a
        sub-expression enclosed in curly braces. The list of values for
        the named elements are walked in parallel and the sub-expression
        expanded each time with a pattern just having a single value for
        those elements, starting from the first value and continuing as
        long as any of those elements has a value. For example, the
        format "%{[]family,familylang{%{family} (%{familylang})\\n}}"
        will expand the pattern "%{family} (%{familylang})\\n" with a
        pattern having only the first value of the family and familylang
        elements, then expands it with the second values, then the
        third, etc.

        As a special case, if an enumerate tag has only one element, and
        that element has only one value in the pattern, and that value
        is of type FcLangSet, the individual languages in the language
        set are enumerated.

        A *builtin* tag is one starting with the character "=" followed
        by a builtin name. The following builtins are defined:

        **unparse**

            Expands to the result of calling FcNameUnparse() on the
            pattern.

        **fcmatch**

            Expands to the output of the default output format of the
            fc-match command on the pattern, without the final newline.

        **fclist**

            Expands to the output of the default output format of the
            fc-list command on the pattern, without the final newline.

        **fccat**

            Expands to the output of the default output format of the
            fc-cat command on the pattern, without the final newline.

        **pkgkit**

            Expands to the list of PackageKit font() tags for the
            pattern.  Currently this includes tags for each family name,
            and each language from the pattern, enumerated and sanitized
            into a set of tags terminated by newline. Package management
            systems can use these tags to tag their packages
            accordingly.

        For example, the format "%{+family,style{%{=unparse}}}\\n" will
        expand to an unparsed name containing only the family and style
        element values from *pattern*.

        The contents of any tag can be followed by a set of zero or more
        *converters*. A converter is specified by the character "|"
        followed by the converter name and arguments. The following
        converters are defined:

        **basename**

            Replaces text with the results of calling FcStrBasename() on
            it.

        **dirname**

            Replaces text with the results of calling FcStrDirname() on
            it.

        **downcase**

            Replaces text with the results of calling FcStrDowncase() on
            it.

        **shescape**

            Escapes text for one level of shell expansion. (Escapes
            single-quotes, also encloses text in single-quotes.)

        **cescape**

            Escapes text such that it can be used as part of a C string
            literal. (Escapes backslash and double-quotes.)

        **xmlescape**

            Escapes text such that it can be used in XML and HTML.
            (Escapes less-than, greater-than, and ampersand.)

        **delete(chars)**

            Deletes all occurrences of each of the characters in *chars*
            from the text. FIXME: This converter is not UTF-8 aware yet.

        **escape(chars)**

            Escapes all occurrences of each of the characters in *chars*
            by prepending it by the first character in chars. FIXME:
            This converter is not UTF-8 aware yet.

        **translate(from,to)**

            Translates all occurrences of each of the characters in
            *from* by replacing them with their corresponding character
            in *to*. If *to* has fewer characters than *from*, it will
            be extended by repeating its last character. FIXME: This
            converter is not UTF-8 aware yet.

        For example, the format "%{family|downcase|delete( )}\\n" will
        expand to the values of the family element in *pattern*,
        lower-cased and with spaces removed.
        """

        carr = _lib.FcPatternFormat(self._fcpattern, format_spec)
        s = _ffi.string(carr)
        _lib.free(carr)
        return s

    def name_unparse(self):
        """
        Converts the given pattern into the standard text format described
        above.
        """

        name = _lib.FcNameUnparse(self._fcpattern)
        s = _ffi.string(name)
        _lib.free(name)
        return s

    def substitute(self):
        """
        Supplies default values for underspecified font patterns:

        * Patterns without a specified style or weight are set to Medium

        * Patterns without a specified style or slant are set to Roman

        * Patterns without a specified pixel size are given one computed from
          any specified point size (default 12), dpi (default 75) and scale
          (default 1).
        """

        _lib.FcDefaultSubstitute(self._fcpattern)

    def equal_subset(self, other, properties):
        """
        Returns whether ``self`` and ``other`` have exactly the same values for
        all of the objects in ``properties``.
        """

        assert isinstance(other, FcPattern)
        os = _FcObjectSet(properties)  # pay attention to ref count
        return bool(_lib.FcPatternEqualSubset(self._fcpattern,
                                              other._fcpattern,
                                              os._fcobjectset))

    def filter(self, properties):
        """
        Returns a new pattern that only has those objects from self that
        are in ``properties``. If properties is ``None``, a duplicate of
        self is returned.
        """

        if properties is not None:
            os = _FcObjectSet(properties)  # pay attention to ref count
            fcpattern = _lib.FcPatternFilter(self._fcpattern, os._fcobjectset)
        else:
            fcpattern = _lib.FcPatternFilter(self._fcpattern, _ffi.NULL)
        _fc_assert(fcpattern)
        return self.__class__(fcpattern, True)

    def del_property(self, obj):
        """
        Deletes all values associated with the property ``obj``, returning
        whether the property existed or not.
        """

        return bool(_lib.FcPatternDel(self._fcpattern, obj))

    def remove(self, obj, pos):
        """
        Removes the value associated with the property ``obj`` at position
        ``pos``, returning whether the property existed and had a value at that
        position or not.
        """

        return bool(_lib.FcPatternRemove(self._fcpattern, obj, pos))

    def _get_value(self, getter, obj, n, v):
        res = getter(self._fcpattern, obj, n, v)
        err = _ffi.string(_ffi.cast("FcResult", res))
        _fc_assert(res == _lib.FcResultMatch, err)
        return v[0]

    def add_integer(self, prop, i):
        """
        Adds an integet to the list of values associated with the property
        named ``obj``.
        """

        obj = _get_obj(prop)
        _fc_assert(_lib.FcPatternAddInteger(self._fcpattern, obj, i))

    def get_integer(self, prop, n):
        """
        Returns the ``n``\ 'th value associated with the property ``obj``.

        :raises FcError:
        """

        i = _ffi.new("int *")
        obj = _get_obj(prop)
        return self._get_value(_lib.FcPatternGetInteger, obj, n, i)

    def add_double(self, prop, d):
        """
        Adds a double to the list of values associated with the property
        named ``obj``.
        """

        obj = _get_obj(prop)
        _fc_assert(_lib.FcPatternAddDouble(self._fcpattern, obj, d))

    def get_double(self, prop, n):
        """
        Returns the ``n``\ 'th value associated with the property ``obj``.

        :raises FcError:
        """

        d = _ffi.new("double *")
        obj = _get_obj(prop)
        return self._get_value(_lib.FcPatternGetDouble, obj, n, d)

    def add_string(self, prop, s):
        """
        Adds a string to the list of values associated with the property
        named ``obj``.
        """

        obj = _get_obj(prop)
        _fc_assert(_lib.FcPatternAddString(self._fcpattern, obj, s))

    def get_string(self, prop, n):
        """
        Returns the ``n``\ 'th value associated with the property ``obj``.

        :raises FcError:
        """

        s = _ffi.new("FcChar8 **")
        obj = _get_obj(prop)
        r = self._get_value(_lib.FcPatternGetString, obj, n, s)
        return _ffi.string(r)

    def add_bool(self, prop, b):
        """
        Adds a boolean to the list of values associated with the property
        named ``obj``.
        """

        obj = _get_obj(prop)
        _fc_assert(_lib.FcPatternAddBool(self._fcpattern, obj, b))

    def get_bool(self, prop, n):
        """
        Returns the ``n``\ 'th value associated with the property ``obj``.

        :raises FcError:
        """

        b = _ffi.new("FcBool *")
        obj = _get_obj(prop)
        return self._get_value(_lib.FcPatternGetBool, obj, n, b)

    # def add_matrix(self, obj, m):
    #     pass

    # def add_charSet(self, obj, c):
    #     pass

    # def add_fTFace(self, obj, f):
    #     pass

    # def add_langSet(self, obj, l):
    #     pass

    def _print(self):
        _lib.FcPatternPrint(self._fcpattern)


class _FcFontSet(object):
    """
    An ``_FcFontSet`` simply holds a list of :py:class:`FcPattern`; these are
    used to return the results of listing available fonts.
    """

    _destroy = _lib.FcFontSetDestroy

    def __init__(self, fcfontset):
        self._fcfontset = fcfontset

    def __getitem__(self, i):
        if 0 <= i < len(self):
            return FcPattern(self._fcfontset.fonts[i])
        raise IndexError("index out of range")

    def __len__(self):
        return self._fcfontset.nfont

    def add(self, font):
        """
        Adds a pattern to a font set. Note that the pattern is not
        copied before being inserted into the set. Raises FcError if the
        pattern cannot be inserted into the set (due to allocation
        failure).
        """

        assert isinstance(font, FcPattern)
        _fc_assert(_lib.FcFontSetAdd(self._fcfontset, font._fcpattern))

    def _print(self):
        _lib.FcFontSetPrint(self._fcfontset)


def FcFontSet(_fset):
    return list(_FcFontSet(_fset))


class _FcObjectSet(object):

    _destroy = _lib.FcObjectSetDestroy

    def __new__(cls, args):
        self = super(_FcObjectSet, cls).__new__(cls)
        cargs = []
        for arg in args:
            value = _get_obj(arg)
            cargs.append(_ffi.new("char[]", value))
        self._fcobjectset = _lib.FcObjectSetBuild(*(cargs + [_ffi.NULL]))
        _fc_assert(self._fcobjectset)
        return self

    def __del__(self):
        self._destroy(self._fcobjectset)


def _strlist(fcstrlist):
    return list(_iter_FcStrList(fcstrlist))


def _iter_FcStrList(fcstrlist):
    _fc_assert(fcstrlist)
    try:
        while True:
            s = _lib.FcStrListNext(fcstrlist)
            if not s:
                return
            yield _ffi.string(s)
    finally:
        _lib.FcStrListDone(fcstrlist)


class FcConfig(object):
    """
    Holds a complete configuration of the library; there is one default
    configuration, other can be constructed from XML data structures. FcConfig
    objects hold two sets of fonts, the first contains those specified by the
    configuration, the second set holds those added by the application at
    run-time. Interfaces that need to reference a particular set use one of the
    FcSetName enumerated values.
    """

    _destroy = _lib.FcConfigDestroy

    @staticmethod
    def home():
        """
        Return the current user's home directory, if it is available, and if
        using it is enabled, and None otherwise. See also enable_home.
        """

        ret = _lib.FcConfigHome()
        if ret:
            return _ffi.string(ret)
        return None

    @staticmethod
    def enable_home(enable):
        """
        If enable is True, then Fontconfig will use various files which are
        specified relative to the user's home directory (using the ~ notation
        in the configuration). When enable is False, then all use of the home
        directory in these contexts will be disabled. The previous setting of
        the value is returned.
        """

        return bool(_lib.FcConfigEnableHome(bool(enable)))

    @classmethod
    def get_current(cls):
        """Returns the current default configuration.

        :raises FcError:
        """

        fcconfig = _lib.FcConfigGetCurrent()
        _fc_assert(fcconfig)
        return cls(fcconfig)

    def __new__(cls, fcconfig=None):
        self = super(FcConfig, cls).__new__(cls)
        if fcconfig is None:
            fcconfig = _lib.FcConfigCreate()
            _fc_assert(fcconfig)
        else:
            _lib.FcConfigReference(fcconfig)
        self._fcconfig = fcconfig
        return self

    def __del__(self):
        self._destroy(self._fcconfig)

    def __eq__(self, other):
        if not isinstance(other, FcConfig):
            return NotImplemented
        return self._fcconfig == other._fcconfig

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_current(self):
        """
        Sets this config as the current default configuration. Implicitly calls
        build_fonts if necessary.

        :raises FcError:
        """

        _fc_assert(_lib.FcConfigSetCurrent(self._fcconfig))

    def up_to_date(self):
        """
        Checks all of the files related to config and returns whether any of
        them has been modified since the configuration was created.
        """

        return bool(_lib.FcConfigUptoDate(self._fcconfig))

    def build_fonts(self):
        """
        Builds the set of available fonts for the given configuration.
        Note that any changes to the configuration after this call have
        indeterminate effects. Raises FcError if this operation runs out
        of memory.

        :raises FcError:
        """

        _fc_assert(_lib.FcConfigBuildFonts(self._fcconfig))

    def get_config_dirs(self):
        """
        Returns the list of font directories specified in the configuration
        files for this config. Does not include any subdirectories.
        """

        return _strlist(_lib.FcConfigGetConfigDirs(self._fcconfig))

    def get_font_dirs(self):
        """
        Returns the list of font directories in config. This includes the
        configured font directories along with any directories below those in
        the filesystem.
        """

        return _strlist(_lib.FcConfigGetFontDirs(self._fcconfig))

    def get_config_files(self):
        """
        Returns the list of known configuration files used to generate config.
        """

        return _strlist(_lib.FcConfigGetConfigFiles(self._fcconfig))

    def get_cache_dirs(self):
        """
        Returns a string list containing all of the directories that fontconfig
        will search when attempting to load a cache file for a font directory.
        """

        return _strlist(_lib.FcConfigGetCacheDirs(self._fcconfig))

    def get_fonts(self, set_name):
        """
        Returns one of the two sets of fonts from the configuration as
        specified by set.

        :raises FcError:
        """

        fset = _lib.FcConfigGetFonts(self._fcconfig, set_name)
        _fc_assert(fset)
        return FcFontSet(fset)

    def get_blanks(self):
        """
        Returns the :class:`_FcBlanks` object associated with the given
        configuration, if no blanks were present in the configuration, this
        function will return None. The returned _FcBlanks object, is valid as
        long as the owning FcConfig is alive.
        """

        blanks = _lib.FcConfigGetBlanks(self._fcconfig)
        if not blanks:
            return None
        return _FcBlanks(blanks)

    def get_rescan_interval(self):
        """
        Returns the interval between automatic checks of the configuration (in
        seconds) specified in config. The configuration is checked during a
        call to FcFontList when this interval has passed since the last check.
        An interval setting of zero disables automatic checks.
        """

        return _lib.FcConfigGetRescanInterval(self._fcconfig)

    def set_rescan_interval(self, interval):
        """
        Sets the rescan interval. An interval setting of zero disables
        automatic checks.
        """

        ret = _lib.FcConfigSetRescanInterval(self._fcconfig, int(interval))
        _fc_assert(ret)

    def app_font_add_file(self, filename):
        """
        Adds an application-specific font to the configuration.

        :raises FcError:
        """

        _fc_assert(_lib.FcConfigAppFontAddFile(self._fcconfig, filename))

    def app_font_add_dir(self, dir):
        """
        Scans the specified directory for fonts, adding each one found to the
        application-specific set of fonts.
        """

        _fc_assert(_lib.FcConfigAppFontAddDir(self._fcconfig, dir))

    def app_font_clear(self):
        "Clears the set of application-specific fonts."

        _lib.FcConfigAppFontClear(self._fcconfig)

    def substitute_with_pattern(self, p, p_pat, kind):
        """
        Performs the sequence of pattern modification operations, if
        kind is MatchKind.pattern, then those tagged as pattern
        operations are applied, else if kind is MatchKind.font, those
        tagged as font operations are applied and p_pat is used for
        <test> elements with target=pattern. Raises FcError if the
        substitution cannot be performed (due to allocation failure).
        """

        assert isinstance(kind, MatchKind)
        if p_pat is None:
            p_pat = _ffi.NULL
        _fc_assert(_lib.FcConfigSubstituteWithPat(self._fcconfig, p, p_pat,
                                                  kind))

    def substitute(self, p, kind):
        """
        Calls substitute_with_pattern setting p_pat to None. Raises
        FcError if the substitution cannot be performed (due to
        allocation failure).

        :raises FcError:
        """

        assert isinstance(kind, MatchKind)
        _fc_assert(_lib.FcConfigSubstitute(self._fcconfig, p, kind))

    def font_list(self, pattern, properties):
        """
        Selects fonts matching pattern, creates patterns from those fonts
        containing only the objects in properties and returns the set of unique
        such patterns.

        :raises FcError:
        """

        assert isinstance(pattern, FcPattern)
        os = _FcObjectSet(properties)  # pay attention to ref count
        _fset = _lib.FcFontList(self._fcconfig, pattern._fcpattern,
                                os._fcobjectset)
        _fc_assert(_fset)
        return FcFontSet(_fset)


class _FcBlanks(object):
    """
    An _FcBlanks object holds a list of Unicode chars which are expected to be
    blank when drawn. When scanning new fonts, any glyphs which are empty and
    not in this list will be assumed to be broken and not placed in the
    FcCharSet associated with the font. This provides a significantly more
    accurate CharSet for applications.
    """

    def __init__(self, fcblanks):
        self._fcblanks = fcblanks


# FreeType specific functions

_ftlibrary = None


def get_freetype_library():
    global _ftlibrary
    if _ftlibrary is None:
        _ftlibrary = _ffi.new("FT_Library *")
        err = _lib.FT_Init_FreeType(_ftlibrary)
        if err:
            raise FtError(err)
    return _ftlibrary[0]


def done_freetype_library():
    global _ftlibrary
    if _ftlibrary is not None:
        _lib.FT_Done_FreeType(_ftlibrary[0])
        _ftlibrary = None


class _FtFace(object):

    @property
    def num_faces(self):
        return self._ftface[0].num_faces

    def __new__(cls, data, id=0, lib=None):
        self = super(_FtFace, cls).__new__(cls)
        if lib is None:
            lib = get_freetype_library()
        self._ftface = _ffi.new("FT_Face *")
        err = _lib.FT_New_Memory_Face(lib, data, len(data), id, self._ftface)
        if err:
            raise FtError(err)
        return self

    def __del__(self):
        _lib.FT_Done_Face(self._ftface[0])


def freetype_query(filename, id, blanks):
    """
    Constructs a :class:`FcPattern` representing the ``id``\ th font in
    ``filename``. Returns the number of fonts in ``filename`` and the pattern.
    """

    assert isinstance(blanks, _FcBlanks)
    count_p = _ffi.new("int *")
    pattern = _lib.FcFreeTypeQuery(filename, id, blanks._fcblanks, count_p)
    _fc_assert(pattern)
    return FcPattern(pattern), count_p[0]


def freetype_query_face(face, filename, id, blanks):
    """
    Constructs a pattern representing ``face``. ``filename`` and ``id`` are
    used solely as data for pattern elements (FC_FILE, FC_INDEX and sometimes
    FC_FAMILY).
    """

    assert isinstance(blanks, _FcBlanks)
    assert isinstance(face, _FtFace)
    ftface = face._ftface[0]
    pattern = _lib.FcFreeTypeQueryFace(ftface, filename, id, blanks._fcblanks)
    _fc_assert(pattern)
    return FcPattern(pattern)


def query_font(filename, data, id, blanks):
    # https://github.com/qtproject/qt/blob/4.8/src/gui/text/qfontdatabase_x11.cpp#L1749
    assert isinstance(blanks, _FcBlanks)
    if get_version() < (2, 4, 2) or not data:
        return freetype_query(filename, id, blanks)
    face = _FtFace(data, id)
    pattern = freetype_query_face(face, filename, id, blanks)
    return pattern, face.num_faces
