# Please fill in the config on lines 13 and 28 (blockchain RPC and SmartContract's raw ABI)
# Also, use a ~/.aws/config file for private config such as aws_access_key_id, aws_secret_access_key, region and output (BotoAWSRequestAuth will read these automatically if the file is present)

#IMPORTS
import json
import boto3 # pip3 install boto3
import requests
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth # pip3 install aws_requests_auth
from elasticsearch import Elasticsearch, RequestsHttpConnection # pip3 install elasticsearch 

# CONFIG
web3 = Web3(HTTPProvider('https://testnet-rpc.cybermiles.io:8545'))
host = 'search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com'
auth = BotoAWSRequestsAuth(aws_host='search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com', aws_region='ap-southeast-2', aws_service='es')
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    region='ap-southeast-2',
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

# FUNCTIONS
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

def loadDataIntoElastic(theContractName, thePayLoad):
    es.index(index=theContractName, body=thePayLoad)

# MAIN
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
                    Abi = fetchAbi()
                    outerData = {}
                    contractInstance = web3.eth.contract(abi=Abi, address=transactionContractAddress)
                    outerData['abiSha3'] = str(web3.toHex(web3.sha3(text=json.dumps(contractInstance.abi))))
                    outerData['blockNumber'] = transactionReceipt.blockNumber 
                    outerData['contractAddress'] = transactionReceipt.contractAddress
                    #print(contractInstance.all_functions())
                    callableFunctions = getPureOrViewFunctions()
                    for callableFunction in callableFunctions:
                        contract_func = contractInstance.functions[str(callableFunction)]
                        result = contract_func().call()
                        if type(result) is list:
                            if len(result) > 0:
                                innerData = {}
                                for i in range(len(result)):
                                    innerData[i] = result[i]
                                outerData[str(callableFunction)] = innerData
                        else:
                            outerData[str(callableFunction)] = result
                    print(json.dumps(outerData))
                    loadDataIntoElastic("fairplay", json.dumps(outerData))
            else:
                print("This transaction does not involve a contract, so we will ignore it")
                continue
    else:
        print("Skipping block number %s - No transactions found!" % blockNumber)
        continue
