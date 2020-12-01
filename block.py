import time
from merkle_tree import MerkleTree
import pickle

class block:
    def __init__(self,height,transactions,prevBlockHash=''):
        self.height = height #int
        self.prevBlockHash = prevBlockHash #str
        self.transactions = transactions #list of transaction
        self.time = time.time() #float
        self.nonce = 0 #int
        self.hash = None #str

    def hash_transactions(self):
        tx_byte_list = []
        for tx in self.transactions:
            tx_byte_list.append(tx.ID)
        m_tree = MerkleTree(tx_byte_list)
        return m_tree.root.data

    def print(self):
        print("Block:",self.height)
        print("    PrevBlockHash:",self.prevBlockHash)
        for tx in self.transactions:
            print("    Transaction ID:",tx.ID)
            print("        TXInput:")
            for txin in tx.Vin:
                print("            TxID:",txin.Txid)
                print("            Vout:",txin.Vout)
                print("            Signature:",txin.Signature)
                print("            PubKey:",txin.PubKey)
            print("        TXOutput:")
            for txout in tx.Vout:
                print("            Value:",txout.Value)
                print("            PubKeyHash",txout.PubKeyHash)
        print("    Time:",self.time)
        print("    Nonce:",self.nonce)
        print("    Hash:",self.hash)