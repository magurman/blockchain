import hashlib
import time
import string

from flask import jsonify

class Block:

    def __init__(self, index, difficulty, data, previousHash):

        assert isinstance(index, int)
        assert isinstance(difficulty, int)
        assert isinstance(data, list)
        assert isinstance(previousHash, str)

        self.index = index
        self.difficulty = difficulty
        self.data = data
        self.previousHash = previousHash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.computeBlockHash()

    def computeBlockHash(self):
        sha256 = hashlib.sha256()

        data = self.data 
        data = list(map(lambda t: t.__str__(), data))
        dataStr = ''.join(data)

        hashStr = (str(self.index) + str(self.difficulty) + dataStr + self.previousHash + str(self.timestamp) + str(self.nonce)).encode('utf-8')
        sha256.update(hashStr)

        return sha256.hexdigest()

    def mine(self):
        while self.hash[0:self.difficulty] != self.getValidHashPrefix():
            print("hash calculated: ", self.hash)
            self.nonce += 1
            self.timestamp = time.time()
            self.hash = self.computeBlockHash()
            
        print("winning hash: ", self.getHash())
        print("number of hashes: ", self.nonce)

    def serialize(self):
        block = {
            "index": self.index,
            "difficulty": self.difficulty,
            "data": self.data,
            "hash": self.hash,
            "previousHash": self.previousHash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }
        return block

    def getDifficulty(self):
        return self.difficulty

    def getHash(self):
        return self.hash
    
    def getPreviousHash(self):
        return self.previousHash

    def getNonce(self):
        return self.nonce

    def getIndex(self):
        return self.index

    def getData(self):
        return self.data

    def getTimestamp(self):
        return self.timestamp

    def getValidHashPrefix(self):
        return self.difficulty * "0"