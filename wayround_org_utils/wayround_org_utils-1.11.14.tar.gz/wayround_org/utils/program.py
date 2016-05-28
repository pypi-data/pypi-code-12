
import copy
import inspect
import logging
import sys
import threading
import time
import gc
import pprint

import wayround_org.utils.error
import wayround_org.utils.getopt
import wayround_org.utils.logging


NO_DOCUMENTATION = '(No documentation)'

DO_NOT_PRINT_EXIT_MESSAGE = 'showing help cmd list, no print'


def logging_setup(loglevel='INFO'):

    loglevel = loglevel.upper()

    # Logging settings
    for i in [
            (logging.CRITICAL, '[c]'),
            (logging.ERROR, '[e]'),
            (logging.WARN, '[w]'),
            (logging.WARNING, '[w]'),
            (logging.INFO, '[i]'),
            (logging.DEBUG, '[d]')
            ]:
        logging.addLevelName(i[0], i[1])
    del i

    opts = wayround_org.utils.getopt.getopt_keyed(sys.argv[1:])[0]

    # Setup logging level and format
    log_level = loglevel

    if '--loglevel' in opts:
        log_level_u = opts['--loglevel'].upper()

        if not log_level_u in wayround_org.utils.logging.LEVEL_NAMES:
            print("[e] Wrong --loglevel parameter")
        else:
            log_level = log_level_u

        del(opts['--loglevel'])
        del(log_level_u)

    logging.basicConfig(
        format="%(levelname)s %(message)s",
        level=log_level
        )

    return


def command_processor(
        command_name,
        commands,
        opts_and_args_list,
        additional_data
        ):

    opts, args = wayround_org.utils.getopt.getopt_keyed(opts_and_args_list)

    ret = dict(
        code=0,
        message='Default Exit',
        main_message="No Error"
        )

    args_l = len(args)

    subtree = commands

    level_depth = []

    for i in range(args_l):

        ii = args[i]

        if not ii in subtree:
            ret = dict(
                code=100,
                message='error',
                main_message="invalid command or subsection name"
                )
            break

        subtree = subtree[ii]
        level_depth.append(ii)

        if callable(subtree):
            break

    if ret['code'] != 0:
        pass
    else:

        args = args[len(level_depth):]

        args_l = len(args)

        show_help = '--help' in opts
        show_list = '--help-list' in opts

        if callable(subtree):

            if show_help:

                ret = {
                    'code': 0,
                    'message': "showing help",
                    'main_message': _format_command_help(level_depth, subtree)
                    }

            elif show_list:

                # TODO: print error

                ret = {
                    'code': 1,
                    'message': "error",
                    'main_message':
                        "--help-list param not applicable to final command"
                    }

            else:

                try:
                    res = subtree(
                        level_depth,
                        opts,
                        args,
                        additional_data
                        )
                except BrokenPipeError:
                    ret = dict(
                        code=1,
                        message="BrokenPipeError"
                        )
                except KeyboardInterrupt:
                    ret = dict(
                        code=1,
                        message='error',
                        main_message="Interrupted With Keyboard"
                        )
                except:
                    e = sys.exc_info()

                    ex_txt = wayround_org.utils.error.return_exception_info(
                        e,
                        tb=True
                        )

                    ret = dict(
                        code=1,
                        message='error',
                        main_message=(
                            "Error while executing command: {}\n{}".format(
                                ' '.join(level_depth),
                                ex_txt
                                )
                            )
                        )

                else:

                    if isinstance(res, int):
                        txt = None

                        if res == 0:
                            txt = 'No errors'
                        else:
                            txt = 'Some error'

                        ret = dict(
                            code=res,
                            message=txt
                            )
                    elif isinstance(res, dict):

                        ret = dict(
                            code=res['code'],
                            message='error',
                            main_message=res['message']
                            )

                    else:
                        ret = dict(
                            code=1,
                            message='error',
                            main_message=(
                                "Command returned not integer and not dict\n"
                                "(forcing exit code 1 and 'error' message)\n"
                                "Actually it has returned(type:{}):\n{}".format(
                                    type(res),
                                    res
                                    )
                                )
                            )

        elif isinstance(subtree, dict):

            if show_help:

                ret = {
                    'code': 0,
                    'message': "showing help",
                    'main_message': _format_command_level_help(
                        subtree,
                        level_depth
                        )
                    }

            elif show_list:

                ret = {
                    'code': 1,
                    'message': DO_NOT_PRINT_EXIT_MESSAGE,
                    'main_message': _format_command_list(
                        subtree,
                        level_depth
                        )
                    }

            else:

                ret = dict(
                    code=1,
                    message='error',
                    main_message=(
                        "Callable command not supplied. "
                        "May be try use --help param."
                        )
                    )

        else:
            raise ValueError("invalid command tree")

    return ret


