# Copyright (c) 2016 Marco Giusti
# See LICENSE for details.

from __future__ import print_function
import os
import sys
import unittest
import random
import tempfile
import errno
import os.path

import fc
fc.init()


FONT_PATH = os.path.abspath("SourceCodePro-Regular.otf")


def mkdtemp():
    parent = os.path.join(os.getcwd(), "_tests_temp")
    try:
        os.makedirs(parent)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    return tempfile.mkdtemp(dir=parent)


# XXX: Add support for other platforms?
@unittest.skipIf(not sys.platform.startswith("linux"), "Not a linux system")
class TestHome(unittest.TestCase):

    def setUp(self):
        self.oldhome = os.environ["HOME"]

    def tearDown(self):
        os.environ["HOME"] = self.oldhome

    def test_home(self):
        home = "/home/pippo"
        os.environ["HOME"] = home
        self.assertEqual(fc.FcConfig.home(), home)

    def test_home_null(self):
        del os.environ["HOME"]
        self.assertIs(fc.FcConfig.home(), None)

    def test_enable_home(self):
        old = fc.FcConfig.enable_home(False)
        self.assertFalse(fc.FcConfig.enable_home(old))
        self.assertEqual(fc.FcConfig.enable_home(old), old)

    def test_disable_home(self):
        old = fc.FcConfig.enable_home(False)
        self.addCleanup(lambda: fc.FcConfig.enable_home(old))
        self.assertIs(fc.FcConfig.home(), None)


class TestInit(unittest.TestCase):

    def test_init_load_config(self):
        cfg = fc.init_load_config()
        self.assertIsInstance(cfg, fc.FcConfig)

    def test_init_load_config_and_fonts(self):
        cfg = fc.init_load_config_and_fonts()
        self.assertIsInstance(cfg, fc.FcConfig)


class TestFcConfig(unittest.TestCase):

    def test_equality(self):
        "The two underlying objects are different."

        cfg1 = fc.FcConfig()
        cfg2 = fc.FcConfig()
        self.assertNotEqual(cfg1, cfg2)

    def test_equality_is_not_identity(self):
        cur1 = fc.FcConfig().get_current()
        cur2 = fc.FcConfig().get_current()
        self.assertIsNot(cur1, cur2)
        self.assertEqual(cur1, cur2)

    def test_get_current(self):
        self.assertIsInstance(fc.FcConfig.get_current(), fc.FcConfig)

    def test_set_current(self):
        old = fc.FcConfig.get_current()
        self.addCleanup(old.set_current)
        cfg = fc.FcConfig()
        cfg.set_current()
        self.assertEqual(cfg, fc.FcConfig.get_current())
        self.assertIsNot(cfg, fc.FcConfig.get_current())

    def test_up_to_date(self):
        "We did not make any change, it should be updated."

        self.assertTrue(fc.FcConfig.get_current().up_to_date())

    def test_get_config_dirs_empty(self):
        "No dirs added."

        self.assertEqual(fc.FcConfig().get_config_dirs(), [])

    def test_get_font_dirs(self):
        self.assertEqual(fc.FcConfig().get_font_dirs(), [])

    def test_get_config_files(self):
        self.assertEqual(fc.FcConfig().get_config_files(), [])

    def test_cache_dirs(self):
        self.assertEqual(fc.FcConfig().get_cache_dirs(), [])

    def test_get_fonts_applications(self):
        "No fonts are returned."

        cfg = fc.FcConfig()
        self.assertRaises(fc.FcError, cfg.get_fonts, fc.SetName.application)
        cfg.app_font_add_file(":/non-existent")
        self.assertEqual(list(cfg.get_fonts(fc.SetName.application)), [])

    def test_rescan_interval(self):
        cfg = fc.FcConfig()
        old = cfg.get_rescan_interval()
        self.addCleanup(lambda: cfg.set_rescan_interval(old))
        interval = random.randint(1, 1000)
        cfg.set_rescan_interval(interval)
        self.assertEqual(cfg.get_rescan_interval(), interval)

    def test_app_font_add_file(self):
        cfg = fc.FcConfig()
        cfg.app_font_add_file(FONT_PATH)
        fonts = cfg.get_fonts(fc.SetName.application)
        self.assertEqual(len(fonts), 1)
        self.assertIsInstance(fonts[0], fc.FcPattern)

    def test_app_font_clear(self):
        cfg = fc.FcConfig()
        cfg.app_font_add_file(FONT_PATH)
        self.assertIsInstance(cfg.get_fonts(fc.SetName.application), list)
        cfg.app_font_clear()
        self.assertRaises(fc.FcError, cfg.get_fonts, fc.SetName.application)

    def test_get_blanks_null(self):
        cfg = fc.FcConfig()
        self.assertIs(cfg.get_blanks(), None)

    def test_get_fcpattern_memory(self):
        import gc
        gc.disable()
        self.addCleanup(gc.enable)
        config = fc.FcConfig.get_current()
        config.get_fonts(fc.SetName.system)
        gc.collect(2)


