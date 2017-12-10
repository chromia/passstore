# -*- coding: utf-8 -*-

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import base64
import struct

# block padding character
padding = b'_'  # must be unused character on base64

# encoding method
encoding = 'utf-8'


class Cipher:
    def __init__(self, passphrase):
        # prepare key
        self.key = SHA256.new(passphrase.encode(encoding=encoding)).digest()

    def encode(self, rawtext):
        # type conversion : str -> byte
        rawdata = rawtext.encode(encoding=encoding)
        # base64 encode(for ease of padding)
        data = base64.b64encode(rawdata)
        # padding(for adjusting the length of the block)
        length = len(data)
        rest_size = length % AES.block_size
        if rest_size != 0:
            padding_size = AES.block_size - rest_size
            data += padding * padding_size
        return data

    def decode(self, data):
        # unpadding
        pad_pos = -1
        for index, c in enumerate(data):
            if c == padding:
                pad_pos = index
                break
        if pad_pos != -1:
            data = data[:pad_pos]
        # base64 decode
        rawdata = base64.b64decode(data)
        # type conversion : byte -> str
        rawtext = rawdata.decode(encoding=encoding)
        return rawtext

    def encrypt(self, rawdata):
        # rawdata is aligned in AES.block_size
        # initialize cipher
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        # encrypting
        message = iv + cipher.encrypt(rawdata)
        return message

    def decrypt(self, message, raw_digest):
        # parse message
        iv = message[:AES.block_size]
        encdata = message[AES.block_size:]
        # initialize cipher
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        # decrypting
        data = cipher.decrypt(encdata)
        new_raw_digest = self.calcdigest(data)
        if raw_digest == new_raw_digest:
            # descrypt success
            rawtext = self.decode(data)
            return (True, rawtext)
        else:
            # decrypt failed
            print('raw digest error')
            print(raw_digest)
            print(new_raw_digest)
            return (False, None)

    def save(self, filepath, rawtext):
        f = None
        try:
            f = open(filepath, "bw")
        except:
            return False
        else:
            # save three information with it's length in binary
            # 1. raw data digest( to confirm whether the keyphrase is correct or not )
            # 2. encoded data digest( as a checksum )
            # 3. encoded data
            rawdata = self.encode(rawtext)
            encdata = self.encrypt(rawdata)
            raw_digest = self.calcdigest(rawdata)
            enc_digest = self.calcdigest(encdata)
            len_raw_digest = len(raw_digest)
            len_enc_digest = len(enc_digest)
            len_enc_data = len(encdata)
            f.write(struct.pack('>L', len_raw_digest))
            f.write(raw_digest)
            f.write(struct.pack('>L', len_enc_digest))
            f.write(enc_digest)
            f.write(struct.pack('>L', len_enc_data))
            f.write(encdata)
            f.close()
            return True

    def load(self, filepath):
        f = None
        try:
            f = open(filepath, "br")
        except:
            return (False, None)
        else:
            size_L = struct.calcsize('>L')
            len_raw_digest = struct.unpack('>L', f.read(size_L))[0]
            raw_digest = f.read(len_raw_digest)
            len_enc_digest = struct.unpack('>L', f.read(size_L))[0]
            enc_digest = f.read(len_enc_digest)
            len_enc_data = struct.unpack('>L', f.read(size_L))[0]
            encdata = f.read(len_enc_data)
            f.close()
            new_enc_digest = self.calcdigest(encdata)
            if enc_digest == new_enc_digest:
                return self.decrypt(encdata, raw_digest)
            else:
                print('enc digest error')
                return (False, None)

    def calcdigest(self, data):
        h = SHA256.new(data)
        return h.digest()


if __name__ == '__main__':
    pass
