import unittest

from block import Block
from blockchain import getFirstBlock, validateNewBlock

class TestBlockchainFunctions(unittest.TestCase):
        
    def testValidateNewBlockInvalidIndex(self):
        currentBlock = getFirstBlock()
        newBlock = Block(2, 1, [], currentBlock.hash) #invalid index
        self.assertFalse(validateNewBlock(currentBlock, newBlock))

    def testValidateNewBlockInvalidPreviousHash(self):
        currentBlock = getFirstBlock()
        newBlock = Block(1, 1, [], '') #invalid previous hash
        self.assertFalse(validateNewBlock(currentBlock, newBlock))

    def testValidateNewBlockInvalidHash(self):
        currentBlock = getFirstBlock()
        newBlock = Block(1, 1, [], currentBlock.hash) 
        newBlock.hash = '' #invalid hash
        self.assertFalse(validateNewBlock(currentBlock, newBlock))

    def testValidateNewBlockInvalidHashPrefix(self):
        currentBlock = getFirstBlock()
        newBlock = Block(1, 1, [], currentBlock.hash) 
        self.assertFalse(validateNewBlock(currentBlock, newBlock))

    
if __name__ == '__main__':
    unittest.main()