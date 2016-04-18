"""
Logging.
"""

import structlog
import twisted


logger = structlog.getLogger()

_configured = False
if not _configured:
    structlog.configure(
        processors=[
            structlog.processors.StackInfoRenderer(),
            structlog.twisted.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.twisted.LoggerFactory(),
        wrapper_class=structlog.twisted.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _configured = True


log = logger
log.startLogging = twisted.python.log.startLogging
