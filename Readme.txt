1.Prerequisites
  pip install hashlib
  pip install base58
  pip install ecdsa

2.How to use my pseudo bitcoin
  (1)Create a wallet and get a random address(first step):
     python pseudoBitcoin.py createwallet
  (2)Create blockchain and give first mining reward to the given address:
     python pseudoBitcoin.py createblockchain -address {address}
  (3)Get balance of the address:
     python pseudoBitcoin.py getbalance -address {address}
  (4)Send a certain amount of coins from address1 to address2(this transaction will create a new block and reward address1):
     python pseudoBitcoin.py send -from {address1} -to {address2} -amount {amount}
  (5)Print the whole blockchain:
     python pseudoBitcoin.py printchain
  (6)Print the block of certain height in the blockchain(height counts from 0):
     python pseudoBitcoin.py printblock -height {height}
  (7)Help command:
     python pseudoBitcoin.py -h
  (8)Reset:
     rm database.pkl wallet.pkl UTXOset.pkl

3.The functionalities I've implemented
  (1)Prototype:Block,Blockchain,Proof-of-Work
  (2)Persistence:Database,Client
  (3)Transaction:UTXO
  (4)Address:Sign&Verify
  (5)Transaction:Mining reward,Merkle tree