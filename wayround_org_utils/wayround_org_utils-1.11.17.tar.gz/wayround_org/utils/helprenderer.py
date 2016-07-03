
import inspect


def render_help(object_dic, order_list=None, only_titles=False, key=None):

    # FIXME: complete doc
    """
    Render Python function __doc__ text to help

    object_dic - dict with <'name':callable> structure.
    order_list - order in whch outut must be created
    only_titles - extract only titles(first lines) from callables __doc__ members
    key -
    """

    key_list = []

    if isinstance(order_list, list):
        if set(list(object_dic.keys())) != set(order_list):
            raise ValueError(
                "object_dic keys must be equal to order_list\n\n{}\n\n{}".format(
                    repr(set(list(object_dic.keys()))),
                    repr(set(order_list))
                    )
                )

        key_list = order_list

    else:
        key_list = list(object_dic.keys())

    for i in key_list:
        if not isinstance(i, str):
            raise ValueError("all keys must be of type str")

    out = ''

    for i in key_list:

        txt = ''
        if not key:
            txt = inspect.getdoc(object_dic[i])
        else:
            txt = inspect.getdoc(key(object_dic[i]))

        if isinstance(txt, str):
            txt = txt.strip()

        if isinstance(txt, list):
            txt = '\n'.join(txt)
        elif txt is None:
            txt = "(No documentation)"
        elif not isinstance(txt, str):
            txt = str(txt)

        if only_titles:
            txt = str(txt)
            txt = '        ' + txt.splitlines()[0].strip()
        else:
            text = ''
            for j in txt.splitlines():
                text += "        {}\n".format(j)

            txt = text

        out += (
            """\
    {key}
{help}
""".format(
                key=i,
                help=txt
                )
            )

    return out
