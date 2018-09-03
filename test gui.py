from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import base64

def encryption(privateInfo):
    """ Method to encrypt your message using AES encryption"""
    BLOCK_SIZE = 16
    PADDING = b'{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    #secret = os.urandom(BLOCK_SIZE)  # Comment this line and uncomment line below to use hard-coded key
    secret = b'\xf9J\xa4\xd1\t\x17\xb8\xabt\xfe\x06\x96\xe3\xe8(.'
    #print('Encryption key:', secret)
    cipher = AES.new(secret,AES.MODE_ECB)
    encoded = EncodeAES(cipher, privateInfo.encode('UTF-8'))
    return(encoded.decode('UTF-8'))


def decrypt_with_key(encryptedString):
    """ Method to decrypt message using a decryptionn key passed in as a parameter """
    key= b'\xf9J\xa4\xd1\t\x17\xb8\xabt\xfe\x06\x96\xe3\xe8(.'
    PADDING = '{'
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode('utf-8').rstrip(PADDING)
    cipher = AES.new(key,AES.MODE_ECB)
    decoded = DecodeAES(cipher, encryptedString)
    return(decoded)

xx = encryption("Sky6fall!ng")
print(xx)
xx = decrypt_with_key(xx)
print(xx)

