# Script to be run via 'zopectl run'.
#
# Uninstalls the SSC as a '_before_traverse_' hook, and enables
# the default '/session_data_manager'.
#

import transaction
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

from zope2.sessioncookie import ssc_hook


def main(root):
    sdm = root._getOb('session_data_manager', None)
    if sdm is not None:
        sdm.updateTraversalData(requestSessionName='SESSION')

    unregisterBeforeTraverse(root, 'sessioncookie')
    root.sessioncookie_installed = False

    print('zope2.sessioncookie hook uninstalled!')
    transaction.commit()


if __name__ == '__main__':
    main(root=app)
