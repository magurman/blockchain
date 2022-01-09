import functools
import hashlib
from ecdsa import SigningKey, VerifyingKey, SECP256k1, NIST384p

import string

class TxIn:
    
    def __init__(self, txOutputId, txOutputIndex, signature):
        self.txOutputId = txOutputId
        self.txOutputIndex = txOutputIndex
        self.signature = signature

    def getSignature(self):
        return self.signature

    def setSignature(self, signature):
        self.signature = signature

    def getTxOutputId(self):
        return self.txOutputId

    def getTxOutputIndex(self):
        return self.txOutputIndex

    def __hash__(self):
        hashObj = self.txOutputId + str(self.txOutputIndex)
        return hash(hashObj)

    def __eq__(self, other):
        return self.txOutputId == other.txOutputId and self.txOutputIndex == other.txOutputIndex

    def __str__(self):
        return self.txOutputId + str(self.txOutputIndex) + self.signature

class TxOut:

    def __init__(self, address, amount):
        self.address = address
        self.amount = amount

    def getAddress(self):
        return self.address

    def getAmount(self):
        return self.amount

    def __str__(self):
        return self.address + str(self.amount)

class UnspentTxOut:

    def __init__(self, txOutId, txOutIndex, address, amount):
        self._txOutId = txOutId
        self._txOutIndex = txOutIndex
        self._address = address
        self._amount = amount

    @property
    def txOutId(self):
        return self._txOutId

    @property
    def txOutIndex(self):
        return self._txOutIndex

    @property
    def address(self):
        return self._address

    @property
    def amount(self):
        return self._amount

class Transaction:

    def __init__(self, txInputs, txOutputs):

        self.id = getTransactionId(txInputs, txOutputs)
        self.txInputs = txInputs
        self.txOutputs = txOutputs

    def __str__(self):
        txInsStr = ''.join(list(map(lambda txIn: txIn.__str__(), self.txInputs)))
        txOutsStr = ''.join(list(map(lambda txOut: txOut.__str__(), self.txOutputs)))
        return self.id + txInsStr + txOutsStr

    def getId(self):
        return self.id

    def getTxInputs(self):
        return self.txInputs

    def getTxOutputs(self):
        return self.txOutputs

COINBASE_AMOUNT = 100

def validateTransactionsStructure(transactions):
    for transaction in transactions:
        if not isValidTransactionStructure(transaction):
            return False
    return True

def isValidTransactionStructure(transaction):
    # validate transaction id is string
    if not isinstance(transaction.getId(), str):
        print("transaction id must be string")
        return False
    
    # validate txIn is list 
    if not isinstance(transaction.getTxInputs(), list):
        print("transaction inputs must be in list")
        return False

    # validate all TxIn structure 
    for txIn in transaction.getTxInputs():
        if not isValidTxInStructure(txIn):
            print("all txIn must have valid structure")
            return False

    #validate TxOut is list 
    if not isinstance(transaction.getTxOutputs(), list):
        print("transaction outputs must be in list")
        return False

    # validate all TxOut structure 
    for txOut in transaction.getTxOutputs():
        if not isValidTxOutStructure(txOut):
            print("all txOut must have valid structure")
            return False

    return True 

def validateNewBlockTransactions(transactions, unspentTxOuts, blockIndex):
    coinbaseTx = transactions[0]
    validCoinbaseTx = validateCoinbaseTx(coinbaseTx, blockIndex)

    if not validCoinbaseTx:
        print("invalid coinbase transaction in block.")
        return False

    #check for duplicate txIns
    allTxIns = list(map(lambda tx: tx.getTxInputs(), transactions))
    txInsFlattened = [txIn for txIns in allTxIns for txIn in txIns]

    if not len(txInsFlattened) == len(set(txInsFlattened)):
        print("Cant have duplicate txIns!")
        return False
    
    #validate all all other transactions
    allOtherTransactions = transactions[1:]        
    allOtherTransactionsValidated = list(map(lambda tx: validateTransaction(tx, unspentTxOuts), allOtherTransactions))
    allOtherTransactionsValid = functools.reduce(lambda tx1, tx2: tx1 and tx2, allOtherTransactionsValidated, True)

    return allOtherTransactionsValid

