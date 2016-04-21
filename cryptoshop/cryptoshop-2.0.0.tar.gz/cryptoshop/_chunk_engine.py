#!/usr/bin/env python3
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

try:
    import botan
except:
    print("Please install the last version of Botan crypto library.")
    print("http://botan.randombit.net/#download")
    print("For Linux users, try to find it in your package manager.")
    sys.exit(0)

from ._nonce_engine import generate_nonce_timestamp
from ._settings import __chunk_size__, __gcmtag_length__, __nonce_length__


def encry_decry_chunk(chunk, key, algo, bool_encry, assoc_data):
    """
    When bool_encry is True, encrypt a chunk of the file with the key and a randomly generated nonce. When it is False,
    the function extract the nonce from the cipherchunk (first 16 bytes), and decrypt the rest of the chunk.
    :param chunk: a chunk in bytes to encrypt or decrypt.
    :param key: a 32 bytes key in bytes.
    :param algo: a string of algorithm. Can be "srp" , "AES" or "twf"
    :param bool_encry: if bool_encry is True, chunk is encrypted. Else, it will be decrypted.
    :param assoc_data: bytes string of additional data for GCM Authentication.
    :return: if bool_encry is True, corresponding nonce + cipherchunk else, a decrypted chunk.
    """
    engine = botan.cipher(algo=algo, encrypt=bool_encry)
    engine.set_key(key=key)
    engine.set_assoc_data(assoc_data)
    if bool_encry is True:
        nonce = generate_nonce_timestamp()
        engine.start(nonce=nonce)
        return nonce + engine.finish(chunk)
    else:
        nonce = chunk[:__nonce_length__]
        encryptedchunk = chunk[__nonce_length__:__nonce_length__ + __gcmtag_length__ + __chunk_size__]
        engine.start(nonce=nonce)
        decryptedchunk = engine.finish(encryptedchunk)
        if decryptedchunk == b"":
            raise Exception("Integrity failure: Invalid passphrase or corrupted data")
        else:
            return decryptedchunk
