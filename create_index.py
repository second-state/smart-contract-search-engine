# Please provide:
# The RPC URL for the blockchain on line 5 and 
# The raw GitHub URL to the contract's ABI on line 8 
# This program will go ahead and find all instances of your contract and index them 

import requests
import json
from web3 import Web3, HTTPProvider
web3 = Web3(HTTPProvider('https://testnet-rpc.cybermiles.io:8545'))

def createUniqueAbiComparisons():
    keccakHashes = []
    contractAbiFileLocation = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/dapp/FairPlay.abi"
    contractAbiFileData = requests.get(contractAbiFileLocation)
    contractAbiJSONData = json.loads(contractAbiFileData.content)
    for item in contractAbiJSONData:
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

latestBlockNumber = web3.eth.getBlock('latest').number
print("Latest block is %s" % latestBlockNumber)

for blockNumber in reversed(range(latestBlockNumber)):
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
            else:
                print("This transaction does not involve a contract, so we will ignore it")
                continue
    else:
        print("Skipping block number %s - No transactions found!" % blockNumber)
        continue
