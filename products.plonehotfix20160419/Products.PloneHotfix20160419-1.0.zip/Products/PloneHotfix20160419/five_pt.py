try:
    from five.pt.engine import Program
except ImportError:
    Program = None
if Program is not None:
    from Products.PageTemplates.Expressions import getEngine
    import logging
    import re

    logger = logging.getLogger('five.pt')

    # We need to patch.  Save the original.
    Program._original_cook = Program.cook

    @classmethod
    def _patched_cook(cls, source_file, text, engine, content_type):
        if engine is getEngine():
            # Same as in chameleon/parser.py, but without the leading '^' for
            # the beginning of the text.  And we explicitly look for python,
            # mostly to avoid matching '<?xml...'
            match_processing_instruction = re.compile(
                r'<\?python(?P<text>.*?)\?>', re.DOTALL)
            matches = match_processing_instruction.findall(text)
            if matches:
                for match in matches:
                    logger.warn('Ignored "<?python" expression %r in '
                                'Zope 2 page template at %s',
                                match, source_file)
                text = match_processing_instruction.sub('', text)
        return cls._original_cook(source_file, text, engine, content_type)

    Program.cook = _patched_cook
