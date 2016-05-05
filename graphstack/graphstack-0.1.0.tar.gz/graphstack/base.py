import contextlib
from functools import wraps
import os.path
from pycallgraph import Config, GlobbingFilter, PyCallGraph
from pycallgraph.output import GraphvizOutput

@contextlib.contextmanager
def gscontext(filename, exclude=None, max_depth=None):
    """Generate a call graph for the enclosed context

    Output a call graph to the chosen filename (introspecting the
    format along the way), optionally excluding some items.

    Args:
        filename (str): The output filename
	exclude (Optional[list]): The globbing strings to exclude. Defaults to ['graphstack.*'].
	max_depth (Optional[int]): The maximum recursion depth to plot. Defaults to infinite.

    """

    globkwargs = {
        'exclude': [
            'graphstack.*',
        ],
    }
    if exclude is not None:
    	globkwargs['exclude'].extend(exclude)
    if max_depth is not None:
        globkwargs['max_depth'] = max_depth

    # Configure exclusion filtering
    config = Config()
    config.trace_filter = GlobbingFilter(**globkwargs)

    # Configure GraphViz output
    fnsplit = os.path.splitext(filename)
    if len(fnsplit) == 1:
        outfile = filename + '.pdf'
        filetype = 'pdf'
    elif len(fnsplit) == 2:
        outfile = filename
        filetype = fnsplit[1][1:]
    graphviz = GraphvizOutput(output_file=outfile)
    graphviz.output_type = filetype

    # Set up context manager
    with PyCallGraph(output=graphviz, config=config):
        yield

def gsdeco(*opts, **kwopts):
    """Generate a call graph for the wrapped function

    Output a call graph to a filename introspected from the function name,
    by wrapping calls to the function in gscontext.

    Args:
        filetype (Optional[str]): The type of output file

        + valid arguments to the context manager
    """
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            filetype = '.' + kwopts.pop('filetype', 'pdf')
            with gscontext(fn.__name__ + filetype, *opts, **kwopts):
                res = fn(*args, **kwargs)
            return res
        return wrapped
    return decorator