def processTransactions(newTransactions, unspentTxOuts, blockIndex):
    # validate transaction structure 
    if not validateTransactionsStructure(newTransactions):
        print("transactions have invalid structure")
        return None

    # validate transactions 
    if not validateNewBlockTransactions(newTransactions, unspentTxOuts, blockIndex):
        print("invalid block transactions")
        return None

    # update and return unspentTxOuts
    return updateUnspentTxOuts(newTransactions, unspentTxOuts)

def updateUnspentTxOuts(newTransactions, unspentTxOuts):
    newTxOuts = []
    for newT in newTransactions:
        newTxOuts = []
        for index, newTxOut in enumerate(newT.getTxOutputs()):
            newTxOuts.append(UnspentTxOut(newT.getId(), index, newTxOut.getAddress(), newTxOut.getAmount()))

    newTxIns = list(map(lambda tx: tx.getTxInputs(), newTransactions))
    newTxInsFlattened = [txIn for txIns in newTxIns for txIn in txIns]
    consumedTxOuts = list(map(lambda txIn: UnspentTxOut(txIn.txOutputId, txIn.txOutputIndex, '', 0), newTxInsFlattened))

    newTxOutSet = set(newTxOuts)
    consumedTxOutSet = set(consumedTxOuts)
    unspentTxOutsSet = set(unspentTxOuts)

    newAndUnspentSet = newTxOutSet | unspentTxOutsSet
    unspentMinusConsumedSet = newAndUnspentSet - consumedTxOutSet

    return list(unspentMinusConsumedSet)

def validateCoinbaseTx(coinbaseTx, blockIndex):
    if coinbaseTx == None:
        print("Every block must contain a coinbaseTx!")
        return False

    if not getTransactionId(coinbaseTx.getTxInputs(), coinbaseTx.getTxOutputs()) == coinbaseTx.getId():
        print("invalid coinbaseTx with id: ", coinbaseTx.getId())
        return False

    if not len(coinbaseTx.getTxInputs()) == 1:
        print("coinbaseTx can only have one txInput!")
        return False

    if not coinbaseTx.getTxInputs()[0].getTxOutputIndex() == blockIndex:
        print('the txIn signature in coinbase tx must be the block height')
        return False

    if not len(coinbaseTx.getTxOutputs()) == 1:
        print('invalid number of txOuts in coinbase transaction')
        return False

    if not coinbaseTx.getTxOutputs()[0].getAmount() == COINBASE_AMOUNT:
        print("coinbase tx must have amount equal to coinbase amount: ", COINBASE_AMOUNT)
        return False

    return True

def getTransactionId(inputs, outputs):
    inputsContent = list(map(lambda txInput: txInput.txOutputId + str(txInput.txOutputIndex), inputs))
    inputsContent = functools.reduce(lambda x, y: x + y, inputsContent, '')
    
    outputsContent = list(map(lambda txOutput: txOutput.address + str(txOutput.amount), outputs))
    outputsContent = functools.reduce(lambda x, y: x + y, outputsContent, '')

    sha256 = hashlib.sha256()
    hashStr = (inputsContent + outputsContent).encode('utf-8')
    sha256.update(hashStr)

    return sha256.hexdigest()

def validateTransaction(transaction, unspentTxOuts):
    if not transaction.getId() == transaction.getTransactionId(transaction.getTxInputs(), transaction.getTxOutputs()):
        return False

    validTxIns = list(map(lambda txInput: validateTxIn(txInput, transaction, unspentTxOuts),transaction.getTxInputs()))
    hasValidTxIns = functools.reduce(lambda txIn1, txIn2: txIn1 and txIn2, validTxIns, True)

    if not hasValidTxIns:
        print("Some if the txIns are not valid.")
        return False

    txInAmounts = list(map(lambda txInput: getTxInAmount(txInput, unspentTxOuts), transaction.getTxInputs()))
    txInAmountsCumulative = functools.reduce(lambda x, y: x + y, txInAmounts, 0) 

    txOutAmounts = list(map(lambda txOut: txOut.getAmount(), transaction.getTxOutputs()))
    txOutAmountsCumulative = functools.reduce(lambda x, y: x + y, txOutAmounts, 0)

    if not txInAmountsCumulative == txOutAmountsCumulative:
        print("txInputAmounts NOT EQUAL to txOutputAmounts for transaction: ", transaction.getId())
        return False

    return True

