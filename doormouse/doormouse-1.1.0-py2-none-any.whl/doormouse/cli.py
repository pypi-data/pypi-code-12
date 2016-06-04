#!/usr/bin/env python
"""Doormouse command line client."""
import sys, os.path
import argparse
import prettytable

from . import Doormouse, DoormouseError
from .filestore import FileStore
from .datastore import DataStore
from . import conf


VERSION = "1.0.0"
PROGNAME = "doormouse"
DEFAULT_CONF = """
{
    "ca": [
        {
            "nickname": "root",
            "cn": "Test Root",
            "cert": [
                {"nickname": "server", "o":"Test Servers"}
            ]
        }
    ]
}
"""


def exitmsg(msg):
    """Exits the program with the given error message."""
    sys.stderr.write("error: {}\n".format(msg))
    sys.exit(2)


def create_parser():
    """Returns a parser object."""
    parser = argparse.ArgumentParser(prog=PROGNAME, description="Doormouse Manager", version=VERSION)
    parser.add_argument("-c", metavar="conf", dest="conf", help="specify a different conf file")
    subparser = parser.add_subparsers(dest="command", help="command")

    init_parser = subparser.add_parser("initialize", help="initialze anchors and store")

    list_parser = subparser.add_parser("list", help="list certificates")
    list_parser.add_argument("issuer_nickname", default=None, nargs="?", metavar="NICKNAME", help="restrict to issuer")

    cre_parser = subparser.add_parser("create", help="create a key and sign the certificate")
    cre_parser.add_argument("cert_nickname", metavar="NICKNAME", help="the nickname of the cert profile")
    cre_parser.add_argument("cn", metavar="COMMON_NAME", help="comman name (hostname) of the certificate")
    cre_parser.add_argument("alt", default=[], nargs="*", metavar="ALT_NAMES",
        help="altername names (hostnames) of the certificate")

    sign_parser = subparser.add_parser("sign", help="sign a certificate request")
    sign_parser.add_argument("cert_nickname", metavar="CERT_NICKNAME", help="the nickname of the cert profile")
    sign_parser.add_argument("request_filename", metavar="REQUEST_FILENAME", help="certificate request filename")

    track_parser = subparser.add_parser("import", help="import a certificate signed by someone else")
    track_parser.add_argument("certfile", metavar="CERTFILE", help="certificate filename")

    forget_parser = subparser.add_parser("forget", help="remove a certificate from the database")
    forget_parser.add_argument("serial", metavar="SERIAL_NUMBER", help="serial number of certificate to forget")

    warn_parser = subparser.add_parser("warn", help="print a warning about expiring certificates or revocation lists")
    warn_parser.add_argument("days", default=30, nargs="?", type=int, help="days till expiration")

    revoke_parser = subparser.add_parser("revoke", help="manage revocation lists")
    revoke_sub_parser = revoke_parser.add_subparsers(dest="subcommand", help="subcommand")

    revoke_list_parser = revoke_sub_parser.add_parser("list", help="list revoked certificates")
    revoke_list_parser.add_argument("issuer_nickname", default=None, nargs="?", metavar="ISSUER_NICKNAME",
        help="restrict to anchor")

    revoke_refresh_parser = revoke_sub_parser.add_parser("refresh", help="refresh the revocation list expiration")
    revoke_refresh_parser.add_argument("issuer_nickname", default=None, nargs="?", metavar="ISSUER_NICKNAME",
        help="restrict to anchor")

    revoke_cert_parser = revoke_sub_parser.add_parser("certificate", help="revoke a certificate")
    revoke_cert_parser.add_argument("serial", metavar="SERIAL_NUMBER", help="serial number of certificate to revoke")

    export_parser = subparser.add_parser("export", help="export a certificate and possibly a key from database")
    export_parser.add_argument("-k", "--include-key", action="store_true", help="(danger!) include the private key")
    export_parser.add_argument("-c", "--include-chain", action="store_true", help="include the CA Chain")
    export_parser.add_argument("-o", "--outfile", metavar="OUTPUT_FILENAME", required=False, help="the name of the file to export the data")
    export_parser.add_argument("serial", metavar="SERIAL_NUMBER", help="serial number of certificate to export")
    

    return parser


def print_certificates(certs):
    """Prints a table of certificates."""
    # if there are no certs, dont print anything
    if len(certs) == 0:
        return

    # create the table and formatting
    table = prettytable.PrettyTable(["Type", "Issuer Nickname", "Profile Nickname", "Common Name", "Status",
        "Serial Number"])
    table.border = False
    table.header_style = "upper"
    table.align = "l"

    # add the certs to the table and print
    for cert in certs:
        table.add_row([cert["cert_type"], cert["issuer_nickname"], cert["profile_nickname"], cert["subject_cn"],
            cert["status"], cert["serial_number"]])
    print table


def print_revoked(certs):
    """Prints a table of revoked certificates."""
    # if there are no certs, dont print anything
    if len(certs) == 0:
        return

    # create the table and formatting
    table = prettytable.PrettyTable(["Issuer Nickname", "Profile Nickname", "Common Name", "Serial Number"])
    table.border = False
    table.header_style = "upper"
    table.align = "l"

    for cert in certs:
        table.add_row([cert["issuer_nickname"], cert["profile_nickname"], cert["subject_cn"], cert["serial_number"]])

    print table


