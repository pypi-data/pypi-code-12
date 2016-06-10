from trac.wiki.api import parse_args
from trac.wiki.macros import WikiMacroBase
from trac.ticket.query import Query
from trac.util.text import unicode_urlencode
from trac.wiki.formatter import system_message
from datetime import datetime


# 0.12 stores timestamps as microseconds. Pre-0.12 stores as seconds.
from trac.util.datefmt import utc
try:
    from trac.util.datefmt import from_utimestamp as from_timestamp
except ImportError:
    def from_timestamp(ts):
        return datetime.fromtimestamp(ts, utc)


def execute_query(env, req, query_args):
    # set maximum number of returned tickets to 0 to get all tickets at once
    query_args['max'] = 0
    # urlencode the args, converting back a few vital exceptions:
    # see the authorized fields in the query language in
    # http://trac.edgewall.org/wiki/TracQuery#QueryLanguage
    query_string = unicode_urlencode(query_args).replace('%21=', '!=') \
                                                .replace('%21%7E=', '!~=') \
                                                .replace('%7E=', '~=') \
                                                .replace('%5E=', '^=') \
                                                .replace('%24=', '$=') \
                                                .replace('%21%5E=', '!^=') \
                                                .replace('%21%24=', '!$=') \
                                                .replace('%7C', '|') \
                                                .replace('+', ' ') \
                                                .replace('%23', '#') \
                                                .replace('%28', '(') \
                                                .replace('%29', ')')
    env.log.debug("query_string: %s", query_string)
    query = Query.from_string(env, query_string)

    tickets = query.execute(req)

    tickets = [t for t in tickets
               if ('TICKET_VIEW' or 'TICKET_VIEW_CC')
               in req.perm('ticket', t['id'])]

    return tickets


class TotalField(WikiMacroBase):
    """Calculates the sum of a field values for the queried tickets.

    The macro accepts a field_name and a comma-separated list of query parameters for the ticket selection,
    in the form "key=value" as specified in TracQuery#QueryLanguage.

    Example:
    {{{
        [[TotalField(field_name, milestone=Sprint 1)]]
    }}}
    """

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        args, options = parse_args(content, strict=False)
        if len(args) != 1:
            return system_message("TotalField macro error", "request and field_name are required.")


        # we have to add custom field to query so that field is added to
        # resulting ticket list
        field_name = args[0]
        options[field_name + "!"] = None

        tickets = execute_query(self.env, req, options)

        sum = 0.0
        for t in tickets:
            try:
                sum += float(t[field_name])
            except:
                pass

        return "%g" % round(sum, 2)
