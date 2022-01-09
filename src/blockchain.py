from block import Block
from flask import Flask, jsonify
from transaction import processTransactions, Transaction, TxIn, TxOut

import time
import functools

BLOCK_GENERATION_INTERVAL = 2 # seconds
DIFFICULTY_CHECK_INTERVAL = 10 # blocks

BLOCK_DIFFICULTY = 2

def validateNewBlock(currentBlock, newBlock):
    
    if not isinstance(newBlock, Block):
        print("new block not of type Block!")
        return False

    if not currentBlock.getIndex() == newBlock.getIndex() - 1: # 
        print("invalid index!")
        return False
    elif not currentBlock.getHash() == newBlock.getPreviousHash():
        print("invalid hash!")
        return False
    elif not newBlock.computeBlockHash() == newBlock.getHash():
        print("invalid computed hash!")
        return False
    elif not newBlock.getValidHashPrefix() == newBlock.getHash()[0:newBlock.getDifficulty()]:
        print("invalid hash prefix!")
        return False
    elif not validateTimestamp(currentBlock, newBlock):
        print("invalid timestamp!")
        return False
    

    print("valid block!")
    return True

# this is good place to start debug LOL
def validateTimestamp(currentBlock, newBlock):
    return newBlock.getTimestamp() - 60 < time.time() and currentBlock.getTimestamp() - 60 < newBlock.getTimestamp()

def getFirstBlock():
    return Block(0, 2, [genesisTransaction()], "")

def isBlockchainValid(blockchain):
    if not blockchain[0] == getFirstBlock():
        return False

    for i in range(1, len(blockchain)):
        if not validateNewBlock(blockchain[i], blockchain[i-1]):
            return False
    return True

def generateNewBlock(blockData):
    currentBlock = getCurrentBlock()
    newIndex = currentBlock.getIndex() + 1
    newBlock = Block(newIndex, BLOCK_DIFFICULTY, blockData, currentBlock.getHash())
    newBlock.mine()
    addBlock(newBlock)
    # broadcast()

def addBlock(newBlock):
    currentBlock = getCurrentBlock()
    if validateNewBlock(currentBlock, newBlock):
        myBlockchain.append(newBlock)

def getCurrentBlock():
        return myBlockchain[len(myBlockchain) - 1]

def getDifficulty():
    currentBlock = myBlockchain[len(myBlockchain) - 1]
    if currentBlock.getIndex() % DIFFICULTY_CHECK_INTERVAL == 0 and not currentBlock.getIndex() == 0:
        return getNewDifficulty(currentBlock)
    else:
        return currentBlock.getDifficulty()

def getNewDifficulty(block):
    lastAdjustedBlock = myBlockchain[len(myBlockchain) - DIFFICULTY_CHECK_INTERVAL]
    expectedTimeElapsed = BLOCK_GENERATION_INTERVAL * DIFFICULTY_CHECK_INTERVAL
    timeElapsed = block.getTimestamp() - lastAdjustedBlock.getTimestamp()

    if timeElapsed * 2 < expectedTimeElapsed: # took less than 1/2 time expected 
        return lastAdjustedBlock.getDifficulty() + 1
    elif timeElapsed / 2 > expectedTimeElapsed: # took more than 2x time expected 
        return lastAdjustedBlock.getDifficulty() - 1
    else: # OK
        return lastAdjustedBlock.getDifficulty()

def getChainAccumulatedDifficulty():
    blockDifficulties = list(map(lambda block: block.getDifficulty(), myBlockchain))
    accumulatedDifficulties = list(map(lambda difficulty: difficulty ** 2, blockDifficulties))
    return functools.reduce(lambda x, y: x + y, accumulatedDifficulties)

def mostWorkChain(self, newChain):

    if isBlockchainValid(newChain) and getChainAccumulatedDifficulty(newChain > getChainAccumulatedDifficulty(myBlockchain)):
        print("valid new chain and more work than current chain. updating chain")
        myBlockchain = newChain
        broadcast()
    else:
        print("new chain is invalid. not replacing")

def serializeBlockchain():
    serializedBlockchain = []
    for block in myBlockchain:
        serializedBlockchain.append(block.serialize())
    return serializedBlockchain

def getBlockchain():
    return myBlockchain

def genesisTransaction():
    txIn = TxIn('', 0, '')
    txOut = TxOut('04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a', 100)
    return Transaction([txIn], [txOut])

myBlockchain = [getFirstBlock()]
unspentTxOuts = processTransactions(myBlockchain[0].getData(), [], 0)