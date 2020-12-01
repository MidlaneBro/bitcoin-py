import hashlib

class MerkleNode:
    def __init__ (self,left,right,data):
        if left is None and right is None:
            self.data = hashlib.sha256(data).hexdigest()
        else:
            self.data = hashlib.sha256((left.data+right.data).encode()).hexdigest()
        self.left = left
        self.right = right

class MerkleTree:
    def __init__(self,data_list):
        nodes = []
        if len(data_list) %2 != 0:
            data_list.append(data_list[-1])
        for data in data_list:
            nodes.append(MerkleNode(None,None,data))
        for i in range(len(data_list)//2):
            new_level = []
            for j in range(0,len(nodes),2):
                node = MerkleNode(nodes[j],nodes[j+1],None)
                new_level.append(node)
            nodes = new_level
        self.root = nodes[0]