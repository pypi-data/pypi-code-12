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

import sys

from ._nonce_engine import generate_nonce_timestamp
from ._settings import __nonce_length__

try:
    import botan
except ImportError:
    print("Please install the last version of Botan crypto library.")
    print("http://botan.randombit.net/#download")
    print("For Linux users, try to find it in your package manager.")
    sys.exit(0)


def encry_decry_cascade(data, masterkey, bool_encry, assoc_data):
    """
    When bool_encry is True, encrypt the data with master key. When it is False, the function extract the three nonce
    from the encrypted data (first 3*21 bytes), and decrypt the data.
    :param data: the data to encrypt or decrypt.
    :param masterkey: a 32 bytes key in bytes.
    :param bool_encry: if bool_encry is True, data is encrypted. Else, it will be decrypted.
    :param assoc_data: Additional data added to GCM authentication.
    :return: if bool_encry is True, corresponding nonce + encrypted data. Else, the decrypted data.
    """
    engine1 = botan.cipher(algo="Serpent/GCM", encrypt=bool_encry)
    engine2 = botan.cipher(algo="AES-256/GCM", encrypt=bool_encry)
    engine3 = botan.cipher(algo="Twofish/GCM", encrypt=bool_encry)

    hash1 = botan.hash_function(algo="SHA-256")
    hash1.update(masterkey)
    hashed1 = hash1.final()

    hash2 = botan.hash_function(algo="SHA-256")
    hash2.update(hashed1)
    hashed2 = hash2.final()

    engine1.set_key(key=masterkey)
    engine1.set_assoc_data(assoc_data)

    engine2.set_key(key=hashed1)
    engine2.set_assoc_data(assoc_data)

    engine3.set_key(key=hashed2)
    engine3.set_assoc_data(assoc_data)

    if bool_encry is True:
        nonce1 = generate_nonce_timestamp()
        nonce2 = generate_nonce_timestamp()
        nonce3 = generate_nonce_timestamp()

        engine1.start(nonce=nonce1)
        engine2.start(nonce=nonce2)
        engine3.start(nonce=nonce3)

        cipher1 = engine1.finish(data)
        cipher2 = engine2.finish(cipher1)
        cipher3 = engine3.finish(cipher2)
        return nonce1 + nonce2 + nonce3 + cipher3
    else:
        nonce1 = data[:__nonce_length__]
        nonce2 = data[__nonce_length__:__nonce_length__ * 2]
        nonce3 = data[__nonce_length__ * 2:__nonce_length__ * 3]

        encrypteddata = data[__nonce_length__ * 3:]

        engine1.start(nonce=nonce1)
        engine2.start(nonce=nonce2)
        engine3.start(nonce=nonce3)

        decrypteddata1 = engine3.finish(encrypteddata)
        if decrypteddata1 == b"":
            raise Exception("Integrity failure: Invalid passphrase or corrupted data")
        decrypteddata2 = engine2.finish(decrypteddata1)
        if decrypteddata2 == b"":
            raise Exception("Integrity failure: Invalid passphrase or corrupted data")
        decrypteddata3 = engine1.finish(decrypteddata2)
        if decrypteddata3 == b"":
            raise Exception("Integrity failure: Invalid passphrase or corrupted data")
        else:
            return decrypteddata3
