"""
Utilities to help debugging python programs in a console easier
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from IPython.terminal import embed, ipapp


# Used by _my_embed
_embedded_shell = None


def break_here():
    import pdb
    pdb.set_trace()


def ipython_here(**kwargs):
    _my_embed(stack_depth=3, **kwargs)


def _my_embed(**kwargs):
    """
    Since we need to control the stack_depth, the only way is to
    copy-and-paste the implementation and change the stack_depth argument :(
    """

    config = kwargs.get('config')
    header = kwargs.pop('header', u'')
    stack_depth = kwargs.pop('stack_depth', 2)
    if config is None:
        config = ipapp.load_default_config()
        config.InteractiveShellEmbed = config.TerminalInteractiveShell
        kwargs['config'] = config

    global _embedded_shell
    if _embedded_shell is None:
        _embedded_shell = embed.InteractiveShellEmbed(**kwargs)
    _embedded_shell(header=header, stack_depth=stack_depth)
