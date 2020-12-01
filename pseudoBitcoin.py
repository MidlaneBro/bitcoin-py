import sys
import argparse
from blockchain import blockchain
import UTXO

def new_parser():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(help='commands')
    # A createwallet command
    tmp = sub_parser.add_parser('createwallet', help='Create a wallet and return an address')
    tmp.add_argument('-wallet', dest='wallet', action='store_true')
    # A createblockchain command
    tmp = sub_parser.add_parser('createblockchain', help='Create a blockchain with a coinbase TX (reward to address) inside the genesis block')
    tmp.add_argument('-address', type=str, dest='chain_address', required=True)
    # A getbalance command
    tmp = sub_parser.add_parser('getbalance', help='Get the account balance')
    tmp.add_argument('-address', type=str, dest='address', required=True)
    # A send command
    tmp = sub_parser.add_parser('send', help='Append new block containing one UTXO transaction inside')
    tmp.add_argument('-from', type=str, dest='from_address', required=True)
    tmp.add_argument('-to', type=str, dest='to_address', required=True)
    tmp.add_argument('-amount', type=int, dest='amount', required=True)
    # A printchain command
    tmp = sub_parser.add_parser('printchain', help='Print all the blocks of the blockchain')
    tmp.add_argument('-print', dest='print', action='store_true')
    #A printblock command
    tmp = sub_parser.add_parser('printblock',help='Print the block of specified height')
    tmp.add_argument('-height', type=int, dest='height', required=True)
    return parser
    

if __name__ == '__main__':
    parser = new_parser()
    args = parser.parse_args()
    bc = blockchain('database.pkl','wallet.pkl','UTXOset.pkl')

    if len(sys.argv)<2:
        print("Usage: pseudoBitcoin.py [-h] {createwallet,createblockchain,getbalance,send,printchain,printblock} ...")

    if hasattr(args,'wallet'):
        print("Your new address:",bc.newWallet())

    if hasattr(args,'chain_address'):
        if not bc.blocks:
            bc.newGenesisBlock(args.chain_address)
        else:
            print("Blockchain already exists")

    if hasattr(args,'address'):
        if bc.blocks:
            print("The balance of address %s is %d" % (args.address,bc.balance(args.address)))
        else:
            print("Please create blockchain first")

    if hasattr(args,'amount'):
        if bc.blocks:
            bc.newblock(args.from_address,args.to_address,args.amount)
        else:
            print("Please create blockchain first")

    if hasattr(args,'print'):
        if bc.blocks:
            bc.print()
        else:
            print("Blockchain doesn't exist")

    if hasattr(args,'height'):
        if len(bc.blocks) > args.height:
            bc.printblock(args.height)
        else:
            print("Block doesn't exist")