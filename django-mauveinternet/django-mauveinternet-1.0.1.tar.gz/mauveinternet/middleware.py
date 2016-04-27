from django.conf import settings


class MessageMiddleware(object):
    """Monkey-patches request.user to add a write_message() method.

    The corresponding Request Context Processor is
    mauveinternet.context_processors.messages
    """
    def process_request(self, request):
        session = request.session
        def write_message(message):
            try:
                session['messages'].append(message)
            except KeyError:
                session['messages'] = [message]
        request.user.write_message = write_message


class ContentTypeMiddleware(object):
    """Negotiates for XHTML, and converts XHTML to HTML if
    that is necessary.

    The conversion is done with regular"""

    def __init__(self):
        import re
        self.DOCTYPE_RE = re.compile(r'<!DOCTYPE[^>]*>')
        self.XMLNS_RE = re.compile(r'\s+xmlns(:[\w-]+)?\s*=\s*".*?"')
        self.EMPTY_TAG_RE = re.compile(r'\s*/>')
        self.LANG_RE = re.compile(r'xml:lang="')

    def process_response(self, request, response):
        if not response['Content-Type'].startswith('application/xhtml+xml'):
            return response

        if getattr(settings, 'FORCE_HTML', False) or 'application/xhtml+xml' not in request.META.get('HTTP_ACCEPT', ''):
            self.convert_to_html(response)

        return response

    def convert_to_html(self, response):
        content = self.DOCTYPE_RE.sub("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">""", response.content, 1)
        content = self.XMLNS_RE.sub('', content)
        content = self.EMPTY_TAG_RE.sub('>', content)
        content = self.LANG_RE.sub('lang="', content, 1)

        response['Content-Type']='text/html; charset=UTF-8'
        response.content = content
