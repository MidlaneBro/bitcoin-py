import pickle
from block import block
from pow import proofOfWork
import sys
import UTXO
from wallet import Wallet
import os

class blockchain:
    def __init__(self,db_file,wallet_file,UTXOset_file):
        self.subsidy = 50
        self.db_file = db_file
        self.wallet_file = wallet_file
        self.UTXOset_file = UTXOset_file
        try:
            with open(db_file,'rb') as f:
                self.blocks = pickle.load(f)
        except FileNotFoundError:
            self.blocks = [] #list of block
            f = open(db_file,'wb')
            pickle.dump(self.blocks,f)
        try:
            with open(wallet_file,'rb') as f:
                self.wallets = pickle.load(f)
        except FileNotFoundError:
            self.wallets = [] #list of wallet
            f = open(wallet_file,'wb')
            pickle.dump(self.wallets,f)
        try:
            with open(UTXOset_file,'rb') as f:
                self.UTXOset = pickle.load(f)
        except FileNotFoundError:
            self.UTXOset = {} #key:TxID(str),value:list_of_TXOutput
            f = open(UTXOset_file,'wb')
            pickle.dump(self.UTXOset,f)

    #initialize UTXOset
    def reindex(self):
        self.UTXOset = self.findUTXO()
        f = open(self.UTXOset_file,'wb')
        pickle.dump(self.UTXOset,f)

    #update UTXOset whenever a new block is created
    def update(self):
        for tx in self.blocks[-1].transactions:
            if tx.Vin[0].Vout != -1: #non-coinbasetransaction
                for vin in tx.Vin:
                    update_outs = []
                    outs = self.UTXOset[vin.Txid.decode()]
                    for outIdx, out in enumerate(outs):
                        if outIdx != vin.Vout:
                            update_outs.append(out)
                    if not update_outs:
                        del self.UTXOset[vin.Txid.decode()]
                    else:
                        self.UTXOset[vin.Txid.decode()] = update_outs
            new_outputs = [out for out in tx.Vout]
            self.UTXOset[tx.ID.decode()] = new_outputs

    def newWallet(self):
        w = Wallet()
        self.wallets.append(w)
        f = open(self.wallet_file,'wb')
        pickle.dump(self.wallets,f)
        return self.wallets[-1].address

    def findWallet(self,address):
        for wallet in self.wallets:
            if wallet.address == address:
                return wallet
        print("Address not found")
        sys.exit()

    def newGenesisBlock(self,address):
        transactions = [self.newCoinBaseTransaction(address)]
        b = block(0,transactions)
        pow = proofOfWork(b)
        nonce, hash = pow.run()
        b.hash = hash
        b.nonce = nonce
        self.blocks.append(b)
        f = open(self.db_file,'wb')
        pickle.dump(self.blocks,f)
        self.reindex()
        f = open(self.UTXOset_file,'wb')
        pickle.dump(self.UTXOset,f)

    def newblock(self,from_address,to_address,amount):
        transactions = [self.newUTXOTransaction(from_address,to_address,amount)]
        for tx in transactions:
            if not self.verifyTransaction(tx):
                print("Error:Invalid transaction")
                sys.exit()
        transactions.append(self.newCoinBaseTransaction(from_address))
        b = block(len(self.blocks),transactions,self.blocks[-1].hash)
        pow = proofOfWork(b)
        nonce, hash = pow.run()
        b.hash = hash
        b.nonce = nonce
        self.blocks.append(b)
        f = open(self.db_file,'wb')
        pickle.dump(self.blocks,f)
        self.update()
        f = open(self.UTXOset_file,'wb')
        pickle.dump(self.UTXOset,f)
        
    def print(self):
        for block in self.blocks:
            block.print()

    def printblock(self,height):
        self.blocks[height].print()
    
    def newCoinBaseTransaction(self,address):
        wallet = self.findWallet(address)
        txin = [UTXO.TXInput(os.urandom(64),-1,None,wallet.PublicKey)]
        txout = [UTXO.TXOutput(self.subsidy,address)]
        tx = UTXO.Transaction(None,txin,txout)
        tx.setID()
        return tx

    def newUTXOTransaction(self,from_address,to_address,amount):
        inputs = []
        outputs = []
        from_wallet = self.findWallet(from_address)
        acc, validOutputs = self.findSpendableOutputs(from_wallet.hash_Publickey,amount)
        if acc < amount:
            print("Error: Not enough funds")
            sys.exit()
        #Build a list of inputs
        for txid, outs in validOutputs.items():
            txID = txid.encode()
            for out in outs:
                inputs.append(UTXO.TXInput(txID,out,None,from_wallet.PublicKey))
        #Build a list of outputs
        outputs.append(UTXO.TXOutput(amount,to_address))
        if acc > amount:
            outputs.append(UTXO.TXOutput(acc-amount,from_address)) #change
        tx = UTXO.Transaction(None,inputs,outputs)
        tx.setID()
        self.signTransaction(tx,from_wallet.PrivateKey)
        return tx

    #find all unspent UTXO outputs
    def findUTXO(self):
        UTXO = {} #key:TxID(str),value:list_of_TXOutput
        spentTXOs = {} #key:TXinput.Txid,value:TXinput.Vout
        #find spentTXOs by traversing TXin
        for block in self.blocks:
            for tx in block.transactions:
                if tx.Vin[0].Vout != -1: #non-coinbasetransaction
                    for txin in tx.Vin:
                        txinID = txin.Txid.decode()
                        if txinID not in spentTXOs:
                            spentTXOs[txinID] = []
                        spentTXOs[txinID].append(txin.Vout)
        #Pick up those TXOs that are not in spentTXOs
        for block in self.blocks:
            for tx in block.transactions:
                txID = tx.ID.decode()
                for outIdx, out in enumerate(tx.Vout):
                    flag = True
                    if txID in spentTXOs:
                        for spentOut in spentTXOs[txID]:
                            if spentOut == outIdx:
                                flag = False
                    if flag:
                        if txID not in UTXO:
                            UTXO[txID] = []
                        UTXO[txID].append(out)
        return UTXO

    #return unspent transaction outputs of given pubkeyhash based on the given amount
    def findSpendableOutputs(self,pubKeyHash,amount):
        Outputs = {} #key:TxID(str),value:outIdx
        accumulated = 0
        #pick up those TXOs that match pubkeyhash in the UTXOset until the amount is fulfilled
        for txID, outs in self.UTXOset.items():
            for outIdx, out in enumerate(outs):
                if out.IsLockedWithKey(pubKeyHash) and accumulated < amount:
                    accumulated += out.Value
                    if txID not in Outputs:
                        Outputs[txID] = []
                    Outputs[txID].append(outIdx)
        return accumulated, Outputs

    #return balance of an address
    def balance(self,address):
        sum = 0
        pubKeyHash = self.findWallet(address).hash_Publickey
        for outs in self.UTXOset.values():
            for out in outs:
                if out.IsLockedWithKey(pubKeyHash):
                    sum += out.Value
        return sum

    def findTransaction(self,ID):
        for block in self.blocks:
            for tx in block.transactions:
                if tx.ID == ID:
                    return tx
        print("Transaction not found")
        sys.exit()

    def signTransaction(self,tx,privKey):
        prevTXs = {}
        for vin in tx.Vin:
            prevTX = self.findTransaction(vin.Txid)
            prevTXs[prevTX.ID.decode()] = prevTX
        tx.sign(privKey,prevTXs)

    def verifyTransaction(self,tx):
        prevTXs = {}
        for vin in tx.Vin:
            prevTX = self.findTransaction(vin.Txid)
            prevTXs[prevTX.ID.decode()] = prevTX
        return tx.verify(prevTXs)