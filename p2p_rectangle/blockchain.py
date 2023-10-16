import hashlib

class Block:
    def __init__(self,data,prev_hash) -> None:
        self.data=data
        self.prev_hash=prev_hash
        self.hash=self.calc_hash()
    
    def calc_hash(self):
        sha=hashlib.sha256()
        sha.update(self.data.encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self) -> None:
        self.chain=[self.create_start_block()]

    def create_start_block(self):
        return Block("start Block","0")

    def add_block(self,data):
        prev_block=self.chain[-1]
        new_block=Block(data,prev_block.hash)
        self.chain.append(new_block)


    def print_chain(self):
        for i in self.chain:
            print(i.data)
            print(i.prev_hash)