def program(command_name, commands, additional_data=None):
    """
    command_name used only for help rendering purposes, so if not given --
    program name will not be rendered in help.

    this function uses command_processor() for command_processing, see it's
    documentation for explanations on parameters
    """

    ret = command_processor(
        command_name,
        commands,
        sys.argv[1:],
        additional_data
        )

    thrs = []

    thr = threading.enumerate()

    for i in thr:
        if isinstance(i, threading.Thread):
            thrs.append(i)

    #'''
    for i in thrs:
        if i.name != 'MainThread':
            gc.collect()
            # print("joining with {}".format(i))
            i.join()
    #'''

    if ret['message'] != DO_NOT_PRINT_EXIT_MESSAGE:

        mm = ret.get('main_message')

        if mm is not None:
            logging.info('{}'.format(mm))

        logging.info(
            "Exit Code: {} ({})".format(ret['code'], ret['message'])
            )

        thr = threading.enumerate()
        if len(thr) != 1:
            time.sleep(5)
            thr = threading.enumerate()
            if len(thr) != 1:
                logging.warning('-------------------------')
                logging.warning(
                    "Threading delay detected:\n{}".format(
                        pprint.pformat(thr)
                        )
                    )
                logging.warning(
                    "Trying to call garbage collector forcibly"
                    )
                logging.warning(
                    "Collection results. Unreachable objects: {}".format(
                        gc.collect()
                        )
                    )
                thr = threading.enumerate()
                if len(thr) != 1:
                    time.sleep(5)
                    thr = threading.enumerate()
                    if len(thr) != 1:
                        logging.error(
                            "Continued threading delay:\n{}".format(
                                pprint.pformat(thr)
                                )
                            )
                    else:
                        logging.info("Threading Cleanup Successful")
            else:
                logging.info('-------------------------')
                logging.info("Threding finished")

    return ret['code']


def _pthr_table(thr):
    thr_txt = pprint.pformat(thr)
    thr_txt = thr_txt.split('\n')
    for i in range(len(thr_txt)):
        thr_txt[i] = '       ' + thr_txt[i]
    thr_txt = '\n'.join(thr_txt)
    return thr_txt


def _format_command_help(level_depth, function):

    command_text = inspect.getdoc(function)

    if not isinstance(command_text, str):
        command_text = NO_DOCUMENTATION

    command_name_text = ' '.join(level_depth)

    ret = """\
Usage: {command_name_text} [options] [parameters]

{command_text}

""".format(
        command_text=command_text,
        command_name_text=command_name_text
        )

    return ret


def _format_command_list(subtree, level_depth):
    ret = None
    level = subtree

    if not hasattr(level, 'keys'):
        level = None

    if level is None:
        ret = None
    else:
        print('\n'.join(level.keys()))
        ret = ''

    return


def _format_command_level_help(subtree, level_depth):

    this_tree_help = NO_DOCUMENTATION
    command_name_text = ' '.join(level_depth)
    sections_text = ''
    subcommands_text = ''
    commands_text = ''

    if '_help' in subtree:
        this_tree_help = subtree['_help']

    for i in subtree.keys():

        if i == '_help':
            continue

        if callable(subtree[i]) or not isinstance(subtree[i], dict):
            continue

        command_help_text = NO_DOCUMENTATION

        if '_help' in subtree[i]:
            command_help_text = subtree[i]['_help']

        if isinstance(command_help_text, str):
            command_help_text = command_help_text.splitlines()[0].strip()

        sections_text += """\
    {cmd_name}
        {cmd_short_descr}

""".format(
            cmd_name=i,
            cmd_short_descr=command_help_text)

    for i in subtree.keys():

        if i == '_help':
            continue

        if not callable(subtree[i]):
            continue

        command_help_text = inspect.getdoc(subtree[i])

        if isinstance(command_help_text, str):
            command_help_text = command_help_text.splitlines()[0].strip()

        if not isinstance(command_help_text, str):
            command_help_text = NO_DOCUMENTATION

        commands_text += """\
    {cmd_name}
        {cmd_short_descr}

""".format(
            cmd_name=i,
            cmd_short_descr=command_help_text)

    this_tree_help_text = ''
    if this_tree_help != NO_DOCUMENTATION:
        this_tree_help_text = """\
{this_tree_help}
""".format(this_tree_help=this_tree_help)

    sub_sect_help_text = ''
    if sections_text != '':
        sub_sect_help_text = """\
sections:
{sect_text}
""".format(sect_text=sections_text)

    sub_comm_help_text = ''
    if commands_text != '':
        sub_comm_help_text = """\
commands:
{cmds_text}
""".format(cmds_text=commands_text)

    ret = "Usage: {command_name_text} [options] [parameters]\n".format(
        command_name_text=command_name_text
        )

    if this_tree_help_text != '':
        ret += '\n{}'.format(this_tree_help_text)

    if sub_sect_help_text != '':
        ret += '\n{}'.format(sub_sect_help_text)

    if sub_comm_help_text != '':
        ret += '\n{}'.format(sub_comm_help_text)

    ret += """\
    --help         help for section or command
    --help-list    list commands in section
"""

    print(ret)

    return
