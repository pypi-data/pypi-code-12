
import re
import logging

NEW_DICT_KEY_TEMPLATE = '{last_placer_child_name}_auto_appended_key_{num:010d}'
LAST_DICT_KEY_CHECK_RE = r'(.*)_auto_appended_key_(\d{10})'


def append(indict, what_to_append):

    last_name = max(indict)

    re_val = re.match(LAST_DICT_KEY_CHECK_RE, last_name)

    placement_i = 0

    if re_val:
        placement_i = int(re_val.group(2)) + 1
        new_key = NEW_DICT_KEY_TEMPLATE.format_map(
            {
                'last_placer_child_name': re_val.group(1),
                'num': placement_i
                }
            )
    else:
        new_key = NEW_DICT_KEY_TEMPLATE.format_map(
            {
                'last_placer_child_name': last_name,
                'num': placement_i
                }
            )

    logging.debug("Adding dict key: `{}'".format(new_key))
    indict[new_key] = what_to_append

    return