class TestFcPattern(unittest.TestCase):

    def test_add_integer(self):
        p = fc.FcPattern()
        p.add_integer("weight", 42)
        self.assertEqual(p.get_integer("weight", 0), 42)

    def test_add_double(self):
        p = fc.FcPattern()
        p.add_double("size", 42.0)
        self.assertEqual(p.get_double("size", 0), 42.0)

    def test_add_string(self):
        p = fc.FcPattern()
        p.add_string("family", "quarantadue")
        self.assertEqual(p.get_string("family", 0), "quarantadue")

    def test_add_bool(self):
        p = fc.FcPattern()
        p.add_bool("antialias", True)
        self.assertEqual(p.get_bool("antialias", 0), True)

    def test_add_mismatch(self):
        p = fc.FcPattern()
        self.assertRaises(TypeError, p.add_integer, "family", 42.0)

    def test_get_mismatch(self):
        p = fc.FcPattern()
        p.add_integer("weight", 42)
        with self.assertRaisesRegexp(fc.FcError, "FcResultTypeMismatch"):
            p.get_string("weight", 0)

    def test_get_no_match(self):
        p = fc.FcPattern()
        with self.assertRaisesRegexp(fc.FcError, "FcResultNoMatch"):
            p.get_integer("family", 0)

    def test_get_no_id(self):
        p = fc.FcPattern()
        p.add_integer("weight", 42)
        with self.assertRaisesRegexp(fc.FcError, "FcResultNoId"):
            p.get_integer("weight", 1)

    def test_integet_get_double(self):
        p = fc.FcPattern()
        p.add_integer("weight", 42)
        self.assertIsInstance(p.get_double("weight", 0), float)

    def test_double_get_integet(self):
        p = fc.FcPattern()
        p.add_double("weight", 42.0)
        self.assertIsInstance(p.get_integer("weight", 0), int)

    def test_remove(self):
        p = fc.FcPattern()
        p.add_double("weight", 42.0)
        p.add_integer("weight", 42)
        p.remove("weight", 1)
        with self.assertRaisesRegexp(fc.FcError, "FcResultNoId"):
            p.get_integer("weight", 1)
        self.assertEqual(p.get_double("weight", 0), 42.0)

    def test_del_property(self):
        p = fc.FcPattern()
        p.add_double("weight", 42.0)
        p.add_integer("weight", 42)
        self.assertTrue(p.del_property("weight"))
        with self.assertRaisesRegexp(fc.FcError, "FcResultNoMatch"):
            p.get_double("weight", 0)

    def test_del_property_empty(self):
        p = fc.FcPattern()
        self.assertFalse(p.del_property("family"))

    def test_build(self):
        p = fc.FcPattern.build([("family", "Times")])
        self.assertEqual(p.get_string("family", 0), "Times")

    def test_build_invalid_type(self):
        self.assertRaises(TypeError, fc.FcPattern.build,
                          [("family", object())])

    def test_build_property_name(self):
        p = fc.FcPattern.build([(fc.PropertyName.family, "Times")])
        self.assertEqual(p.get_string("family", 0), "Times")

    def test_copy(self):
        import copy

        p1 = fc.FcPattern.build([(fc.PropertyName.family, "Times")])
        p2 = copy.copy(p1)
        self.assertEqual(p1, p2)
        self.assertIsNot(p1, p2)
        p2.add_string("lang", "en")
        self.assertNotEqual(p1, p2)

    def test_substitute(self):
        p1 = fc.FcPattern()
        p2 = fc.FcPattern()
        self.assertEqual(p1, p2)
        p1.substitute()
        self.assertNotEqual(p1, p2)
        self.assertEqual(p1.get_integer(fc.PropertyName.weight, 0), 100)
        self.assertEqual(p1.get_integer(fc.PropertyName.slant, 0), 0)
        self.assertEqual(p1.get_integer(fc.PropertyName.size, 0), 12.0)
        self.assertEqual(p1.get_integer(fc.PropertyName.dpi, 0), 75.0)
        self.assertEqual(p1.get_integer(fc.PropertyName.scale, 0), 1.0)

    def test_equal_subset(self):
        p1 = fc.FcPattern.build([(fc.PropertyName.family, "Times"),
                                 (fc.PropertyName.slant, 0)])
        p2 = fc.FcPattern.build([(fc.PropertyName.family, "Times"),
                                 (fc.PropertyName.slant, 100)])
        self.assertTrue(p1.equal_subset(p2, [fc.PropertyName.family]))
        self.assertFalse(p1.equal_subset(p2, [fc.PropertyName.slant]))

    def test_filter(self):
        p1 = fc.FcPattern.build([(fc.PropertyName.family, "Times"),
                                 (fc.PropertyName.slant, 0)])
        p2 = p1.filter([fc.PropertyName.family])
        self.assertEqual(p2.get_string(fc.PropertyName.family, 0), "Times")

    def test_filter_duplicate(self):
        p1 = fc.FcPattern.build([(fc.PropertyName.family, "Times"),
                                 (fc.PropertyName.slant, 0)])
        p2 = p1.filter(None)
        self.assertEqual(p1, p2)
        self.assertIsNot(p1._fcpattern, p2._fcpattern)


