#!/usr/bin/python

import os
import sys
import argparse

# The commandline hooks and parsers. Supported commands are:
#
# scry
#    start
#    stop
#    status
#    query
#    service
#    config
#    help
#
# The service command parses a secondary list of keywords:
#
# scry service
#    dir
#    list
#    search
#    install
#    disable
#    enable
#    remove
#    help


# Class Definitions
class SilentError(Exception): pass
class SilentArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise SilentError(message)
class Options(object):
    def __init__(self,**kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)



# Commandline Entrypoint
def cmd(args=None):
    parser     = SilentArgumentParser()

    commands = [('start'  , 'begin running SCRY',
                 'Start running SCRY. Listen to HTTP requests using the configured port and settings.'),
                ('stop'   , 'end running SCRY',
                 'Stop running SCRY, by sending a shutdown request to the configured port.'),
                ('status' , 'check if SCRY is currently running',
                 'Check if SCRY is currently running, by requesting the status page from the configured port.'),
                ('query'  , 'query SCRY directly, offline',
                 'Run an offline query with SCRY.'),
                ('service', 'see "scry service help"',
                 'Manage which services SCRY loads, and where from.'),
                ('config' , 'see "scry config help"',
                 'Configure where and how the SCRY app runs, and manage accessibility.'),
                ('help'   , 'show this help message and exit','')]
    
    service_cmds = [('dir',"change SCRY's working directory",
                     'Set a new directory in which SCRY looks for services and configuration, writes log files, etc.'),
                    ('list','list the services SCRY currently exposes',
                     'Print a list of services which SCRY 1) loads from its current working directory, 2) loads from elsewhere, and 3) does not load.'),
                    ('search','search PyPI for additional services',
                     'Query the Python Package Index for packages with the `Framework :: SCRY` trove classifier.'),
                    ('install','download new services from PyPI',
                     'Download and install new services from PyPI using pip. Automatically enable them unless told not to with `--no_add`.'),
                    ('disable','prevent a service from being loaded by SCRY',
                     "If the specified service(s) is in SCRY's working directory, add it to the no-load list. Otherwise, remove it from the remote-load list."),
                    ('enable','revert `scry service disable`, or load remote services',
                     "If the specified service(s) is in SCRY's working directory, remove it from the no-load list. Otherwise, add it to the remote-load list."),
                    ('remove','permanently remove a service - USE WITH CAUTION',
                     "If the specified service(s) is in SCRY's working directory, permanently delete the module. Otherwise, run `pip uninstall <service>`."),
                    ('help'   , 'show this help message and exit','')]
                                    
    subparsers = parser.add_subparsers(dest='command', title='commands')
    p          = dict()
    for c,h,d in commands:
        p[c] = subparsers.add_parser(c, help=h, description=d)

    p['start'].add_argument('-d','--debug',help="start SCRY in debug mode, ignoring the configuration file's debug setting",action='store_true')
    p['start'].add_argument('-r','--restart',help="start SCRY, or restart SCRY if it's already running",action='store_true')

    p['query'].add_argument('-q','--query',help='an inline SPARQL query; overrules the specification of an --input file, if one is given')
    p['query'].add_argument('-i','--input',help='path to an input file, for reading a SPARQL query from')
    p['query'].add_argument('-o','--output',help='path to an output file, for writing results to; if none is given, results are printed to the terminal')
    p['query'].add_argument('-s','--statistics',help='track and print simple statistics and progress status',action='store_true')

    p['config'].add_argument('-d','--debug',nargs='?',help='change the debug setting to the value specified; toggle if no value is given',default=False)
    p['config'].add_argument('-a','--allow_remote',nargs='?',help='change the allow_remote setting to the value specified; toggle if no value is given',default=False)
    p['config'].add_argument('-p','--port',help='change the port on which SCRY listens for requests')
    p['config'].add_argument('-L','--list_ips',help='show which IP addresses SCRY accepts requests from',action='store_true')
    p['config'].add_argument('-A','--add_ip',nargs='+',help='add the specified IP address(es) to the list SCRY accepts requests from')
    p['config'].add_argument('-R','--remove_ip',nargs='+',help='remove the specified IP address(es) from the list SCRY accepts requests from')
    p['config'].add_argument('-s','--summary',help="print a summary of SCRY's configuration",action='store_true')
    p['config'].add_argument('-r','--restart',help='start or restart SCRY after applying configuration changes (required for Debug, Allow_Remote and Port changes to take effect)',action='store_true')

    serviceparsers = p['service'].add_subparsers(dest='subcommand',title='service subcommands')
    sp             = dict()
    for c,h,d in service_cmds:
        sp[c] = serviceparsers.add_parser(c, help=h, description=d)

    sp['dir'].add_argument('directory',nargs='?',help="The path to SCRY's new working directory. If none is given, print the current directory instead.",default=False)
    sp['dir'].add_argument('-r','--reset',help="Set SCRY's working directory back to the default: ~/Documents/SCRY/",action='store_true')
    sp['search'].add_argument('terms', nargs='*', help='Optional: Results will be narrowed down to those containing the specified terms.')
    sp['install'].add_argument('id', help="The PyPI identifier of the service you'd like to install.")
    sp['install'].add_argument('-n','--no_add',help="Do not add the newly installed service to SCRY's Remote Load list.",action='store_true')
    sp['disable'].add_argument('id', nargs='+', help='The name(s) of the service(s) you want to disable.')
    sp['disable'].add_argument('-l','--list',help='Run `scry service list` after disabling selected services.',action='store_true')
    sp['enable'].add_argument('id', nargs='+', help='The name(s) of the service(s) you want to enable.')
    sp['enable'].add_argument('-l','--list',help='Run `scry service list` after enabling selected services.',action='store_true')
    sp['remove'].add_argument('id', help="The PyPI identifier of the service you'd like to permanently remove.")

    if args is None:
        args = sys.argv[1:]

    try:
        parsed = parser.parse_args(args)
        fnc = eval(parsed.command)
        fnc(parsed)
    except SilentError:
        args = [args[0],'-h'] if args and args[0] in ['start','stop','status','query','config','service','help'] else ['-h']
        parser.parse_args(args)



