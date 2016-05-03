#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

class ChirpException(Exception):
    pass


class ChirpNetworkException(ChirpException):
    pass


class ChirpAuthenticationFailed(ChirpException):
    def __str__(self):
        return 'Authentication failed. Please check your credentials.'


class ChirpInvalidShortcodeException(ChirpException):
    def __str__(self):
        return ('Invalid shortcode. The shortcode contains characters not '
                'recognised by the Chirp engine.')


class ChirpInvalidLongcodeException(ChirpException):
    def __str__(self):
        return ('Invalid longcode. The longcode contains characters not '
                'recognised by the Chirp engine.')
