import flask

from datetime import datetime
from functools import wraps
from werkzeug.exceptions import HTTPException
from scry.app import app, DEFAULT_QUERY
from scry.app.query_wrapper import QueryWrapper


# Use this decorator AFTER the app.route decorator(s), NOT before.
def host_only(func):
    @wraps(func)
    def host_only_func(*args, **kwargs):
        if flask.request.remote_addr != '127.0.0.1':
            e = HTTPException('The page you have requested may only be accessed by the host.')
            e.code = 403
            raise e
            return
        return func(*args, **kwargs)
    return host_only_func
    
    
@app.route('/')
@app.route('/about')
def about():
    args = dict()
    args.update(flask.request.args)
    args.update({'page':'about'})
    return flask.render_template('about.html', **args)


@app.route('/services')
def services():
    args = dict()
    args.update(flask.request.args)
    args.update({'page':'services',
                 'services':flask.g['services'],
                 'procedures':flask.g['procedures']})
    return flask.render_template('services.html', **args)


@app.route('/query')
def query():
    args = dict()
    args.update(flask.request.args)
    args.update({'default_query':DEFAULT_QUERY,
                 'page':'query'})
    return flask.render_template('query.html', **args)

# Use HTML anchors (#) -- not URL parameters (?) to get specific queries, endpoints, tab titles through YASQE.
# Variables whose value you can specify: query, endpoint, contentTypeConstruct, contentTypeSelect, endpoint, requestMethod, tabTitle, headers, outFormat
# Example: localhost:5000/query#query=SELECT%20*%20WHERE%20%7B%0A%20%20%3Fs%20%3Fp%20%3Fo%20.%0A%7D%20LIMIT%2010&tabTitle=Example%201


@app.route('/update')
#@host_only
def update():
    args = dict()
    args.update(flask.request.args)
    args.update({'page':'update'})
    return flask.render_template('update.html', **args)


@app.route('/contact')
def contact():
    args = dict()
    args.update(flask.request.args)
    args.update({'page':'contact'})
    return flask.render_template('contact.html', **args)

        
@app.route('/scry/', methods=['GET', 'POST'])
def sparql():
    flask.g['query_count'] += 1
    
    wrapper = QueryWrapper(flask.request,flask.g)
    return wrapper.resolve()


@app.route('/shutdown', methods=['POST'])
@host_only
def shutdown():
    func = flask.request.environ.get('werkzeug.server.shutdown')()
    return 'SCRY stopped.'


@app.route('/update_g', methods=['POST'])
@host_only
def update_g():
    from scry.config   import get_conf
    from scry.services import load, describe
    conf = get_conf()
    flask.g['allowed_ips']                     = set([ip.strip() for ip in conf.get('App','ips').strip().split('\n')])
    flask.g['services'], flask.g['procedures'] = load()
    flask.g['orb_description']                 = describe(flask.g['procedures'])
    return 'Update succesful.'


@app.route('/status')
@host_only
def status():
    launch = flask.g['launch_time']
    live   = datetime.now() - launch
    mins   = live.seconds/60
    hours  = mins/60
    days   = hours/24

    secs   = live.seconds - mins*60
    mins  -= hours*60
    hours -= days*24
    plural = lambda n: 's' if n!=1 else ''
    
    if days:
        time = '%i day%s, %i hour%s and %i minute%s' % (days, plural(days), hours, plural(hours), mins, plural(mins))
    elif hours:
        time = '%i hour%s, %i minute%s and %i second%s' % (hours, plural(hours), mins, plural(mins), secs, plural(secs))
    elif mins:
        time = '%i minute%s and %i second%s' % (mins, plural(mins), secs, plural(secs))
    else:
        time = '%i seconds' % secs
    
    res  = 'This SCRY instance has been live for %s.\n' % time +\
           'It was launched on %s at %02i:%02i:%02i.\n' % (str(launch.date()), launch.hour, launch.minute, launch.second) +\
           'Since then, it has received %i requests, of which %i were SPARQL queries.' % (flask.g['request_count'], flask.g['query_count'])
    return res