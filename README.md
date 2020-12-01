# Prerequisites
    pip install hashlib
    pip install base58
    pip install ecdsa
    
# How to use my pseudo bitcoin
### Create a wallet and get a random address(first step)
    python pseudoBitcoin.py createwallet
### Create blockchain and give first mining reward to the given address
    python pseudoBitcoin.py createblockchain -address {address}
### Get balance of the address
    python pseudoBitcoin.py getbalance -address {address}
### Send a certain amount of coins from address1 to address2(this transaction will create a new block and reward address1)
    python pseudoBitcoin.py send -from {address1} -to {address2} -amount {amount}
### Print the whole blockchain
    python pseudoBitcoin.py printchain
### Print the block of certain height in the blockchain(height counts from 0)
    python pseudoBitcoin.py printblock -height {height}
### Help command
    python pseudoBitcoin.py -h
### Reset
    rm database.pkl wallet.pkl UTXOset.pkl

# The functionalities I've implemented
* Prototype:Block,Blockchain,Proof-of-Work
* Persistence:Database,Client
* Transaction:UTXO
* Address:Sign&Verify
* Transaction:Mining reward,Merkle tree