# Commands invoked from the entrypoint
def start(parsed):
    print ''
    print 'Starting SCRY...'

    import flask
    import datetime
    from scry.app      import app
    from scry.app.log  import get_runtime_log
    from scry.config   import get_conf
    from scry.utility  import make_bool
    from scry.services import load, describe

    conf = get_conf()
    g = dict()
    g['launch_time']     = datetime.datetime.now()
    g['request_count']   = 0
    g['query_count']     = 0
    g['allowed_ips']     = set([ip.strip() for ip in conf.get('App','ips').strip().split('\n')])
    g['services'], g['procedures'] = load()
    g['orb_description'] = describe(g['procedures'])
    g['log']             = get_runtime_log()
    g['log']('SCRY launched')
    
    flask.g = g
    
    allow_remote = make_bool(conf.get('App','allow-remote'))
    debug        = make_bool(conf.get('App','debug')) or parsed.debug
    port         = int(conf.get('App','port'))
    host         = '0.0.0.0' if allow_remote else None
    
    if parsed.restart:
        import requests
        try:
            requests.post('http://localhost:%i/shutdown' % port)
        except requests.exceptions.ConnectionError:
            pass
    app.run(debug=debug, port=port, host=host)
            

def stop(parsed):
    import requests
    from scry.config import get_conf

    print ''
    print 'Stopping SCRY...'
    try:
        print requests.post('http://localhost:%s/shutdown' % get_conf().get('App','port')).text
    except requests.exceptions.ConnectionError:
        print "SCRY isn't running!"
    print ''



def status(parsed):
    import requests
    from scry.config import get_conf
    
    print ''
    try:
        print requests.get('http://localhost:%s/status' % get_conf().get('App','port')).text
    except requests.exceptions.ConnectionError:
        print "SCRY isn't running!"
    print ''



