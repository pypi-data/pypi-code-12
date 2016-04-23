#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Cryptoshop Strong file encryption.
# Encrypt and decrypt file in GCM mode with AES, Serpent or Twofish as secure as possible.
# Copyright(C) 2016 CORRAIRE Fabrice. antidote1911@gmail.com

# ############################################################################
# This file is part of Cryptoshop-GUI (full Qt5 gui for Cryptoshop).
#
#    Cryptoshop is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Cryptoshop is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cryptoshop.  If not, see <http://www.gnu.org/licenses/>.
# ############################################################################
"""

    Nonce Must be unique. They do not need to be kept secret and they can be included in a transmitted message.
    NIST recommends a 96-bit nonce length for performance critical situations but it can be up to 2^64 - 1 bits.
    http://csrc.nist.gov/groups/ST/toolkit/BCM/documents/proposedmodes/gcm/gcm-spec.pdf

    Reuse an nonce with a given key is CATASTROPHIC.
    ------------------------------------------------

    Generate nonce with RNG is not enough. RNG are sensible to collision.
    To make unique nonce, cryptoshop use a concatenation of an incremental counter, UUIDv4, and a random part generated
    by RNG.

"""

import botan
import uuid

count = 1


def generate_nonce_timestamp():
    """ Generate unique nonce with counter, uuid and rng."""
    global count
    rng = botan.rng().get(30)
    uuid4 = uuid.uuid4().bytes  # 16 byte
    tmpnonce = (bytes(str(count).encode('utf-8'))) + uuid4 + rng
    nonce = tmpnonce[:41]  # 41 byte (328 bit)
    count += 1
    return nonce
