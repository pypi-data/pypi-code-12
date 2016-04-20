#!/usr/bin/env python

import trust
import trust.audit
import logging
import os
import www
from flask import Flask, jsonify, request
from logging.handlers import SysLogHandler


app = Flask(__name__)

logHandler = SysLogHandler(address="/dev/log")
formatter = logging.Formatter("trust-service: [%(levelname)s] %(message)s")

logHandler.setFormatter(formatter)
logHandler.setLevel(logging.DEBUG)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.DEBUG)

trust.trust_blueprint.finder = trust.FileFinder(
    data_path=os.path.join(os.path.dirname(__file__), "tests/system/data"),
    logger=app.logger,
    audit=trust.audit.AuditToSyslog("trust-service-audit"))

app.register_blueprint(trust.trust_blueprint, url_prefix="/service")
app.register_blueprint(www.docs_blueprint)

app.logger.info("The application started.")

if __name__ == "__main__":
    app.run(threaded=True)
