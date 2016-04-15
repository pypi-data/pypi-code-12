# -*- coding: utf-8 -*-
# exdoc.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,E0012,E0611,E1101,E1103,F0401,R0201,R0903,R0913
# pylint: disable=R0914,W0105,W0122,W0212,W0611,W0613

# Standard library imports
from __future__ import print_function
import collections
import bisect
import copy
import os
import pickle
import sys
import textwrap
if sys.hexversion < 0x03000000: # pragma: no cover
    import __builtin__
else:   # pragma: no cover
    import builtins as __builtin__
# Putil imports
if sys.hexversion >= 0x03000000: # pragma: no cover
    from putil.compat3 import _rwtb
else: # pragma: no cover
    from putil.compat2 import _rwtb
import putil.exh
import putil.misc
import putil.tree


###
# Global variables
###
# Minimum width of the output lines, broken out as a global variable
# mainly to ease testing
_MINWIDTH = 40


###
# Functions
###
def _format_msg(text, width, indent=0, prefix=''):
    r"""
    Format exception message: replace newline characters \n with ``\n``,
    ` with \` and then wrap text as needed
    """
    text = repr(text).replace('`', '\\`').replace('\\n', ' ``\\n`` ')
    sindent = ' '*indent if not prefix else prefix
    wrapped_text = textwrap.wrap(text, width, subsequent_indent=sindent
    )
    # [1:-1] eliminates quotes generated by repr in first line
    return ('\n'.join(wrapped_text))[1:-1].rstrip()


def _validate_fname(fname, arg_name):
    """ Validates that a string is a valid file name """
    if fname is not None:
        msg = 'Argument `{0}` is not valid'.format(arg_name)
        if ((not isinstance(fname, str)) or
           (isinstance(fname, str) and ('\0' in fname))):
            raise RuntimeError(msg)
        try:
            if not os.path.exists(fname):
                os.access(fname, os.W_OK)
        except (TypeError, ValueError): # pragma: no cover
            raise RuntimeError(msg)


