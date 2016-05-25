# implements a few zone scanners..
import dns

from . import exceptions

class Scanner:
    names = ['@', '*', 'www', 'forum', 'secure', 'mail',
             'git', 'corp', 'localhost', 'autodiscover']

    def __init__(self, checker):
        self.checker = checker
        self.domain = checker.domain

    def _check_name(self, name, rdtype):
        try:
            res = self.checker.query_relative(name, rdtype)
        except exceptions.BadRcode as e:
            if 'NXDOMAIN' in e.args:
                return
        except exceptions.NoAnswer:
            return

        yield res.rrset

        cname = [a for a in res.response.answer if
                 a.rdtype == dns.rdatatype.CNAME and
                 a.name.is_subdomain(dns.name.from_text(self.domain))]

        for rrset in cname:
            yield rrset

    def check_name(self, name):
        for res in self._check_name(name, 'A'):
            yield res

        if name == '@':
            for rdtype in ('AAAA', 'NS', 'MX', 'LOC', 'SPF', 'TXT'):
                for res in self._check_name(name, rdtype):
                    yield res

    def __iter__(self):
        for name in self.names:
            res = self.check_name(name)
            for rr in res:
                yield rr
            else:
                continue
            if name == '*':
                break

        for name in ('_xmpp._tcp', '_sip._tcp'):
            for res in self._check_name(name, 'SRV'):
                yield res