def getTxInAmount(txIn, unspentTxOuts):
    return findUnspentTxOut(txIn.transactionId, txIn.transactionIndex, unspentTxOuts).amount

def findUnspentTxOut(transactionId, transactionIndex, unspentTxOuts):
    return next(filter(lambda unspentTxOut: unspentTxOut.txOutId == transactionId and unspentTxOut.txOutIndex == transactionIndex, unspentTxOuts), None)

def validateTxIn(txInput, transaction, unspentTxOuts):
    unspentTxOutId = txInput.txOutputId
    # unspentTxOutIndex = txInput.txOutputIndex

    referencedTxOut = next(filter(lambda unspentTxOut: unspentTxOut.txOutId == unspentTxOutId, unspentTxOuts), None)

    if referencedTxOut == None:
        print("Could not find referenced txOut")
        return False

    address = referencedTxOut.address

    vk = VerifyingKey.from_string(bytes.fromhex(address), curve=SECP256k1, hashfunc=hashlib.sha256) # the default is sha1

    valid = vk.verify(txInput.getSignature(), bytes.fromhex(transaction.getId()))

    return valid

# pk here might be passed as string so would need to convert
def signTxIn(transaction, txInIndex, pk, unspentTxOuts):
    txIn = transaction.getTxInputs()[txInIndex]
    dataToSign = txIn.getTxOutputId()
    referencedUnspentTxOut = findUnspentTxOut(txIn.getTxOutputId(),txIn.getTxOutputIndex(), unspentTxOuts)

    if referencedUnspentTxOut == None:
        print("could not find unspent tx out!")
        return  

    referencedAddress = referencedUnspentTxOut.address

    if (referencedAddress == getPublicKey(pk)):
        print("prviate key does not match private key of referenced tx out")
        return
    
    sk = SigningKey.from_pem(pk)
    sig = sk.sign(dataToSign)
    return sig

def createCoinbseTransaction(address, blockIndex):

    txIn = TxIn('', blockIndex, "")
    txOut = TxOut(address, COINBASE_AMOUNT)

    coinbaseTransaction = Transaction([txIn], [txOut])
    return coinbaseTransaction

def isValidTxInStructure(txIn):
    # make sure not null

    if txIn is None:
        print("txIn is None!")
        return False

    # make sure signature is string 
    if not isinstance(txIn.getSignature(), str):
        print("signature must be a string")
        return False 

    # make sure txOutid is string
    if not isinstance(txIn.getTxOutputId(), str):
        print("TxOutputId must be a string")
        return False 

    # make sure txOutindex is int 
    if not isinstance(txIn.getTxOutputIndex(), int):
        print("TxOutputId must be an integer")
        return False

    return True

def isValidTxOutStructure(txOut):
    
    # make sure not null
    if txOut == None:
        print("txOut is None!")
        return False

    # make sure address is string 
    if not isinstance(txOut.getAddress(), str):
        print("address must be a string")
        return False 

    # validate address
    if not isValidAddress(txOut.getAddress()):
        print("invalid address!")
        return False

    # make sure amount is int 
    if not isinstance(txOut.getAmount(), int):
        print("amount must be a string")
        return False 

    return True

def isValidAddress(address):
    if not len(address) == 130: #hardcoded?
        print("invalid public key length")
        return False
    elif not all(c in string.hexdigits for c in address):
        print("public key must only contain hex characters")
        return False
    elif not address.startswith('04'):
        print("public key must start with 04")
        return False
    
    return True

def getPublicKey(sk):
    #currently: being passed as string and need sk to be SigningKey object
    vk = sk.verifying_key
    return vk