###
# Context managers
###
class ExDocCxt(object):
    r"""
    Context manager to simplify exception tracing; it sets up the
    tracing environment and returns a :py:class:`putil.exdoc.ExDoc`
    object that can the be used in the documentation string of each
    callable to extract the exceptions documentation with either
    :py:meth:`putil.exdoc.ExDoc.get_sphinx_doc` or
    :py:meth:`putil.exdoc.ExDoc.get_sphinx_autodoc`.

    :param exclude: Module exclusion list. A particular callable in
                    an otherwise fully qualified name is omitted if
                    it belongs to a module in this list. If None all
                    callables are included
    :type  exclude: list of strings or None

    :param pickle_fname: File name to pickle traced exception handler
                         (useful for debugging purposes). If None all
                         pickle file is created
    :type  pickle_fname: :ref:`FileName` or None

    :param in_callables_fname: File name that contains traced modules
                               information. File can be produced by either
                               the
                               :py:meth:`putil.pinspect.Callables.save` or
                               :py:meth:`putil.exh.ExHandle.save_callables`
                               methods
    :type  in_callables_fname: :ref:`FileNameExists` or None

    :param out_callables_fname: File name to save traced modules information
                                to in `JSON <http://www.json.org/>`_ format.
                                If the file exists it is overwritten
    :type  out_callables_fname: :ref:`FileNameExists` or None

    :raises:
     * OSError (File *[in_callables_fname]* could not be found)

     * RuntimeError (Argument \`in_callables_fname\` is not valid)

     * RuntimeError (Argument \`exclude\` is not valid)

     * RuntimeError (Argument \`out_callables_fname\` is not valid)

     * RuntimeError (Argument \`pickle_fname\` is not valid)

    For example:

        >>> from __future__ import print_function
        >>> import putil.eng, putil.exdoc
        >>> with putil.exdoc.ExDocCxt() as exdoc_obj:
        ...     value = putil.eng.peng(1e6, 3, False)
        >>> print(exdoc_obj.get_sphinx_doc('putil.eng.peng'))
        .. Auto-generated exceptions documentation for putil.eng.peng
        <BLANKLINE>
        :raises:
         * RuntimeError (Argument \`frac_length\` is not valid)
        <BLANKLINE>
         * RuntimeError (Argument \`number\` is not valid)
        <BLANKLINE>
         * RuntimeError (Argument \`rjust\` is not valid)
        <BLANKLINE>
        <BLANKLINE>
    """
    def __init__(
        self,
        exclude=None,
        _no_print=True,
        pickle_fname=None,
        in_callables_fname=None,
        out_callables_fname=None
    ):
        # Validate aguments
        if (exclude is not None) and (not isinstance(exclude, list)):
            raise RuntimeError('Argument `exclude` is not valid')
        _validate_fname(pickle_fname, 'pickle_fname')
        _validate_fname(in_callables_fname, 'in_callables_fname')
        _validate_fname(out_callables_fname, 'out_callables_fname')
        if ((in_callables_fname is not None) and
           (not os.path.exists(in_callables_fname))):
            raise OSError(
                'File {0} could not be found'.format(in_callables_fname)
            )
        if not isinstance(_no_print, bool):
            raise RuntimeError('Argument `_no_print` is not valid')
        # Need to have an exception handler with full_cname=True and clean
        # the slate for the trace. If there is an existing handler copy it
        # to a temporary variable and copy it back/restore it upon exit
        self._pickle_fname = pickle_fname
        self._pickle_dict = {}
        self._existing_exhobj = None
        self._out_callables_fname = out_callables_fname
        if putil.exh.get_exh_obj() is not None:
            self._existing_exhobj = copy.copy(putil.exh.get_exh_obj())
        putil.exh.set_exh_obj(
            putil.exh.ExHandle(
                full_cname=True,
                exclude=exclude,
                callables_fname=in_callables_fname
            )
        )
        # Create a dummy ExDoc object. It has to be created here so that
        # it can be returned by the context in the '[...] as [...]' clause.
        # The actual (valid) contents of this object are loaded upon
        # context exit
        self._exdoc_obj = putil.exdoc.ExDoc(
            exh_obj=putil.exh.ExHandle(), _empty=True, _no_print=_no_print
        )
        # Pass exclude list to all processes. For multi-CPU trace runs
        # via py.test (using the xdist plug-in) this is picked up in the
        # ../tests/conftest.py file
        setattr(__builtin__, '_EXDOC_EXCLUDE', exclude)
        setattr(__builtin__, '_EXDOC_FULL_CNAME', True)
        setattr(__builtin__, '_EXDOC_CALLABLES_FNAME', in_callables_fname)

    def __enter__(self):
        return self._exdoc_obj

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            putil.exh.del_exh_obj()
            return False
        # Merge all exception handlers of a multi-CPU run. Each CPU
        # process should place its exception handler as an element of
        # __builtin__._EXH_LIST. For py.test-based tracing, the code to
        # do this is in ../tests/conftest.py
        if hasattr(__builtin__, '_EXH_LIST') and __builtin__._EXH_LIST:
            exhobj = copy.copy(__builtin__._EXH_LIST[0])
            for obj in __builtin__._EXH_LIST[1:]:
                exhobj += obj
            self._pickle_dict['_EXH_LIST'] = copy.copy(__builtin__._EXH_LIST)
            delattr(__builtin__, '_EXH_LIST')
        else:
            exhobj = putil.exh.get_exh_obj()
        delattr(__builtin__, '_EXDOC_EXCLUDE')
        delattr(__builtin__, '_EXDOC_FULL_CNAME')
        delattr(__builtin__, '_EXDOC_CALLABLES_FNAME')
        if self._out_callables_fname is not None:
            exhobj.save_callables(self._out_callables_fname)
        self._exdoc_obj._exh_obj = copy.copy(exhobj)
        self._pickle_dict['exhobj'] = copy.copy(exhobj)
        # Delete all traced exceptions
        putil.exh.del_exh_obj()
        # Generate exceptions database
        self._exdoc_obj._build_ex_tree()
        self._exdoc_obj._build_module_db()
        self._pickle_dict['exdoc'] = copy.copy(self._exdoc_obj)
        if self._pickle_fname is not None:
            with open(self._pickle_fname, 'wb') as fobj:
                pickle.dump(self._pickle_dict, fobj)
        # Delete exceptions from exception tree building. The _build_ex_tree()
        # method uses the tree module, which in turn uses the ExDoc class, so
        # there will be exceptions registered in a global exception handler
        putil.exh.del_exh_obj()
        # Restore exception handler (if any) active when context was activated
        if self._existing_exhobj is not None:
            putil.exh.set_exh_obj(self._existing_exhobj)


