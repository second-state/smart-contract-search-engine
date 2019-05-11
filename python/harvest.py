import os
import json
import boto3 
import requests
import configparser
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

class Harvest:
    def __init__(self):

        # CWD
        self.scriptExecutionLocation = os.getcwd()

        # Config
        print("Reading configuration file")
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.config.read(os.path.join(self.scriptExecutionLocation, 'config.ini'))

        # ABI (single abi)
        self.fairPlayAbi = self.config['abis']['fair_play_v_one']
        print("FairPlay ABI: %s" % self.fairPlayAbi)

        self.contractAbiFileData = requests.get(self.fairPlayAbi)
        print("ABI file data")
        print(self.contractAbiFileData)

        self.contractAbiJSONData = json.loads(self.contractAbiFileData.content)
        print("ABI JSON data")
        print(self.contractAbiJSONData)

        # ABI[s] possible future use, if storing abis in the configuration (for now use single abi option above)
        self.abis = {}
        for key in self.config['abis']:
            stringKey = str(key)
            self.abis[stringKey] = self.config['abis'][key]
        print("\nABIs:")
        for (ufaKey, ufaValue) in self.abis.items():
            print(ufaKey + ": " + ufaValue)
        # Blockchain RPC
        self.blockchainRpc = self.config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

        # Elasticsearch index
        self.elasticSearchIndex = self.config['elasticSearch']['index']
        print("ElasticSearch Index: %s" % self.elasticSearchIndex)

        # Elasticsearch endpoint
        self.elasticSearchEndpoint = self.config['elasticSearch']['endpoint']
        print("ElasticSearch Endpoint: %s" % self.elasticSearchEndpoint)

        # Elasticsearch AWS region
        self.elasticSearchAwsRegion = self.config['elasticSearch']['aws_region']

        # Web 3 init
        self.web3 = Web3(HTTPProvider(str(self.blockchainRpc)))

        # AWS Boto
        self.auth = BotoAWSRequestsAuth(aws_host=self.elasticSearchEndpoint, aws_region=self.elasticSearchAwsRegion, aws_service='es')
        self.es = Elasticsearch(
            hosts=[{'host': self.elasticSearchEndpoint, 'port': 443}],
            region=self.elasticSearchAwsRegion,
            use_ssl=True,
            verify_certs=True,
            http_auth=self.auth,
            connection_class=RequestsHttpConnection
        )

        #############################################
        # Functions
    def createUniqueAbiComparisons(self):
        keccakHashes = []
        for item in self.contractAbiJSONData:
            if item['type'] == 'function':
                if len(item['inputs']) == 0:
                    stringToHash = str(item['name'] + '()')
                    print("String to be hashed: %s" % stringToHash)
                    hashCreated = str(self.web3.toHex(self.web3.sha3(text=stringToHash)))[2:10]
                    print("Hash: %s" % hashCreated)
                    keccakHashes.append(hashCreated)
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
                    print("String to be hashed: %s" % stringToHash)
                    hashCreated = str(self.web3.toHex(self.web3.sha3(text=stringToHash)))[2:10]
                    print("Hash: %s" % hashCreated)
                    keccakHashes.append(hashCreated)
        return keccakHashes

    def loadDataIntoElastic(self, _theId, _thePayLoad):
        esReponseD = self.es.index(index=self.elasticSearchIndex, id=_theId, body=_thePayLoad)
        print("\n %s \n" % thePayLoad)
        return esReponseD

    def hasDataBeenIndexed(self, _esId):
        print("Checking for %s " % _esId)
        returnVal = False
        try:
            esReponse2 = self.es.get(index=self.elasticSearchIndex, id=_esId, _source="false")
            if esReponse2['found'] == True:
                returnVal = True
                print("Item is already indexed.")
        except:
            print("Item does not exist yet.")
        return returnVal

    def getPureOrViewFunctionNames(self):
        pureOrViewFunctions = []
        for item in self.contractAbiJSONData:
            if item['type'] == 'function':
                if len(item['inputs']) == 0:
                    if len(item['outputs']) > 0:
                        pureOrViewFunctions.append(str(item['name']))
        return pureOrViewFunctions

    def fetchPureViewFunctionData(self, _theContractInstance):
        callableFunctions = self.getPureOrViewFunctionNames()
        theFunctionData = {}
        for callableFunction in callableFunctions:
            contract_func = _theContractInstance.functions[str(callableFunction)]
            result = contract_func().call()
            if type(result) is list:
                if len(result) > 0:
                    innerData = {}
                    for i in range(len(result)):
                        innerData[i] = result[i]
                    theFunctionData[str(callableFunction)] = innerData
            else:
                theFunctionData[str(callableFunction)] = result
        return theFunctionData

    def getFunctionDataId(self, _theFunctionData):
        theId = str(self.web3.toHex(self.web3.sha3(text=json.dumps(_theFunctionData))))
        return theId

    def harvest(self, _stop=False):
        latestBlockNumber = self.web3.eth.getBlock('latest').number
        print("Latest block is %s" % latestBlockNumber)
        stopAtBlock = 0
        if _stop == True:
            stopAtBlock = latestBlockNumber - 350
        for blockNumber in reversed(range(stopAtBlock, latestBlockNumber)):
            print("\nProcessing block number %s" % blockNumber)
            # Check to see if this block has any transactions in it
            blockTransactionCount = self.web3.eth.getBlockTransactionCount(blockNumber)
            if blockTransactionCount > 0:
                print("Transaction count: %s." % blockTransactionCount)
                block = self.web3.eth.getBlock(blockNumber)
                # We could loop through the transactions
                for singleTransaction in block.transactions:
                    singleTransactionHex = singleTransaction.hex()
                    print("Processing transaction hex: %s " % singleTransactionHex)
                    # Get the transaction data
                    transactionData = self.web3.eth.getTransaction(str(singleTransactionHex))
                    # Get the transaction receipt
                    transactionReceipt = self.web3.eth.getTransactionReceipt(str(singleTransactionHex))
                    # Determine if this transaction is contract related
                    transactionContractAddress = transactionReceipt.contractAddress
                    if transactionContractAddress != None:
                        print("Found contract address: %s " % transactionContractAddress)
                        # We can now test the first 4 bytes of the Keccak hash of the ASCII form of all FairPlay.sol function signatures
                        listOfKeccakHashes = self.createUniqueAbiComparisons()
                        count = 0
                        for individualHash in listOfKeccakHashes:
                            if individualHash in transactionData.input:
                                count += 1
                                print("Found a match: %s " % individualHash)
                        if count == len(listOfKeccakHashes):
                            print("All hashes match!")
                            print("Contract address: %s " % transactionContractAddress)
                            try:
                                #Abi = fetchAbi()
                                outerData = {}
                                contractInstance = self.web3.eth.contract(abi=Abi, address=transactionContractAddress)
                                outerData['abiSha3'] = str(self.web3.toHex(self.web3.sha3(text=json.dumps(contractInstance.abi))))
                                outerData['blockNumber'] = transactionReceipt.blockNumber 
                                outerData['contractAddress'] = transactionReceipt.contractAddress
                                functionData = fetchPureViewFunctionData(contractInstance)
                                functionDataId = getFunctionDataId(functionData)
                                outerData['functionDataId'] = functionDataId
                                outerData['functionData'] = functionData
                                itemId = str(self.web3.toHex(self.web3.sha3(text=transactionReceipt.contractAddress)))
                                dataStatus = hasDataBeenIndexed(itemId)
                                if dataStatus == False:
                                    indexResult = loadDataIntoElastic(itemId, json.dumps(outerData))
                            except:
                                print("An exception occured! - Please try and load contract at address: %s manually to diagnose." % transactionContractAddress)
                    else:
                        print("This transaction does not involve a contract, so we will ignore it")
                        continue
            else:
                print("Skipping block number %s - No transactions found!" % blockNumber)
                continue



# Driver - Start
harvester = Harvest()
# Harvest everything
harvester.harvest()
# Harvest with a stop block
harvester.harvest(True)



# notes
# loadDataIntoElastic now only has 2 arguments because we get the index globally
# hasDataBeenIndexed also has no index arg anymore