class TestPatternFormat(unittest.TestCase):

    def setUp(self):
        blanks = fc.FcConfig.get_current().get_blanks()
        self.pattern, _ = fc.freetype_query(FONT_PATH, 0, blanks)

    def test_simple(self):
        s = "{0:%{{family}} %{{style}}}".format(self.pattern)
        self.assertEqual(s, "Source Code Pro Regular")

    def test_extend(self):
        s = "{0:%-20{{family}}%{{style}}}".format(self.pattern)
        self.assertEqual(s, "Source Code Pro     Regular")

    def test_one_value(self):
        # not really useful, but the font does not have any multiple property
        s = "{0:%{{family[0]}}}".format(self.pattern)
        self.assertEqual(s, "Source Code Pro")

    def test_name(self):
        s = "{0:%{{family=}}}".format(self.pattern)
        self.assertEqual(s, "family=Source Code Pro")

    def test_empty_name(self):
        s = "{0:%{{size=}}}".format(self.pattern)
        self.assertEqual(s, "")

    def test_column(self):
        s = "{0:%{{:family=}}}".format(self.pattern)
        self.assertEqual(s, ":family=Source Code Pro")

    def test_column_empty(self):
        s = "{0:%{{:size=}}}".format(self.pattern)
        self.assertEqual(s, "")

    def test_default_string(self):
        s = "{0:%{{:size=:-42}}}".format(self.pattern)
        self.assertEqual(s, ":size=42")

    def test_count(self):
        s = "{0:%{{#family}}}".format(self.pattern)
        self.assertEqual(s, "1")

    def test_sub_expression(self):
        # please don't do it
        s = "{0:%40{{{{%{{family}} %{{style}}}}}}}".format(self.pattern)
        self.assertEqual(s, "                 Source Code Pro Regular")

    def test_filter_out(self):
        # boom
        s = "{0:%{{-size,pixelsize{{%{{family}}}}}}}".format(self.pattern)
        self.assertEqual(s, "Source Code Pro")

    @unittest.skip("Cannot understand the format")
    def test_filter_in(self):
        s = "{0:%{{+size,pixelsize{{%{{family}}}}}}}".format(self.pattern)
        self.assertEqual(s, "Source Code Pro")

    # XXX: do more tests


class TestFreeType(unittest.TestCase):

    def test_query(self):
        blanks = fc.FcConfig.get_current().get_blanks()
        pat, count = fc.freetype_query(FONT_PATH, 0, blanks)
        self.assertEqual(count, 1)
        self.assertEqual(pat.get_string("family", 0), "Source Code Pro")

    def test_query_face(self):
        ID = 0
        with open(FONT_PATH) as fp:
            data = fp.read()
        blanks = fc.FcConfig.get_current().get_blanks()
        face = fc._FtFace(data, ID)
        pat = fc.freetype_query_face(face, FONT_PATH, ID, blanks)
        self.assertEqual(pat.get_string("family", 0), "Source Code Pro")

    def test_query_font(self):
        blanks = fc.FcConfig.get_current().get_blanks()
        with open(FONT_PATH) as fp:
            data = fp.read()
        pat, _ = fc.query_font(FONT_PATH, data, 0, blanks)
        self.assertEqual(pat.get_string("family", 0), "Source Code Pro")
