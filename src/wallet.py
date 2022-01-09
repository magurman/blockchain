
from transaction import Transaction, TxOut, TxIn, signTxIn
from ecdsa import SigningKey, VerifyingKey, SECP256k1, NIST384p
import hashlib

from os.path import exists

def createTxOuts(recipientAddress, myAddress, amount, leftoverAmount):
    txOutRecipient = TxOut(recipientAddress, amount)
    if leftoverAmount == 0:
        return txOutRecipient

    txOutMe = TxOut(myAddress, leftoverAmount)
    return (txOutRecipient, txOutMe)

def findTxOutsForAmount(amount, myUnspentTxOuts):
    currentAmount = 0
    includedUnspentTxOuts = []
    for utxo in myUnspentTxOuts:
        includedUnspentTxOuts.append(utxo)
        currentAmount += utxo.amount
        if currentAmount >= amount:
            leftoverAmount = currentAmount - amount
            return (includedUnspentTxOuts, leftoverAmount)
    
    print("not enough coins!")
    #raise exception for not enough coins 

# THIS IS WRONG -- creating transaction is wrong because createTxOuts returns a tuple of transactions. might be simple as making a list out of those
def createTransaction(recipientAddress, amount, pk, unspentTxOuts):
    myAddress = getPublicFromPrivateKey(pk)
    myUnspentTxOuts = list(filter(lambda utxo: utxo.address == myAddress, unspentTxOuts))

    includedUnspentTxOuts, leftoverAmount = findTxOutsForAmount(amount, myUnspentTxOuts)

    unsignedTxIns = list(map(lambda utxo: TxIn(utxo.txOutputId, utxo.txOutputIndex, ''), includedUnspentTxOuts))

    tx = Transaction(unsignedTxIns, createTxOuts(recipientAddress, myAddress, amount, leftoverAmount))

    for index, txIn in enumerate(tx.getTxInputs()):
        txIn.setSignature(signTxIn(tx, index, pk, unspentTxOuts))
    
    return tx # make sure changes reflect in tx 

def getBalance(address, unspentTxOuts):
    unspentTxOutsForAddress = list(filter(lambda utxo: utxo.address == address, unspentTxOuts))
    unspentTxOutAmounts = list(map(lambda utxo: utxo.amount, unspentTxOutsForAddress))
    return sum(unspentTxOutAmounts)

def getVerifyingKeyFromSigningKey(sk):
    return sk.verifying_key

def getSigningKeyFromWalletLocation(pkLocation):
    with open(pkLocation, 'r') as file:
        keydata = file.read()

    return SigningKey.from_string(bytes.fromhex(keydata), curve=SECP256k1, hashfunc=hashlib.sha256)# the default is sha1

def writePkToFile(filepath, pk):
    with open(filepath, "w") as file:
        file.write(pk)

# maybe do some validation here 
def getPublicFromPrivateKey(pk):
    return SigningKey.from_string(bytes.fromhex(pk), curve=SECP256k1, hashfunc=hashlib.sha256) # the default is sha1.

def generatePrivateKey():
    sk = SigningKey.generate(curve=SECP256k1)
    return sk.to_string().hex()