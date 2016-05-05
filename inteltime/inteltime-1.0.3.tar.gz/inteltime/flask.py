"""
inteltime - Cycle and Checkpoint Calculator front-end for Slack
"""

import json
import re
import pytz
from flask import Flask, Blueprint, Response, request

from . import Cycle, Checkpoint

bp = Blueprint('inteltime', __name__)                #pylint: disable=invalid-name

@bp.route("/cycle", methods=['GET', 'POST'])
def slack_checkpoint():
    """Compute cycle time"""
    form = request.form if request.method == 'POST' else request.args
    text = form.get('text', '')
    if ',' in text:
        target, zone = text.split(',')
    else:
        target, zone = text, None
    try:
        cycle = Cycle(target, timezone=zone)
    except pytz.exceptions.UnknownTimeZoneError as err:
        return "Unknown timezone: {}".format(err)

    text = "Cycle start: {}\nCycle end: {}".format(cycle, cycle+1)
    return Response(json.dumps({"text": text, "response_type": "in_channel"}),
                    content_type="application/json")


@bp.route("/checkpoint", methods=['GET', 'POST'])
def slack_cycle():
    """Comput checkpoint time, or checkpoints on date"""
    form = request.form if request.method == 'POST' else request.args
    text = form.get('text', '')
    if ',' in text:
        target, zone = text.split(',')
    else:
        target, zone = text, None
    match = re.match("on (.*)", target, re.IGNORECASE)
    try:
        if match:
            checkpoint = Checkpoint(match.group(0), timezone=zone)
            text = "\n".join(["Checkpoint {}: {}{}".format(
                chkp.number(), chkp, " (new cycle)" if chkp.cycle_start() else '')
                              for chkp in checkpoint.on_day()])
        else:
            checkpoint = Checkpoint(target, timezone=zone)
            text = "Next checkpoint at {} (in {})".format(
                checkpoint+1, checkpoint.until_next())
    except pytz.exceptions.UnknownTimeZoneError as err:
        text = "Error: Unknown timezone: {}".format(err)
    return Response(json.dumps({"text": text, "response_type": "in_channel"}),
                    content_type="application/json")


app = Flask(__name__)                            #pylint: disable=invalid-name
app.register_blueprint(bp)

def main():
    """Standalone flask mode for debugging, not designed for production"""
    config = {
        'url-prefix': '/inteltime',
        'ssl-context': ['/etc/ssl/private/local.pem'],
        'debug': True
    }

    url_prefix = config.get('url-prefix')
    if url_prefix:
        app.register_blueprint(bp, url_prefix=url_prefix)

    ssl_context = config.get('ssl-context')
    if ssl_context:
        ssl_context = tuple(ssl_context)

    app.run(
        host=config.get('bind-host', '0.0.0.0'),
        port=config.get('bind-port', 8443),
        debug=config.get('debug', False),
        ssl_context=ssl_context
    )


if __name__ == '__main__':
    main()
