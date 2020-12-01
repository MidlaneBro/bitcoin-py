import sys
import block
import hashlib

class proofOfWork:
    max_nonce = sys.maxsize
    target_bits = 11

    def __init__ (self,block):
        self.block = block
        self.target = 1<<(256-self.target_bits)

    def prepare_data(self,nonce):
        data_list = [self.block.prevBlockHash,self.block.hash_transactions(),str(int(self.block.time)),str(self.target_bits),str(nonce)]
        return (''.join(data_list)).encode()

    def run(self):
        nonce = 0
        print("Mining a new block")
        while nonce < self.max_nonce:
            data = self.prepare_data(nonce)
            hash_hex = hashlib.sha256(data).hexdigest()
            sys.stdout.write("%s \r" % (hash_hex))
            hash_int = int(hash_hex,16)
            if(hash_int) < self.target:
                break
            else:
                nonce += 1
        print("\n\n")
        return nonce,hash_hex

    def validate(self):
        data = self.prepare_data(self.block.nonce)
        hash_hex = hashlib.sha256(data).hexdigest()
        hash_int = int(hash_hex,16)
        return True if hash_int < self.target else False