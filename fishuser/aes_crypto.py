#!/usr/bin/env python
import os, base64
from Crypto.Cipher import AES



class AESCrypto:
    # the block size for the cipher object; must be 16, 24, or 32 for AES
    BLOCK_SIZE = 32
    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'
    # one-liner to sufficiently pad the text to be encrypted
    def pad(self, s):
        return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING
    # one-liners to encrypt/encode and decrypt/decode a string
    # encrypt with AES, encode with base64
    def EncodeAES(self, s):
        return base64.b64encode(self.cipher.encrypt(self.pad(s)))
    def DecodeAES(self, e):
        return self.cipher.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
    def __init__(self, secret=''):
        if secret:
            self.secret = secret
        else:
            # generate a random secret key
            self.secret = os.urandom(self.BLOCK_SIZE)

        # create a cipher object using the random secret
        self.cipher = AES.new(self.secret)



if __name__ == '__main__':
    ac = AESCrypto()
    # encode a string
    encoded = ac.EncodeAES('This is a TTTest')
    # decode the encoded string
    decoded = ac.DecodeAES(encoded)
    print decoded
