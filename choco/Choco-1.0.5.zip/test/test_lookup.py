from choco.template import Template
from choco import lookup, errors, runtime
from choco.util import FastEncodingBuffer
from choco import compat
from test.util import flatten_result, result_lines
from test import eq_
import unittest
import os

from test import TemplateTest, template_base, module_base, ui_template_base, assert_raises_message

tl = lookup.TemplateLookup(directories=[template_base])
class LookupTest(unittest.TestCase):
    def test_basic(self):
        t = tl.get_template('index.html')
        assert result_lines(t.render()) == [
            "this is index"
        ]
    def test_subdir(self):
        t = tl.get_template('/subdir/index.html')
        assert result_lines(t.render()) == [
            "this is sub index",
            "this is include 2"

        ]

        assert tl.get_template('/subdir/index.html').module_id \
                            == '_subdir_index_html'

    def test_updir(self):
        t = tl.get_template('/subdir/foo/../bar/../index.html')
        assert result_lines(t.render()) == [
            "this is sub index",
            "this is include 2"

        ]

    def test_directory_lookup(self):
        """test that hitting an existent directory still raises
        LookupError."""

        self.assertRaises(errors.TopLevelLookupException,
            tl.get_template, "/subdir"
        )

    def test_no_lookup(self):
        t = Template("hi <%include file='foo.html'/>")
        try:
            t.render()
            assert False
        except errors.TemplateLookupException:
            eq_(
                str(compat.exception_as()),
            "Template 'memory:%s' has no TemplateLookup associated" % \
                            hex(id(t))
                )

    def test_uri_adjust(self):
        tl = lookup.TemplateLookup(directories=['/foo/bar'])
        assert tl.filename_to_uri('/foo/bar/etc/lala/index.html') == \
                        '/etc/lala/index.html'

        tl = lookup.TemplateLookup(directories=['./foo/bar'])
        assert tl.filename_to_uri('./foo/bar/etc/index.html') == \
                        '/etc/index.html'

    def test_uri_cache(self):
        """test that the _uri_cache dictionary is available"""
        tl._uri_cache[('foo', 'bar')] = '/some/path'
        assert tl._uri_cache[('foo', 'bar')] == '/some/path'

    def test_check_not_found(self):
        tl = lookup.TemplateLookup()
        tl.put_string("foo", "this is a template")
        f = tl.get_template("foo")
        assert f.uri in tl.collection
        f.filename = "nonexistent"
        self.assertRaises(errors.TemplateLookupException,
            tl.get_template, "foo"
        )
        assert f.uri not in tl.collection

    def test_dont_accept_relative_outside_of_root(self):
        """test the mechanics of an include where
        the include goes outside of the path"""
        tl = lookup.TemplateLookup(directories=[os.path.join(template_base, "subdir")])
        index = tl.get_template("index.html")

        ctx = runtime.Context(FastEncodingBuffer())
        ctx._with_template=index

        assert_raises_message(
            errors.TemplateLookupException,
           "Template uri \"../index.html\" is invalid - it "
            "cannot be relative outside of the root path",
            runtime._lookup_template, ctx, "../index.html", index.uri
        )

        assert_raises_message(
            errors.TemplateLookupException,
           "Template uri \"../othersubdir/foo.html\" is invalid - it "
            "cannot be relative outside of the root path",
            runtime._lookup_template, ctx, "../othersubdir/foo.html", index.uri
        )

        # this is OK since the .. cancels out
        t = runtime._lookup_template(ctx, "foo/../index.html", index.uri)



def create_ui_container():
    from choco.ui import UIContainer, UIModule
    ui_container = UIContainer([ui_template_base])

    class PostView(UIModule):

        default_template = "post.html"

        def render(self):
            return {
                "title": "'post name'"
            }
    ui_container.put_ui("PostView", PostView)
    return ui_container

tl2 = lookup.TemplateLookup(directories=[template_base], ui_container=create_ui_container())
class UILooupTest(unittest.TestCase):


    def test_ui(self):
        t = tl2.get_template("ui.html")
        assert result_lines(t.render()) == [
            "Test ui",
            "This is a post named 'post name'"

        ]


    def test_ui_not_found(self):
        t = tl2.get_template("ui_not_found.html")
        self.assertRaises(errors.UINotFoundException, t.render)
