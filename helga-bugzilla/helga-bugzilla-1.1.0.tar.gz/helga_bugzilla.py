from txbugzilla import connect
from twisted.internet import defer
import re
from helga.plugins import match
from helga import log, settings

logger = log.getLogger(__name__)


def match_tickets(message):
    tickets = []

    pattern = re.compile(r"""
       (?:               # Prefix to trigger the plugin:
            bzs?         #   "bz" or "bzs"
          | bugs?        #   "bug" or "bugs"
          | bugzilla?    #   "bugzilla" or "bugzillas"
       )                 #
       \s*               #
       [#]?[0-9]+        # Number, optionally preceded by "#"
       (?:               # The following pattern will match zero or more times:
          ,?             #   Optional comma
          \s+            #
          (?:and\s+)?    #   Optional "and "
          [#]?[0-9]+     #   Number, optionally preceded by "#"
       )*
       """, re.VERBOSE | re.IGNORECASE)
    for bzmatch in re.findall(pattern, message):
        for ticket in re.findall(r'[0-9]+', bzmatch):
            tickets.append(ticket)
    return tickets


@match(match_tickets, priority=0)
def helga_bugzilla(client, channel, nick, message, matches):
    """
    Match possible Bugzilla tickets, return links and summary info
    """
    connect_args = {}
    if hasattr(settings, 'BUGZILLA_XMLRPC_URL'):
        connect_args['url'] = settings.BUGZILLA_XMLRPC_URL
    d = connect(**connect_args)

    d.addCallback(get_summaries, matches, client, channel)
    d.addErrback(send_err, client, channel)
    # TODO: make this second callback not fire, if errback was called.
    d.addCallback(send_message, client, channel, nick)
    d.addErrback(send_err, client, channel)


@defer.inlineCallbacks
def get_summaries(bz, matches, client, channel):
    bugs = yield bz.get_bugs_summaries(matches)
    defer.returnValue(bugs)


def construct_message(bugs, nick):
    """
    Return a string about a nick and a list of tickets' URLs and summaries.
    """
    msgs = []
    for bug in bugs:
        if hasattr(settings, 'BUGZILLA_TICKET_URL'):
            url = settings.BUGZILLA_TICKET_URL % {'ticket': bug.id}
        else:
            url = bug.weburl
        msgs.append('%s [%s]' % (url, bug.summary))
    if len(msgs) == 1:
        msg = msgs[0]
    else:
        msg = "{} and {}".format(", ".join(msgs[:-1]), msgs[-1])
    return '%s might be talking about %s' % (nick, msg)


def send_message(bugs, client, channel, nick):
    if bugs is not None:
        msg = construct_message(bugs, nick)
        client.msg(channel, msg)


def send_err(e, client, channel):
    client.msg(channel, str(e.value))
