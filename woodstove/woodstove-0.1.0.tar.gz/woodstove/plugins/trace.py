''' Tracer plugin '''
import sys
import time
import pstats
import cProfile
if sys.version_info >= (3, 0, 0):
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO
from woodstove import hooks, log, context


def trace_enabled(req):
    ''' Is tracing enabled for this request '''
    return req.request.headers.get('Woodstove-Trace-Enabled') is not None


def log_delta(req, msg, delta=None):
    ''' Log delta between now and entry of route context '''
    if delta is None:
        ctx = context.ctx_get()
        delta = time.time() - ctx['tracer_context_start']

    log.get_logger(req.robj.fname).debug("%.4f: %s(%r,%r): %s", delta, req.robj.fname, req.args,
                        req.kwargs, msg)


def end_trace(fname):
    ''' Disable profiler '''
    ctx = context.ctx_get()
    profiler = ctx.get('tracer_profiler')

    if profiler is None:
        return

    logger = log.get_logger(__name__)
    profiler.disable()
    logger.debug("Profiler disabled")
    lines = ctx['tracer_lines']
    sort = ctx['tracer_sort'].split(',')
    trace_buf = BytesIO()
    stats = pstats.Stats(profiler, stream=trace_buf).sort_stats(*sort)
    stats.print_stats(lines)
    logger.debug("Dumping profiling data")
    log.get_logger(fname).debug(trace_buf.getvalue())


@hooks.hook('route', 'context')
def trace_route_context(ctx):
    ''' Trace timing of route context setup '''
    req = ctx['request']

    if not trace_enabled(req):
        return

    logger = log.get_logger(req.robj.fname)
    logger.debug("Request tracing enabled")
    ctx_time = time.time()
    profiler = cProfile.Profile()
    lines = int(req.request.headers.get('Woodstove-Trace-Lines', '25'))
    sort = req.request.headers.get('Woodstove-Trace-Sort', 'cumulative')
    ctx.update({"tracer_context_start": ctx_time,
                "tracer_profiler": profiler,
                "tracer_lines": lines,
                "tracer_sort": sort})
    logger.debug("Starting profiler")
    profiler.enable()
    log_delta(req, "Route context entered", 0.0)
    log.get_logger(__name__).debug("%f: Route context entered", time.time())


@hooks.hook('route', 'enter')
def trace_route_enter(req):
    ''' Trace timing of route enter '''
    if not trace_enabled(req):
        return

    log_delta(req, "Route entered")


@hooks.hook('route', 'exit')
def trace_route_exit(req):
    ''' Trace timing of route exit '''
    if not trace_enabled(req):
        return

    log_delta(req, "Route exited")
    end_trace(__name__)
