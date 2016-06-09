
import os, re, sys, subprocess, tempfile
from bf.text import Text

class Schema(Text):

    def __init__(self, fn, **args):
        """relaxng schema initialization.
        fn = the schema filename (required)
        """
        Text.__init__(self, fn=fn, **args)

    def trang(self, ext='.rng'):
        """use trang to create a schema with the given format extension
        SIDE EFFECT: creates a new file on the filesystem."""
        from . import JARS
        trang_jar = os.path.join(JARS, 'trang.jar')
        outfn = os.path.splitext(self.fn)[0] + ext
        stderr = tempfile.NamedTemporaryFile()
        try:
            result = subprocess.check_call(
                ["java", "-jar", trang_jar, self.fn, outfn],
                universal_newlines=True,
                stderr=stderr)
        except subprocess.CalledProcessError as e:
            f = open(stderr.name, 'r+b')
            output = f.read(); f.close()
            raise RuntimeError(str(output, 'utf-8')).with_traceback(sys.exc_info()[2]) from None
        if result==0:
            return outfn
    
    @classmethod
    def from_tag(cls, tag, schemas, ext='.rnc'):
        """load a schema using an element's tag. schemas can be a string or a list of strings"""
        return cls(fn=cls.filename(tag, schemas, ext=ext))

    @classmethod
    def filename(cls, tag, schemas, ext='.rnc'):
        """given a tag and a list of schemas, return the filename of the schema.
        If schemas is a string, treat it as a comma-separated list.
        """
        if type(schemas)==str: 
            schemas = re.split("\s*,\s*", schemas)
        for schema in schemas:
            fn = os.path.join(schema, cls.dirname(tag), cls.basename(tag, ext=ext))
            if os.path.exists(fn):
                return fn

    @classmethod
    def dirname(cls, namespace):
        """convert a namespace url to a directory name. 
            Also accepts an Element 'tag' with namespace prepended in {braces}."""
        md = re.match("^\{?(?:[^:]+:/{0,2})?([^\}]+)\}?", namespace)
        if md is not None:
            dirname = re.sub("[/:\.]", '_', md.group(1))
        else:
            dirname = ''
        return dirname

    @classmethod
    def basename(cls, tag, ext='.rnc'):
        return re.sub("\{[^\}]*\}", "", tag) + ext
