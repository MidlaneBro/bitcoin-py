from ecdsa import SigningKey
import hashlib
import base58

class Wallet:
    def __init__ (self):
        self.PrivateKey = SigningKey.generate()
        self.PublicKey = self.PrivateKey.verifying_key
        self.hash_Publickey = self.hashPublicKey() #str
        self.address = self.getAddress() #str

    def hashPublicKey(self):
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(self.PublicKey.to_string()).hexdigest().encode())
        return ripemd160.hexdigest()

    def getAddress(self):
        versionPayload = ('00' + self.hash_Publickey).encode()
        checksum = hashlib.sha256(hashlib.sha256(versionPayload).hexdigest().encode()).hexdigest()[0:4].encode()
        fullPayload = versionPayload + checksum
        return base58.b58encode(fullPayload).decode()
