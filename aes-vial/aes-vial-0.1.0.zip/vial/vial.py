# The MIT License (MIT)
#
# Vial - A simple wrapper for PyCrypto's AES CTR encryption.
# Version: 0.1.0
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''Vial is a simple wrapper for AES CTR mode. You have to set the key to
an appropriate length:

    AES-128bit (16 bytes/characters)
    AES-192bit (24 bytes/characters)
    AES-256bit (32 bytes/characters)

or use a hashing package that'll provide more security and ease your pain of
typing exactly the 16, 24 or 32 characters.

Usage:

    import vial

    vial = Vial(key)
    vial.encrypt(plaintext, output_counter_file)
    vial.decrypt(plaintext, output_counter_file)
    vial.encrypt_stream(input, output, block_size)
    vial.decrypt_stream(input, output, block_size)
'''

import os
import codecs
from Crypto.Cipher import AES
from Crypto.Util import Counter as Ctr


class Secret(object):
    '''Object that handles setting the random counter for AES CTR.'''
    def __init__(self, secret=None):
        if secret is None:
            secret = os.urandom(16)
        self.secret = secret
        IV = int(codecs.encode(secret, 'hex'), 16)
        self.counter = Ctr.new(128, initial_value=IV,
                               allow_wraparound=True)


class Vial(object):
    '''Object providing functions calling AES CTR encrypting & decrypting
functions.

Check Vial.encrypt(), Vial.decrypt(), Vial.encrypt_stream() and
Vial.decrypt_stream()
    '''
    def __init__(self, key):
        self.key = key

    def encrypt(self, text, counter_path):
        '''This function needs as an extra argument a path where you want
the file with initial Counter value stored. The file is important,
you need to use it to decrypt.

        Returns:

            encrypted text (bytes)
        '''
        self.secret = Secret()
        with open(counter_path, 'wb') as f:
            f.write(self.secret.secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=self.secret.counter)
        encrypted = crypto.encrypt(text)
        return encrypted

    def decrypt(self, text, counter_path):
        '''This function needs as an extra argument the path where you saved
the file from Vial.encrypt(). Without this file the text won't be
decrypted.

        Returns:

            decrypted text (bytes)
        '''
        with open(counter_path, 'rb') as f:
            load_secret = f.read()
        self.secret = Secret(secret=load_secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=self.secret.counter)
        decrypted = crypto.decrypt(text)
        return decrypted

    def encrypt_stream(self, input, output, block_size=4096):
        '''This function needs as extra arguments only input file and a path
for the output file. A file with Counter's initial value will be
created automatically in the same location and with the same name as
output file.

        Args:

            input, output: Expects a file object ( f = open(...) )
            block_size (optional): The max block_size to encrypt with the same
                                   AES encrypt()

        Example:

            vial = Vial(key)
            input = open('encrypt_me.png', 'rb')
            output = open('im_encrypted.png', 'wb')
            vial.encrypt_stream(input, output)
            input.close()
            output.close()

            Result:

                root/
                    encrypt_me.png
                    im_encrypted.png
                    im_encrypted.ctr
        '''
        self.secret = Secret()
        counter_path = os.path.splitext(output.name)[0] + '.ctr'
        with open(counter_path, 'wb') as f:
            f.write(self.secret.secret)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=self.secret.counter)
        while True:
            data = input.read(block_size)
            if not data:
                break
            data = crypto.encrypt(data)
            output.write(data)

    def decrypt_stream(self, input, output, block_size=4096):
        '''This function needs as extra arguments only input file and a path
for the output file. The file with Counter's initial value has to be
placed in the same folder as the input file as the function
automatically checks for it and gets the value to decrypt it.

        Args:

            input, output: Expects a file object ( f = open(...) )
            block_size (optional): The max block_size to decrypt with the same
                                   AES decrypt()

        Example:

            vial = Vial(key)
            input = open('im_encrypted.png', 'rb')
            output = open('im_decrypted.png', 'wb')
            vial.encrypt_stream(input, output)
            input.close()
            output.close()

            Result:

                root/
                    im_encrypted.png
                    im_encrypted.ctr
                    im_decrypted.png
        '''
        counter_path = os.path.splitext(input.name)[0] + '.ctr'
        with open(counter_path, 'rb') as f:
            counter_read = f.read()
        self.secret = Secret(secret=counter_read)
        crypto = AES.new(self.key, AES.MODE_CTR, counter=self.secret.counter)
        while True:
            data = input.read(block_size)
            if not data:
                break
            data = crypto.decrypt(data)
            output.write(data)


if __name__ == '__main__':
    root_path = os.path.abspath(os.path.dirname(__file__))
    key32 = '0123456789' * 3 + 'QW'
    vial = Vial(key32)
    path = root_path + '/vial_test.ctr'
    enc = vial.encrypt(16 * 'a', path)
    print('enc:\n', enc, len(enc))

    vial = Vial(key32)
    path = root_path + '/vial_test.ctr'
    dec = vial.decrypt(enc, path)
    print('\ndec:\n', dec, len(dec))

    vial = Vial(key32)
    finput = open(root_path + '/encrypt_me.png', 'rb')
    foutput = open(root_path + '/im_encrypted.png', 'wb')
    vial.encrypt_stream(finput, foutput)
    finput.close()
    foutput.close()

    vial = Vial(key32)
    finput = open(root_path + '/im_encrypted.png', 'rb')
    foutput = open(root_path + '/im_decrypted.png', 'wb')
    vial.decrypt_stream(finput, foutput)
    finput.close()
    foutput.close()
