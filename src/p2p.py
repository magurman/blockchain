
from flask import Flask, render_template
from flask_socketio import SocketIO, send

from block import Block

from blockchain import getBlockchain

from transaction import Transaction

from transactionPool import getTransactionPool

from enum import Enum

import asyncio

import json 

class MessageType(Enum):
    QUERY_LATEST = 0,
    QUERY_ALL = 1,
    RESPONSE_BLOCKCHAIN = 2,
    QUERY_TRANSACTION_POOL = 3,
    RESPONSE_TRANSACTION_POOL = 4

class Message:

    def __init__(self, messageType, data):
        self.messageType = messageType
        self.data = data

sockets = []

def initConnection(ws):
    sockets.append(ws)

    initMessageHandler(ws)

    initErrorHandler(ws)

    write(ws, queryChainLengthMsg())

    asyncio.sleep(0.5)
    broadcast(queryTransactionPoolMsg())

def queryChainLengthMsg():
    return Message(MessageType.QUERY_LATEST, None)

def queryAllMsg():
    return Message(MessageType.QUERY_ALL, None)

def queryTransactionPoolMsg():
    return Message(MessageType.QUERY_TRANSACTION_POOL, None)

def initErrorHandler(ws):
    return

def initMessageHandler(ws, socketio):

    @socketio.on('message')
    def handle_message(message):
        m = json.loads(message, object_hook=asMessage) # need to check if this was successful 

        messageType = m.messageType

        if messageType == MessageType.QUERY_ALL:
            write(ws, responseChainMsg()) 
        elif messageType == MessageType.QUERY_LATEST:
            write(ws, responseLatestMsg())
        elif messageType == MessageType.QUERY_TRANSACTION_POOL:
            write(ws, responseTransactionPoolMsg())
        elif messageType == MessageType.RESPONSE_BLOCKCHAIN:
            blocks = json.loads(message.data, object_hook=asBlock) # need to check if this was successful 
            handleBlockchainRespone(blocks)
        elif messageType == MessageType.RESPONSE_TRANSACTION_POOL:
            receivedTransactions = json.loads(message.data, object_hook=asTransaction) # need to check if this was successful -- how to serialized tx inputs/outputs?

            for tx in receivedTransactions:
                try:
                    handleReceivedTransaction(tx)
                    broadcastTransactionPool()
                except:
                    print("errro")

def broadcastTransactionPool():
    broadcast(responseTransactionPoolMsg())

def handleReceivedTransaction(transaction):
    tp = getTransactionPool()
    tp.addTransactionToTransactionPool(transaction,)
    return

def handleBlockchainRespone(blocks):
    receivedBlocksLength = len(blocks)

    if receivedBlocksLength == 0:
        print("received blockchain of size 0")
        return

    latestBlockReceived = blocks[receivedBlocksLength - 1]

    # need to valdiate latest block structure here

    latestBlockHeld = getBlockchain().getCurrentBlock()
    if latestBlockReceived.getIndex() > latestBlockHeld.getIndex():
        print('blockchain possibly behind. We got: '
            + latestBlockHeld.getIndex() + ' Peer got: ' + latestBlockReceived.getIndex())

        if latestBlockHeld.getHash() == latestBlockHeld.getPreviousHash():        
            if getBlockchain().addBlock(latestBlockReceived):
                broadcast(responseLatestMsg())
        elif receivedBlocksLength == 1:
            print("we have to query the chain from our peer")
            broadcast(queryAllMsg())
        else:
            print("received blockchain is longer than current blockchain")
            # MUST REPLACE THE CHAIN HERE. NOT SURE FUNCTION IMPL WAS CORRECT.
    else: 
        print("received blockchain is not longer than current blockchain. do nothing.")

def responseTransactionPoolMsg():
    # must json-stringify transaction pool here
    # return Message(MessageType.RESPONSE_TRANSACTION_POOL, NONE)
    return

def responseLatestMsg():
    return Message(MessageType.RESPONSE_BLOCKCHAIN, getBlockchain().getCurrentBlock().serialize())

def responseChainMsg():
    return Message(MessageType.RESPONSE_BLOCKCHAIN, getBlockchain().serialize())

def write(ws, message):
    # must send json-stringify of message
    return

def broadcast(message):
    for socket in sockets:
        write(socket, message)

def broadcastLatest():
    broadcast(responseLatestMsg())

def connectToPeers(newPeer):
    return

def initP2PServer(port):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app)
    socketio.run(app)

    @socketio.on('connect')
    def handle_connect(socketio):
        initConnection(socketio)
        
def asMessage(message):
    m = Message('', '')
    m.__dict__.update(message)
    return m

def asTransaction(transaction):
    t = Transaction([],[])
    t.__dict__.update(transaction)
    return t

def asBlock(block):
    b = Block(0,0,'','')
    b.__dict__.update(block)
    return b

if __name__ == '__main__':
    initP2PServer(5000)
    