###
# Classes
###
class ExDoc(object):
    """
    Generates exception documentation with `reStructuredText
    <http://docutils.sourceforge.net/rst.html>`_ mark-up

    :param exh_obj: Exception handler containing exception information
                    for the callable(s) to be documented
    :type  exh_obj: :py:class:`putil.exh.ExHandle`

    :param depth: Default hierarchy levels to include in the exceptions
                  per callable (see :py:attr:`putil.exdoc.ExDoc.depth`).
                  If None exceptions at all depths are included
    :type  depth: non-negative integer or None

    :param  exclude: Default list of (potentially partial) module and
                     callable names to exclude from exceptions per callable
                     (see :py:attr:`putil.exdoc.ExDoc.exclude`). If None all
                     callables are included
    :type   exclude: list of strings or None

    :rtype: :py:class:`putil.exdoc.ExDoc`

    :raises:
     * RuntimeError (Argument \\`depth\\` is not valid)

     * RuntimeError (Argument \\`exclude\\` is not valid)

     * RuntimeError (Argument \\`exh_obj\\` is not valid)

     * RuntimeError (Exceptions database is empty)

     * RuntimeError (Exceptions do not have a common callable)

     * ValueError (Object of argument \\`exh_obj\\` does not have any
       exception trace information)
    """
    # pylint: disable=R0902
    def __init__(self, exh_obj, depth=None, exclude=None,
                 _empty=False, _no_print=False):
        if (not _empty) and (not isinstance(exh_obj, putil.exh.ExHandle)):
            raise RuntimeError('Argument `exh_obj` is not valid')
        if (not _empty) and (not exh_obj.exceptions_db):
            raise ValueError(
                'Object of argument `exh_obj` does not have any '
                'exception trace information'
            )
        if not isinstance(_no_print, bool):
            raise RuntimeError('Argument `_no_print` is not valid')
        self._module_obj_db = {}
        self._depth = None
        self._exclude = None
        self._tobj = None
        self._exh_obj = exh_obj
        self._no_print = _no_print
        self._set_depth(depth)
        self._set_exclude(exclude)
        if not _empty:
            self._build_ex_tree()
            self._build_module_db()

    def __copy__(self):
        cobj = ExDoc(
            exh_obj=None,
            depth=self.depth,
            exclude=self.exclude[:] if self.exclude else None,
            _empty=True,
            _no_print=self._no_print
        )
        cobj._exh_obj = copy.copy(self._exh_obj)
        existing_exhobj = (
            copy.copy(putil.exh.get_exh_obj())
            if putil.exh.get_exh_obj() is not None else
            None
        )
        cobj._tobj = copy.copy(self._tobj)
        if existing_exhobj is None:
            putil.exh.del_exh_obj()
        else:
            putil.exh.set_exh_obj(existing_exhobj)
        cobj._module_obj_db = copy.deepcopy(self._module_obj_db)
        return cobj

    def _build_ex_tree(self):
        """ Construct exception tree from trace """
        # Load exception data into tree structure
        sep = self._exh_obj.callables_separator
        data = self._exh_obj.exceptions_db
        if not data:
            raise RuntimeError('Exceptions database is empty')
        # Add root node to exceptions, needed when tracing done
        # through test runner which is excluded from callable path
        for item in data:
            item['name'] = 'root{sep}{name}'.format(sep=sep, name=item['name'])
        self._tobj = putil.tree.Tree(sep)
        try:
            self._tobj.add_nodes(data)
        except ValueError as eobj:
            if str(eobj).startswith('Illegal node name'):
                raise RuntimeError('Exceptions do not have a common callable')
            raise
        # Find closest root node to first multi-leaf branching or first
        # callable with exceptions and make that the root node
        node = self._tobj.root_name
        while ((len(self._tobj.get_children(node)) == 1) and
              (not self._tobj.get_data(node))):
            node = self._tobj.get_children(node)[0]
        if not self._tobj.is_root(node):    # pragma: no branch
            self._tobj.make_root(node)
            nsep = self._tobj.node_separator
            prefix = nsep.join(node.split(self._tobj.node_separator)[:-1])
            self._tobj.delete_prefix(prefix)
        self._print_ex_tree()

    def _build_module_db(self):
        """
        Build database of module callables sorted by line number.
        The database is a dictionary whose keys are module file names and
        whose values are lists of dictionaries containing name and line
        number of callables in that module
        """
        tdict = collections.defaultdict(lambda: [])
        for callable_name, callable_dict in self._exh_obj.callables_db.items():
            fname, line_no = callable_dict['code_id']
            cname = (
                '{cls_name}.__init__'.format(cls_name=callable_name)
                if callable_dict['type'] == 'class' else
                callable_name
            )
            tdict[fname].append({'name':cname, 'line':line_no})
        for fname in tdict.keys():
            self._module_obj_db[fname] = sorted(
                tdict[fname], key=lambda idict: idict['line']
            )

    def _get_depth(self):
        """ depth getter """
        return self._depth

    def _get_exclude(self):
        """ exclude getter """
        return self._exclude

    def _print_ex_tree(self):
        """ Prints exception tree """
        if not self._no_print:
            print(self._tobj)

    def _process_exlist(self, exc, raised):
        """
        Remove raised information from exception message and create separate
        list for it
        """
        if (not raised) or (raised and exc.endswith('*')):
            return exc[:-1] if exc.endswith('*') else exc
        return None

    def _set_depth(self, depth):
        """ depth setter """
        if depth and ((not isinstance(depth, int)) or
           (isinstance(depth, int) and (depth < 0))):
            raise RuntimeError('Argument `depth` is not valid')
        self._depth = depth

    def _set_exclude(self, exclude):
        """ exclude setter """
        if exclude and ((not isinstance(exclude, list)) or
           (isinstance(exclude, list) and
           any([not isinstance(item, str) for item in exclude]))):
            raise RuntimeError('Argument `exclude` is not valid')
        self._exclude = exclude

    def get_sphinx_autodoc(self, depth=None, exclude=None,
                           width=72, error=False, raised=False,
                           no_comment=False):
        """
        Returns an exception list marked up in `reStructuredText`_
        automatically determining callable name

        :param depth: Hierarchy levels to include in the exceptions list
                      (overrides default **depth** argument; see
                      :py:attr:`putil.exdoc.ExDoc.depth`). If None exceptions
                      at all depths are included
        :type  depth: non-negative integer or None

        :param exclude: List of (potentially partial) module and callable
                        names to exclude from exceptions list  (overrides
                        default **exclude** argument, see
                        :py:attr:`putil.exdoc.ExDoc.exclude`). If None all
                        callables are included
        :type  exclude: list of strings or None

        :param width: Maximum width of the lines of text (minimum 40)
        :type  width: integer

        :param error: Flag that indicates whether an exception should be
                      raised if the callable is not found in the callables
                      exceptions database (True) or not (False)
        :type  error: boolean

        :param raised: Flag that indicates whether only exceptions that
                       were raised (and presumably caught) should be
                       documented (True) or all registered exceptions should
                       be documented (False)

        :type  raised: boolean

        :param no_comment: Flag that indicates whether a reStructuredText
                           comment labeling the callable (method, function or
                           class property) should be printed (False) or not
                           (True) before the exceptions documentation
        :type  no_comment: boolean

        :raises:

         * RuntimeError (Argument \\`depth\\` is not valid)

         * RuntimeError (Argument \\`error\\` is not valid)

         * RuntimeError (Argument \\`exclude\\` is not valid)

         * RuntimeError (Argument \\`no_comment\\` is not valid)

         * RuntimeError (Argument \\`raised\\` is not valid)

         * RuntimeError (Argument \\`width\\` is not valid)

         * RuntimeError (Callable not found in exception list: *[name]*)

         * RuntimeError (Unable to determine callable name)
        """
        # This code is cog-specific: cog code file name is the module
        # file name, a plus (+), and then the line number where the
        # cog function is
        frame = sys._getframe(1)
        index = frame.f_code.co_filename.rfind('+')
        fname = os.path.abspath(frame.f_code.co_filename[:index])
        # Find name of callable based on module name and line number
        # within that module, then get the exceptions by using the
        # get_sphinx_doc() method with this information
        line_num = int(frame.f_code.co_filename[index+1:])
        module_db = self._module_obj_db[fname]
        names = [callable_dict['name'] for callable_dict in module_db]
        line_nums = [callable_dict['line'] for callable_dict in module_db]
        name = names[bisect.bisect(line_nums, line_num)-1]
        return self.get_sphinx_doc(
            name=name,
            depth=depth,
            exclude=exclude,
            width=width,
            error=error,
            raised=raised,
            no_comment=no_comment
        )

    def get_sphinx_doc(self, name, depth=None, exclude=None,
                       width=72, error=False, raised=False, no_comment=False):
        """
        Returns an exception list marked up in `reStructuredText`_

        :param name: Name of the callable (method, function or class
                     property) to generate exceptions documentation for
        :type  name: string

        :param depth: Hierarchy levels to include in the exceptions
                      list (overrides default **depth** argument; see
                      :py:attr:`putil.exdoc.ExDoc.depth`). If None exceptions
                      at all depths are included
        :type  depth: non-negative integer or None

        :param exclude: List of (potentially partial) module and
                        callable names to exclude from exceptions list
                        (overrides default **exclude** argument; see
                        :py:attr:`putil.exdoc.ExDoc.exclude`). If None all
                        callables are included
        :type  exclude: list of strings or None

        :param width: Maximum width of the lines of text (minimum 40)
        :type  width: integer

        :param error: Flag that indicates whether an exception should
                      be raised if the callable is not found in the callables
                      exceptions database (True) or not (False)
        :type  error: boolean

        :param raised: Flag that indicates whether only exceptions that
                       were raised (and presumably caught) should be
                       documented (True) or all registered exceptions
                       should be documented (False)
        :type  raised: boolean

        :param no_comment: Flag that indicates whether a reStructuredText
                           comment labeling the callable (method, function or
                           class property) should be printed (False) or not
                           (True) before the exceptions documentation
        :type  no_comment: boolean

        :raises:
         * RuntimeError (Argument \\`depth\\` is not valid)

         * RuntimeError (Argument \\`error\\` is not valid)

         * RuntimeError (Argument \\`exclude\\` is not valid)

         * RuntimeError (Argument \\`no_comment\\` is not valid)

         * RuntimeError (Argument \\`raised\\` is not valid)

         * RuntimeError (Argument \\`width\\` is not valid)

         * RuntimeError (Callable not found in exception list: *[name]*)
        """
        # pylint: disable=R0101,R0204,R0912,R0915,R0916
        if depth and ((not isinstance(depth, int)) or
           (isinstance(depth, int) and (depth < 0))):
            raise RuntimeError('Argument `depth` is not valid')
        if exclude and ((not isinstance(exclude, list)) or
           (isinstance(exclude, list) and
           any([not isinstance(item, str) for item in exclude]))):
            raise RuntimeError('Argument `exclude` is not valid')
        if (not isinstance(width, int)) or (isinstance(width, int) and
           (width < _MINWIDTH)):
            raise RuntimeError('Argument `width` is not valid')
        if not isinstance(error, bool):
            raise RuntimeError('Argument `error` is not valid')
        if not isinstance(raised, bool):
            raise RuntimeError('Argument `raised` is not valid')
        if not isinstance(no_comment, bool):
            raise RuntimeError('Argument `raised` is not valid')
        depth = self._depth if depth is None else depth
        exclude = self._exclude if not exclude else exclude
        callable_dict = {}
        prop = False
        # Try to find "regular" callable. The trace may have several calls
        # to the same callable, capturing potentially different exceptions
        # or behaviors, thus capture them all
        instances = self._tobj.search_tree(name)
        if instances:
            callable_dict[name] = {'type':'regular', 'instances':instances}
        else:
            # Try to find property callable
            for action in ['getter', 'setter', 'deleter']:
                prop_name = '{name}({action})'.format(name=name, action=action)
                instances = self._tobj.search_tree(prop_name)
                if instances:
                    callable_dict[prop_name] = {
                        'type':action, 'instances':instances
                    }
                    prop = True
        if error and (not callable_dict):
            raise RuntimeError(
                'Callable not found in exception list: {callable}'.format(
                    callable=name
                )
            )
        elif not callable_dict:
            # Callable did not register any exception
            return ''
        # Create exception table using depth, exclude and raised arguments
        sep = self._tobj.node_separator
        dkeys = []
        for key, name_dict in callable_dict.items():
            exlist = []
            for callable_root in name_dict['instances']:
                # Find callable tree depth, this is the reference
                # level (depth=0) for the depth argument
                rlevel = callable_root[:callable_root.index(name)].count(sep)
                # Create a list of tuples with the full node name of each node
                # that contains the callable name (to find exceptions in tree)
                # and the path underneath the callable appearance on the
                # callable tree, split by tree path separator (to determine if
                # exception should be added based on depth and exclusion list
                nodes = self._tobj.get_subtree(callable_root)
                tnodes = [
                    (node, sep.join(node.split(sep)[rlevel:]))
                    for node in nodes
                ]
                for fnode, rnode in tnodes:
                    data = self._tobj._get_data(fnode)
                    if (data and ((depth is None) or ((depth is not None) and
                       (rnode.count(sep) <= depth))) and ((not exclude) or
                       (not any([item in rnode for item in exclude])))):
                        for exc in data:
                            msg = self._process_exlist(exc, raised)
                            if msg is not None:
                                exlist.append(msg)
            if exlist:
                name_dict['exlist'] = list(set(exlist[:]))
            else:
                # A callable can have registered exceptions but none of them
                # may meet the depth and exclude specification, in this case
                # the entry should be deleted from the dictionary
                dkeys.append(key)
        for key in dkeys:
            del callable_dict[key]
        if not callable_dict:
            # Callable had registered exceptions but not a single one of those
            # was raised
            return ''
        # Generate final output
        if no_comment:
            exoutput = ['']
        else:
            template = (
                '.. Auto-generated exceptions documentation for {callable}'
            )
            exoutput = [
                _format_msg(
                    template.format(callable=name), width, prefix='.. '
                )
            ]
            exoutput.extend([''])
        desc_dict = {
            'getter':'retrieved',
            'setter':'assigned',
            'deleter':'deleted'
        }
        if prop:
            if len(callable_dict) == 1:
                # For a property that raises exceptions on one and only one
                # action (set, get or delete) the format when there is only
                # one exception is (with get as an example action):
                # :raises: (when retrieved) RuntimeError (Invalid option)
                # If there are multiple exceptions:
                # :raises: (when retrieved)
                #
                #    * RuntimeError (Invalid options)
                #
                #    * TypeError (Wrong type)
                callable_root = next(iter(callable_dict))
                action = callable_dict[callable_root]['type']
                desc = desc_dict[action]
                exlist = set(callable_dict[callable_root]['exlist'])
                exlength = len(exlist)
                indent = 1 if exlength == 1 else 3
                template = ':raises: (when {action})\n\n'.format(action=desc)
                prefix = (template.strip()+' ') if exlength == 1 else ' * '
                fexlist = [
                    _format_msg(
                        '{prefix}{name}'.format(prefix=prefix, name=name),
                        width,
                        indent
                    ) for name in sorted(list(exlist))
                ]
                exoutput.extend(
                    [(template if exlength > 1 else '')+'\n\n'.join(fexlist)]
                )
            else:
                # For a property that raises exceptions on more than one
                # action (set, get or delete) the format is:
                # :raises:
                #  * When assigned:
                #
                #    * RuntimeError (Invalid options)
                #
                #    * TypeError (Wrong type)
                #
                #  * When retrieved:
                #
                #    * RuntimeError (Null object)
                exoutput.append(':raises:')
                for action in ['setter', 'deleter', 'getter']:
                    desc = desc_dict[action]
                    for callable_root in callable_dict:
                        if callable_dict[callable_root]['type'] == action:
                            exlist = set(
                                callable_dict[callable_root]['exlist']
                            )
                            fexlist = [
                                _format_msg(
                                    '   * {name}'.format(name=name), width, 5
                                ) for name in sorted(list(exlist))
                            ]
                            exoutput.extend(
                                [
                                    ' * When {action}\n\n'.format(action=desc)+
                                    '\n\n'.join(fexlist)+'\n'
                                ]
                            )
        else:
            # For a regular callable (function or method) that raises only
            # one exception the format is:
            # :raises: RuntimeError (Invalid options)
            # For a regular callable (function or method) that raises multiple
            # exceptions the format is:
            # :raises:
            #  * RuntimeError (Invalid options)
            #
            #  * RuntimeError (Null object)
            exlist = set(callable_dict[next(iter(callable_dict))]['exlist'])
            exlength = len(exlist)
            indent = 1 if exlength == 1 else 3
            prefix = ':raises: ' if exlength == 1 else ' * '
            fexlist = [
                _format_msg(
                    '{prefix}{name}'.format(prefix=prefix, name=name),
                    width,
                    indent
                ) for name in sorted(list(exlist))
            ]
            exoutput.extend(
                [(':raises:\n' if exlength > 1 else '')+'\n\n'.join(fexlist)]
            )
        exoutput[-1] = '{line}\n\n'.format(line=exoutput[-1].rstrip())
        return ('\n'.join(exoutput)) if exoutput else ''

    # Managed attributes
    depth = property(_get_depth, _set_depth, doc='Call hierarchy depth')
    """
    Gets or sets the default hierarchy levels to include in the exceptions per
    callable. For example, a function :code:`my_func()` calls two other
    functions, :code:`get_data()` and :code:`process_data()`, and in turn
    :code:`get_data()` calls another function, :code:`open_socket()`. In this
    scenario, the calls hierarchy is::

            my_func            <- depth = 0
            ├get_data          <- depth = 1
            │└open_socket      <- depth = 2
            └process_data      <- depth = 1

    Setting :code:`depth=0` means that only exceptions raised by
    :code:`my_func()` are going to be included in the documentation; Setting
    :code:`depth=1` means that only exceptions raised by :code:`my_func()`,
    :code:`get_data()` and :code:`process_data()` are going to be included in
    the documentation; and finally setting :code:`depth=2` (in this case it has
    the same effects as :code:`depth=None`) means that only exceptions raised
    by :code:`my_func()`, :code:`get_data()`, :code:`process_data()` and
    :code:`open_socket()` are going to be included in the documentation.

    :rtype: non-negative integer

    :raises: RuntimeError (Argument \\`depth\\` is not valid)
    """

    exclude = property(
        _get_exclude, _set_exclude, doc='Modules and callables to exclude'
    )
    """
    Gets or sets the default list of (potentially partial) module and callable
    names to exclude from exceptions per callable. For example,
    :code:`['putil.ex']` excludes all exceptions from modules
    :py:mod:`putil.exh` and :py:mod:`putil.exdoc` (it acts as
    :code:`r'putil.ex*'`).  In addition to these modules,
    :code:`['putil.ex', 'putil.eng.peng']` excludes exceptions from the
    function :py:func:`putil.eng.peng`.

    :rtype: list

    :raises: RuntimeError (Argument \\`exclude\\` is not valid)
    """
