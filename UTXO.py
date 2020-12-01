import sys
import pickle
import hashlib
import base58
from ecdsa import SigningKey

class TXInput:
    def __init__ (self,id,vout,sig,key):
        self.Txid = id #bytes #從哪個transaction來的ID
        self.Vout = vout #int #該transaction的第幾個Vout
        self.Signature = sig
        self.PubKey = key
    
    def usesKey(self,pubKeyHash):
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(self.PubKey.to_string()).hexdigest().encode())
        lockinghash = ripemd160.hexdigest()
        return lockinghash == pubKeyHash

class TXOutput:
    def __init__ (self,value,address):
        self.Value = value #int #real money
        self.address = address #str
        self.PubKeyHash = self.lock(address) #str

    def lock(self,address):
        pubKeyHash = base58.b58decode(address)
        pubKeyHash = pubKeyHash[1:len(pubKeyHash)-4]
        return pubKeyHash.decode()

    def IsLockedWithKey(self,pubKeyHash):
        return self.PubKeyHash[1:] == pubKeyHash

class Transaction:
    def __init__ (self,id,vin,vout):
        self.ID = id #bytes
        self.Vin = vin #list of TXInput
        self.Vout = vout #list of TXOutput

    def setID(self):
        self.ID = hashlib.sha256(pickle.dumps(self)).hexdigest().encode()

    def hash(self):
        return hashlib.sha256(pickle.dumps(self)).hexdigest().encode()

    def trimmedCopy(self): #return a copy without signature and pubkey in txinput
        inputs = [] #list of TXInput
        outputs = [] #list of TXOutput
        for vin in self.Vin:
            inputs.append(TXInput(vin.Txid,vin.Vout,None,None))
        for vout in self.Vout:
            outputs.append(TXOutput(vout.Value,vout.address))
        return Transaction(self.ID,inputs,outputs)

    def sign(self, privKey, prevTXs):
        for vin in self.Vin:
            if not prevTXs[vin.Txid.decode()].ID:
                print("Previous transaction is not correct") 
                sys.exit()
        txCopy = self.trimmedCopy()
        for inTD, vin in enumerate(txCopy.Vin):
            prevTx = prevTXs[vin.Txid.decode()]
            txCopy.Vin[inTD].Signature = None
            txCopy.Vin[inTD].PubKey = prevTx.Vout[vin.Vout].PubKeyHash
            txCopy.ID = txCopy.hash()
            txCopy.Vin[inTD].PubKey = None
            self.Vin[inTD].Signature = privKey.sign(txCopy.ID)

    def verify(self, prevTXs):
        for vin in self.Vin:
            if not prevTXs[vin.Txid.decode()].ID:
                print("Previous transaction is not correct")
                sys.exit()
        txCopy = self.trimmedCopy()
        for inTD, vin in enumerate(self.Vin):
            prevTx = prevTXs[vin.Txid.decode()]
            txCopy.Vin[inTD].Signature = None
            txCopy.Vin[inTD].PubKey = prevTx.Vout[vin.Vout].PubKeyHash
            txCopy.ID = txCopy.hash()
            txCopy.Vin[inTD].PubKey = None
            if not vin.PubKey.verify(self.Vin[inTD].Signature,txCopy.ID):
                return False
        return True