def query(parsed):
    import datetime
    import scry.query
    import scry.services

    if not parsed.query and not parsed.input:
        print "\n  A query must be given, either directly (-q) or in a file (-i)\n  See also 'scry query -h'\n"
        sys.exit()
    
    def stat(s):
        if parsed.statistics: print(s)

    t1    = datetime.datetime.now()
    stat('\n%s -- Loading services...' % t1.time().isoformat())
    S, P  = scry.services.load()
    D     = scry.services.describe(P)
    t2    = datetime.datetime.now()
    stat('%s -- Preparing query...' % t2.time().isoformat())
    if parsed.query:
        qry = parsed.query
    else:
        with open(parsed.input) as f:
            qry = f.read()
    qh    = scry.query.QueryHandler(qry, P, D, dict())
    t3    = datetime.datetime.now()
    stat('%s -- Resolving query...' % t3.time().isoformat())
    res   = qh.resolve()
    t4    = datetime.datetime.now()
    stat('%s -- Formatting results...' % t4.time().isoformat())
    # MAKE FORMATTING FANCIER EVENTUALLY
    if parsed.output:
        with open(parsed.output,'w') as f:
            f.write('\t'.join(['?%s' % v for v in res.vars])+ '\n')
            for r in res:
                line = '\t'.join([binding.encode() if binding else '' for binding in r])
                f.write(line + '\n')
    else:
        stat('')
        print '\t'.join(['?%s' % v for v in res.vars])
        for r in res:
            line = '\t'.join([binding.encode() if binding else '' for binding in r])
            if line: print line
        stat('')
    t5 = datetime.datetime.now()
    
    stat('%s -- Query completed:\n\n      %i results bound in %f seconds:\n' % (t5.time().isoformat(), len(res), (t5-t1).total_seconds()))
    stat('  %13.6f s to load services' % (t2-t1).total_seconds())
    stat('  %13.6f s to parse and prepare the query' % (t3-t2).total_seconds())
    stat('  %13.6f s to resolve the query' % (t4-t3).total_seconds())
    stat('  %13.6f s to format and print results\n' % (t5-t4).total_seconds())
        


def config(parsed):
    import requests
    from scry.app     import update_flask_g
    from scry.config  import get_scry_dir, get_conf, write_conf
    from scry.utility import make_bool

    write_new = False
    update_g  = False
    conf      = get_conf()

    def update(field,value):
        same_val = conf.get('App',field) == value
        conf.set('App',field,value)
        return write_new or not same_val
        
    if parsed.debug is None: # Toggle
        write_new = update('debug', str(not make_bool(conf.get('App','debug'))))
    elif parsed.debug: # Overwrite
        write_new = update('debug', parsed.debug)

    if parsed.allow_remote is None: # Toggle
        write_new = update('allow-remote', str(not make_bool(conf.get('App','allow-remote'))))
    elif parsed.allow_remote: # Overwrite
        write_new = update('allow-remote', parsed.allow_remote)
    
    live_port = conf.get('App','port') # The port SCRY is /currently/ live on, if any
    if parsed.port: update('port',str(parsed.port))
    
    ips = set([ip.strip() for ip in conf.get('App','ips').strip().split('\n')])
    if parsed.remove_ip:
        for i in parsed.remove_ip:
            try:
                ips.remove(i)
                update_g = True
            except KeyError:
                print "Warning: Couldn't remove %s from the list of allowed IPs, because it's not on there."
    if parsed.add_ip:
        for i in parsed.add_ip:
            if i not in ips: update_g = True
            ips.add(i)
    if parsed.remove_ip or parsed.add_ip:
        write_new = update('ips','\n'+'\n'.join(ips))

    # WRITE NEW CONFIG FILE
    write_conf(conf)

    # PRINT CONFIG VALUES
    def print_ips():
        print '  White-listed IP addresses:'
        for i in ips: print '\t%s' % i
        
    if parsed.summary:
        ar = make_bool(conf.get('App','allow-remote'))
        print '\n  Allow remote connections?    %s' % str(ar)
        if ar: print '  Port:                        %s' % conf.get('App','port')
        print '  Debug?                       %s' % str(make_bool(conf.get('App','debug')))
        print_ips()
        print ''
    elif parsed.list_ips:
        print ''
        print_ips()
        print ''
    
    # RESTART SCRY
    if parsed.restart:
        try: # Necessary implementation for if Port is reconfigured
            requests.post('http://localhost:%s/shutdown' % live_port)
        except requests.exceptions.ConnectionError:
            pass
        start(Options(restart=False))
    elif update_g:
        update_flask_g(live_port)



