# from blockchain import Blockchain, getBlockchain, getFirstBlock
from block import Block

from flask import Flask, jsonify

def main():
    # blockchain = getBlockchain()
    block = Block(1,5,'', Block(0, 2, "First block!", "").getHash())
    block.mine()

    # print("blockchain size: ", len(getBlockchain().getChain()))
    # getBlockchain().addBlock(block)
    # print("blockchain size: ", len(getBlockchain().getChain()))


    # b2 = Block(2, 2, '', block.getHash())
    # getBlockchain().addBlock(b2)
    # print("blockchain size: ", len(getBlockchain().getChain()))

    # for i in range(5):
    #     blockchain.generateNewBlock("block: "+ str(i))

    # print("accumulated difficulty: ", blockchain.getChainAccumulatedDifficulty(blockchain))

    # app = Flask(__name__)

    # @app.route('/get_chain', methods=['GET'])
    # def getChain():
    #     res = {
    #         "chain": blockchain.serialize()
    #     }
    #     return res, 200

    # app.run(host='127.0.0.1', port=5000)

main()