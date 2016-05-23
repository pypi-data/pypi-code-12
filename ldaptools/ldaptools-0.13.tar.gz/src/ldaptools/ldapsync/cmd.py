import argparse
import sys

import ldap.sasl

from ldaptools import ldif_utils, paged, ldap_source
from ldaptools.synchronize import Synchronize


def source_uri(value):
    for prefix in ['ldapi://', 'ldap://', 'ldaps://']:
        if value.startswith(prefix):
            return value
    raise argparse.ArgumentTypeError('%r is not an LDAP url' % value)


def or_type(f1, f2):
    def f(value):
        try:
            return f1(value)
        except argparse.ArgumentTypeError, e1:
            try:
                return f2(value)
            except argparse.ArgumentTypeError, e2:
                raise argparse.ArgumentTypeError('%s and %s' % (e1.args[0], e2.args[0]))
    return f


def object_class_pivot(value):
    value = filter(None, map(str.strip, map(str.lower, value.split())))
    if len(value) != 2:
        raise argparse.ArgumentTypeError('%r is not a pair of an objectClass and an attribute name')
    return value


def main(args=None):
    parser = argparse.ArgumentParser(description='''\
Synchronize an LDIF file or a source LDAP directory to another directory

Base DN of the source is remapped to another DN in the target directory''')
    parser.add_argument('--object-class-pivot',
                        required=True,
                        type=object_class_pivot,
                        action='append',
                        help='an objectClass and an attribute name which is the unique identifier '
                        'for this class')
    parser.add_argument('--attributes-file',
                        type=argparse.FileType('r'),
                        help='a file containing the list of attributes to synchronize')
    parser.add_argument('--attributes',
                        help='a list of attribute names separated by spaces')
    parser.add_argument('--source-uri',
                        required=True,
                        type=or_type(source_uri, argparse.FileType('r')),
                        help='URL of an LDAP directory (ldapi://, ldap:// or ldaps://) or path of '
                        'and LDIF file')
    parser.add_argument('--case-insensitive-attribute',
                        action='append',
                        help='indicate that the attribute must be compared case insensitively')
    parser.add_argument('--source-base-dn',
                        required=True,
                        help='base DN of the source')
    parser.add_argument('--source-bind-dn',
                        help='bind DN for a source LDAP directory')
    parser.add_argument('--source-bind-password',
                        help='bind password for a source LDAP directory')
    parser.add_argument('--source-filter',
                        help='filter to apply to a source LDAP directory')

    parser.add_argument('--target-uri',
                        type=source_uri,
                        required=True,
                        help='URL of the target LDAP directory')
    parser.add_argument('--target-base-dn',
                        required=True,
                        help='base DN of the target LDAP directory')
    parser.add_argument('--target-bind-dn',
                        help='bind DN for a target LDAP directory')
    parser.add_argument('--target-bind-password',
                        help='bind password for a target LDAP directory')
    parser.add_argument('--fake',
                        action='store_true',
                        help='compute synchronization actions but do not apply')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='print all actions to stdout')

    options = parser.parse_args(args=args)

    attributes = set()

    if options.attributes_file:
        attributes.update([attribute.strip().lower() for attribute in options.attributes_file])
    if options.attributes:
        for attribute in options.attributes.split():
            attribute = attribute.strip().lower()
            if attribute:
                attributes.add(attribute)
    attributes = list(attributes)
    if not attributes:
        parser.print_help()
        print 'Yout must give at least one attribute to synchronize'

    if options.verbose:
        print 'Synchronizing ',
    if hasattr(options.source_uri, 'read'):
        if options.verbose:
            print options.source_uri.name,
        source = ldif_utils.ListLDIFParser(options.source_uri)
        source.parse()
    else:
        if options.verbose:
            print options.source_uri,
        conn = paged.PagedLDAPObject(options.source_uri)
        if options.source_uri.startswith('ldapi://'):
            conn.sasl_interactive_bind_s("", ldap.sasl.external())
        elif options.source_bind_dn and options.source_bind_password:
            conn.simple_bind_s(options.source_bind_dn, options.source_bind_password)

        source = ldap_source.LDAPSource(conn, base_dn=options.source_base_dn, attributes=attributes,
                                       filterstr=options.source_filter)

    if options.verbose:
        print 'to', options.target_uri
    target_conn = paged.PagedLDAPObject(options.target_uri)
    if options.target_uri.startswith('ldapi://'):
        target_conn.sasl_interactive_bind_s("", ldap.sasl.external())
    elif options.target_bind_dn and options.target_bind_dn:
        target_conn.simple_bind_s(options.target_bind_dn, options.target_bind_password)
    synchronize = Synchronize(source, options.source_base_dn,
                              target_conn, options.target_base_dn,
                              pivot_attributes=options.object_class_pivot,
                              attributes=attributes,
                              case_insensitive_attribute=options.case_insensitive_attribute)

    synchronize.build_actions()
    if options.verbose:
        for action in synchronize.actions:
            print ' -', action
        if not synchronize.actions:
            print 'Nothing to do.'
    if not options.fake:
        synchronize.apply_actions()
    failed_actions = [action for action in synchronize.actions if action.errors]
    if failed_actions:
        print >>sys.stderr, 'Some actions failed:'
        for action in failed_actions:
            print ' -', action
            for error in action.errors:
                print '  *', error
        raise SystemExit(1)
