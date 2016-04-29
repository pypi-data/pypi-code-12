# Script to be run via 'zopectl run'.
#
# Installs the SSC as a '__before_traverse__' hook,, after first disabling
# the default '/session_data_manager'.
#

import transaction
from ZPublisher.BeforeTraverse import registerBeforeTraverse

from zope2.sessioncookie import ssc_hook


def main(root):
    sdm = root._getOb('session_data_manager', None)
    if sdm is not None:
        sdm.updateTraversalData(requestSessionName=None)

    registerBeforeTraverse(root, ssc_hook, 'sessioncookie', 50)
    root.sessioncookie_installed = True

    print('zope2.sessioncookie hook installed!')
    transaction.commit()


if __name__ == '__main__':
    main(root=app)
