import copy

transactionPool = []

def getTransactionPoolDeepCopy():
    return copy.deepcopy(transactionPool)

def addTransactionToTransactionPool(transaction, unspentTxOuts):
    if not transaction.validateTransaction(transaction, unspentTxOuts):
        print("invalid transaction")
        # raise error

    if not isValidTxForPool(transaction, transactionPool):
        print("invalid tx for transaction pool")
        # raise exception

    print("adding tx to tx pool")
    transactionPool.append(transaction)

def isValidTxForPool(transaction, transactionPool):
    txInsForPool = getTxPoolTxIns(transactionPool)

    txInsForTransaction = transaction.getTxInputs()

    # this needs to be tested -- what kind of equality is being checked here
    for txIn in txInsForTransaction:
        if txIn in txInsForPool:
            print("txIn for transaction already found in transactionPool txIns")
            return False

    return True

def getTxPoolTxIns(transactionPool):
    txPoolIns = list(map(lambda tx: tx.getTxInputs(), transactionPool))

    txPoolIns = [txIn for txIns in txPoolIns for txIn in txIns]

    return txPoolIns

def updateTransactionPool(unspentTxOuts):
    invalidTransactions = []
    for tx in transactionPool:
        for txIn in tx.getTxInputs():
            if not hasTxIn(txIn, unspentTxOuts):
                invalidTransactions.append(tx)
                break
        
    # will need to test this as well
    if len(invalidTransactions) > 0:
        print("removing transactions with invalid txIns")
        for tx in invalidTransactions:
            transactionPool.remove(tx)

def hasTxIn(txIn, unspentTxOuts):
        for utxo in unspentTxOuts:
            if utxo.txOutId == txIn.getTxOutputId() and utxo.txOutputIndex == txIn.getTxOutputIndex():
                return True
        return False

def getTransactionPool():
    return transactionPool