def print_expiring(certs):
    """Prints a table of expiring certificates."""
    # if there are no certs, dont print anything
    if len(certs) == 0:
        return

    # create the table and formatting
    table = prettytable.PrettyTable(["Profile Nickname", "Common Name", "Serial Number", "Days Till Expire"])
    table.border = False
    table.header_style = "upper"
    table.align = "l"

    for cert in certs:
        table.add_row([cert["profile_nickname"], cert["subject_cn"], cert["serial_number"], cert["days_till_expire"]])

    print table

def export_certificate(datastore, serial, path, include_private, include_chain):
    cert = datastore.get_certificate(serial)

    if cert is None:
        raise Exception('Certificate with serial %s not found.' % serial)
    else:
        if cert['cert_type'] == 'cert':
            if path is None:
                path = "./%s.pem" % serial
            homedir = os.path.expanduser('~')
            data_out = ''
        
            if include_private:
                path_key  = '%s/.doormouse/cert/%s/key_%s.pem' % (homedir, cert['issuer_nickname'], cert['serial_number'])
                data_key  = open(path_key, 'r').read()
                data_out += data_key
            
            path_cert = '%s/.doormouse/cert/%s/cert_%s.pem' % (homedir, cert['issuer_nickname'], cert['serial_number'])
            data_cert = open(path_cert, 'r').read()
            data_out += data_cert
        
            if include_chain:
                ca        = datastore.get_issuer(cert['issuer_nickname'])
                path_ca   = '%s/.doormouse/ca/%s/ca_%s.pem' % (homedir, cert['issuer_nickname'], cert['issuer_nickname'])
                data_ca   = open(path_ca, 'r').read()
                data_out += data_ca
            
                current = ca
                while current['issuer_nickname'] != current['profile_nickname']:
                    next_ca   = datastore.get_issuer(current['issuer_nickname'])
                    next_path = '%s/.doormouse/ca/%s/ca_%s.pem' % (homedir, next_ca['issuer_nickname'], next_ca['issuer_nickname'])
                    next_data = open(next_path, 'r').read()
                    data_out += next_data
                
                    current = next_ca
                
        
            outfile = open(path, 'w')
            outfile.write(data_out)
            outfile.close()
            print 'Writing export to %s...' % path
        else:
            print 'Export CA cert not allowed'
        

def main():
    """Runs the program."""
    # parse the command line args
    parser = create_parser()
    args = parser.parse_args()

    # setup the default locations and files
    rootdir = os.path.join(os.path.expanduser("~"), ".doormouse")
    dbpath = os.path.join(rootdir, "datastore.db")
    if args.conf:
        confpath = args.conf
    else:
        confpath = os.path.join(rootdir, "doormouse.conf")

    # initialize filestore
    filestore = FileStore(rootdir)
    try:
        filestore.initialize_store()
    except DoormouseError as exc:
        exitmsg(exc.message)

    # prepare the conf file if necessary
    if not os.path.isfile(confpath):
        print "warning: conf file not found, creating a default one"
        try:
            with open(confpath, "w") as cfile:
                cfile.write(DEFAULT_CONF)
        except IOError as exc:
            exitmsg("unable to write a default conf file at '{}': {}".format(confpath, exc.strerror))

    # initialize datastore
    datastore = DataStore(dbpath, confpath)
    try:
        datastore.initialize_store()
        conf_str = datastore.load_conf_str()
    except DoormouseError as exc:
        exitmsg(exc.message)

    # finally initialize doormouse
    doormouse = Doormouse(filestore, datastore)

    # parse the conf string
    try:
        cnf = conf.parse(conf_str)
    except ValueError:
        exitmsg("unable to parse conf file")

    # run the command
    if args.command == "initialize":
        doormouse.initialize_issuers(cnf)

    elif args.command == "list":
        try:
            print_certificates(doormouse.list_certificates(cnf, args.issuer_nickname))
        except ValueError as exc:
            exitmsg(exc.message)

    elif args.command == "create":
        try:
            doormouse.create_cert(cnf, args.cert_nickname, args.cn, args.alt)
        except ValueError as exc:
            exitmsg(exc.message)

    elif args.command == "sign":
        try:
            doormouse.sign(cnf, args.cert_nickname, args.request_filename)
        except ValueError as exc:
            exitmsg(exc.message)

    elif args.command == "import":
        try:
            doormouse.track(cnf, args.certfile)
        except ValueError as exc:
            exitmsg(exc.message)

    elif args.command == "forget":
        try:
            doormouse.remove_certificate(cnf, args.serial)
        except ValueError as exc:
            exitmsg(exc.message)

    elif args.command == "warn":
        print_expiring(doormouse.list_expiring(cnf, args.days))

    elif args.command == "revoke":
        if args.subcommand == "list":
            try:
                print_revoked(doormouse.list_revoked(cnf, args.issuer_nickname))
            except ValueError as exc:
                exitmsg(exc.message)

        elif args.subcommand == "refresh":
            try:
                doormouse.refresh_crl(cnf, args.issuer_nickname)
            except ValueError as exc:
                exitmsg(exc.message)

        elif args.subcommand == "certificate":
            try:
                doormouse.revoke_certificate(cnf, args.serial)
            except ValueError as exc:
                exitmsg(exc.message)

        else:
            exitmsg("unknown revoke command: {}".format(args.subcommand))
    elif args.command == "export":
        try:
            export_certificate(datastore, args.serial, args.outfile, args.include_key, args.include_chain)
        
        except ValueError as exc:
            exitmsg(exc.message)
                
    else:
        exitmsg("unknown command: {}".format(args.command))


if __name__ == "__main__":
    main()