def service(parsed):
    from scry.config   import get_scry_dir, get_conf, write_conf, get_subdir
    from scry.services import find_services

    sub    = parsed.subcommand
    conf   = get_conf()
    update = False

    if sub == 'dir':
        if parsed.reset:
            os.environ['SCRY_DIR'] = os.path.expanduser(os.path.join('~','Documents','SCRY')) + os.sep
        elif not parsed.directory:
            print get_scry_dir()
        else: # APPEARS NOT TO WORK! The logic is correct, but my os.environ refuses to update...
            os.environ['SCRY_DIR'] = os.path.expanduser(parsed.directory)
    
    elif sub == 'list':
        d = get_subdir('Services')
        ll, rl, nl = find_services(d)
        print'\nServices loaded from `%s`:' % d
        if ll:
            for s in ll: print '  %s' % s
        else:
            print '  -'        
        print '\nServices loaded from elsewhere:'
        if rl:
            for s in rl: print '  %s' % s
        else:
            print '  -'        
        print '\nServices NOT loaded from `%s`:' % d
        if nl:
            for s in nl: print '  %s' % s
        else:
            print '  -'
        print ''

    elif sub == 'search':
        #parsed.id
        print '\n  Sorry! This feature is currently disabled.\n'
            
    elif sub == 'install':
        import pip
        pkg = parsed.id
        pip_name = pkg.replace('_','-')
        imp_name = pkg.replace('-','_')
        pip.main(['install',pip_name])

        if not parsed.no_add:
            service(Options(subcommand='enable',id=[imp_name],list=True))

    elif sub == 'disable':
        d = get_subdir('Services')
        ll, rl, nl = find_services(d)
        for m in parsed.id:
            if m in ll:
                nl.append(m)
                update = True
            elif m in rl:
                rl.remove(m)
                update = True
            else:
                if m not in nl:
                    print 'Warning: `%s` not found in local or remotely loaded services' % m
        
    elif sub == 'enable':
        from imp import find_module
        d = get_subdir('Services')
        ll, rl, nl = find_services(d)
        for m in parsed.id:
            if m in nl:
                nl.remove(m)
                update = True
            else:
                try:
                    find_module(m)
                    rl.append(m)
                    update = True
                except ImportError:
                    if m not in ll:
                        print 'Warning: `%s` not found; could not enable it' % m

    elif sub == 'remove':
        from scry.config   import get_subdir
        from scry.services import find_services

        pkg = parsed.id
        ll,rl,nl = find_services(get_subdir('Services'))

        if pkg in ll or pkg in nl:
            # Delete the file
            
            pass
        elif pkg in rl:
            # pip uninstall
            import pip
            pip.main(['uninstall',pkg])
        else:
            print 'Warning: `%s` not found; could not remove it' % pkg
            return
        
        service(Options(subcommand='disable',id=[pkg],list=True))
        
        
    elif sub == 'help':
        cmd(['service', '-h'])
    
    # If disable / enable changed anything:    
    if update:
        from scry.app import update_flask_g
        conf.set('Services','no-load','\n'+'\n'.join(set(nl)))
        conf.set('Services','remote-load','\n'+'\n'.join(set(rl)))
        write_conf(conf)
        update_flask_g(conf.get('App','port'))
        if parsed.list:
            service(Options(subcommand='list'))

def help(parsed):
    cmd(['-h'])