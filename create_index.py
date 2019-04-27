# Please provide:
# The RPC URL for the blockchain on line 10 and 
# The raw GitHub URL to the contract's ABI on line 14
# This program will go ahead and find your contract and index it 
from elasticsearch import Elasticsearch # pip3 install elasticsearch 
es=Elasticsearch([{'host':'https://search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com/','port':9200}])
import requests
import json
from web3 import Web3, HTTPProvider
web3 = Web3(HTTPProvider('https://testnet-rpc.cybermiles.io:8545'))


def fetchAbi():
    contractAbiFileLocation = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/dapp/FairPlay.abi"
    contractAbiFileData = requests.get(contractAbiFileLocation)
    contractAbiJSONData = json.loads(contractAbiFileData.content)
    return contractAbiJSONData

def createUniqueAbiComparisons():
    keccakHashes = []
    Abi = fetchAbi()
    for item in Abi:
        if item['type'] == 'function':
            if len(item['inputs']) == 0:
                stringToHash = str(item['name'] + '()')
                keccakHashes.append(str(web3.toHex(web3.sha3(text=stringToHash)))[2:10])
            else:
                tempString = ""
                tempString += item['name'] + '('
                iterator = 1
                for functionInput in item['inputs']:
                    if iterator == len(item['inputs']):
                        tempString += str(functionInput['type'] + ')')
                    else:
                        tempString += str(functionInput['type'] + ',')
                        iterator += 1
                stringToHash = tempString
                keccakHashes.append(str(web3.toHex(web3.sha3(text=stringToHash)))[2:10])
    return keccakHashes

def getPureOrViewFunctions():
    pureOrViewFunctions = []
    Abi = fetchAbi()
    for item in Abi:
        if item['type'] == 'function':
            if len(item['inputs']) == 0:
                if len(item['outputs']) > 0:
                    pureOrViewFunctions.append(str(item['name']))
    return pureOrViewFunctions

latestBlockNumber = web3.eth.getBlock('latest').number
print("Latest block is %s" % latestBlockNumber)

for blockNumber in reversed(range(1563539)):
    print("\nProcessing block number %s" % blockNumber)
    # Check to see if this block has any transactions in it
    blockTransactionCount = web3.eth.getBlockTransactionCount(blockNumber)
    if blockTransactionCount > 0:
        print("Transaction count: %s." % blockTransactionCount)
        block = web3.eth.getBlock(blockNumber)
        # We could loop through the transactions
        for singleTransaction in block.transactions:
            singleTransactionHex = singleTransaction.hex()
            print("Processing transaction hex: %s " % singleTransactionHex)
            # Get the transaction data
            transactionData = web3.eth.getTransaction(str(singleTransactionHex))
            # Get the transaction receipt
            transactionReceipt = web3.eth.getTransactionReceipt(str(singleTransactionHex))
            # Determine if this transaction is contract related
            transactionContractAddress = transactionReceipt.contractAddress
            if transactionContractAddress != None:
                print("Found contract address: %s " % transactionContractAddress)
                # We can now test the first 4 bytes of the Keccak hash of the ASCII form of all FairPlay.sol function signatures
                listOfKeccakHashes = createUniqueAbiComparisons()
                count = 0
                for individualHash in listOfKeccakHashes:
                    if individualHash in transactionData.input:
                        count += 1
                        print("Found a match: %s " % individualHash)
                if count == len(listOfKeccakHashes):
                    print("All hashes match!")
                    print("Contract address: %s " % transactionContractAddress)
                    # We can now call the contract functions at this address and store all of this data in the search engine
                    outerData = {}
                    outerData['blockNumber'] = transactionReceipt.blockNumber 
                    outerData['contractAddress'] = transactionReceipt.contractAddress
                    
                    Abi = fetchAbi()
                    contractInstance = web3.eth.contract(abi=Abi, address=transactionContractAddress)
                    #print(contractInstance.all_functions())
                    callableFunctions = getPureOrViewFunctions()
                    for callableFunction in callableFunctions:
                        contract_func = contractInstance.functions[str(callableFunction)]
                        result = contract_func().call()
                        outerData[str(callableFunction)] = result
                    print(json.dumps(outerData))
                    res = es.index(index='FairPlay', body=outerData)
            else:
                print("This transaction does not involve a contract, so we will ignore it")
                continue
    else:
        print("Skipping block number %s - No transactions found!" % blockNumber)
        continue
