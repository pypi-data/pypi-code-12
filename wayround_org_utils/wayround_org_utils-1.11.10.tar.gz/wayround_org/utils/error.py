
import sys
import traceback
import pprint


def return_instant_exception_info(tb=False):
    return return_exception_info(
        sys.exc_info(),
        tb=tb
        )


def return_exception_info(exc_info, tb=False):
    txt = """
EXCEPTION: {type}
    VALUE: {val}
""".format(
        type=repr(exc_info[0].__name__),
        val=repr(exc_info[1])
        )

    if tb:
        txt += """
TRACEBACK:
{tb}
{feo}
    """.format(
            tb=''.join(
                traceback.format_list(traceback.extract_tb(exc_info[2]))
                ),
            feo=''.join(
                traceback.format_exception_only(exc_info[0], exc_info[1])
                )
            )

    return txt


def print_exception_info(e):
    txt = return_exception_info(e)
    print(txt)
    return


def prompt(g=None, l=None, prompt='-> ', readline_=True):

    if readline_:
        import readline

    bk = False

    while not bk:

        try:
            cmd = input(prompt)
            try:
                e = eval(cmd, g, l)
                if isinstance(e, dict):
                    pprint.pprint(e, indent=2)
                else:
                    print(repr(e))
            except SyntaxError:
                exec(cmd, g, l)

        except EOFError:
            bk = True
        except:
            print(
                return_exception_info(
                    sys.exc_info(),
                    tb=True
                    )
                )

    print('')

    return

extract_stack = traceback.extract_stack
format_list = traceback.format_list
