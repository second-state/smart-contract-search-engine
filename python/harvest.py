import os
import sys
import time
import json
import boto3 
import argparse
import requests
import threading
import configparser
import elasticsearch.helpers
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

        # ABI[s] Allow for multiple ABIs in the config.ini
        self.abis = {}
        for key in self.config['abis']:
            stringKey = str(key)
            tempData = {}
            tempData["url"] = self.config['abis'][key]
            tempData["json"] = requests.get(self.config['abis'][key]).content
            self.abis[stringKey] = tempData
        # Print the ABIs
        print("\nABIs:")
        for (outerKey, outerValue) in self.abis.items():
            print("%s:" % outerKey)
            for innerKey, innerValue in outerValue.items():
                print("\t %s" % innerKey)
                print("\t %s" % innerValue)
            
        # Blockchain RPC
        self.blockchainRpc = self.config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

        # Elasticsearch index - This is now derived from the ABI key name in the config.ini
        #self.elasticSearchIndex = self.config['elasticSearch']['index']
        #print("ElasticSearch Index: %s" % self.elasticSearchIndex)

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
    def createUniqueAbiComparisons(self, _contractAbiJSONData):
        keccakHashes = []
        for item in _contractAbiJSONData:
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

    def loadDataIntoElastic(self, _theIndex, _theId, _thePayLoad):
        esReponseD = self.es.index(index=_theIndex, id=_theId, body=_thePayLoad)
        print("\n %s \n" % _thePayLoad)
        return esReponseD

    def updateDataInElastic(self, _theIndex, _theId, _thePayLoad):
        esReponseD = self.es.update(index=_theIndex, id=_theId, body=_thePayLoad)
        print("\n %s \n" % _thePayLoad)
        return esReponseD

    def hasDataBeenIndexed(self, _theIndex, _esId):
        print("Checking for %s " % _esId)
        returnVal = False
        try:
            esReponse2 = self.es.get(index=_theIndex, id=_esId, _source="false")
            if esReponse2['found'] == True:
                returnVal = True
                print("Item is already indexed.")
        except:
            print("Item does not exist yet.")
        return returnVal

    def fetchPureViewFunctionData(self, _contractAbiJSONData, _theContractInstance):
        callableFunctions = []
        for item in _contractAbiJSONData:
            if item['type'] == 'function':
                if len(item['inputs']) == 0:
                    if len(item['outputs']) > 0:
                        callableFunctions.append(str(item['name']))
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

    def fetchContractAddresses(self, _theIndex):
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["contractAddress"] = "0x*"
        dWildCard["wildcard"] = dContractAddress 
        dMatch = {}
        dReauiresUpdating = {}
        dReauiresUpdating["requiresUpdating"] = "yes"
        dMatch["match"] = dReauiresUpdating
        lMust = []
        lMust.append(dMatch)
        dBool = {}
        dBool["must"] = lMust
        lShould = []
        lShould.append(dWildCard)
        dBool["should"] = lShould
        dOb = {}
        dOb["bool"] = dBool
        dQuery["query"] = dOb
        lContractAddress.append("contractAddress")
        dQuery["_source"] = lContractAddress
        print(dQuery)
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=_theIndex, query=json.dumps(dQuery), preserve_order=True)
        uniqueList = []
        for i, doc in enumerate(esReponseAddresses):
            source = doc.get('_source')
            if source['contractAddress'] not in uniqueList:
                uniqueList.append(source['contractAddress'])
        return uniqueList

    def fetchFunctionDataIds(self, _theIndex):
        dQuery = {}
        dWildCard = {}
        dFunctionDataId = {}
        lFunctionId = []
        dFunctionDataId["functionDataId"] = "0x*"
        dWildCard["wildcard"] = dFunctionDataId
        lFunctionId.append("functionDataId")
        dQuery["query"] = dWildCard
        dQuery["_source"] = lFunctionId
        esReponseIds = elasticsearch.helpers.scan(client=self.es, index=_theIndex, query=json.dumps(dQuery), preserve_order=True)
        uniqueList = []
        for i, doc in enumerate(esReponseIds):
            source = doc.get('_source')
            if source['functionDataId'] not in uniqueList:
                uniqueList.append(source['functionDataId'])
        return uniqueList

    def harvest(self, _esIndex, _version, _contractAbiJSONData,  _stop=False):
        latestBlockNumber = self.web3.eth.getBlock('latest').number
        print("Latest block is %s" % latestBlockNumber)
        stopAtBlock = 0
        if _stop == True:
            # If run once per minute 24 is a satisfactory number (4 X the amount of blocks produced per minute)
            stopAtBlock = latestBlockNumber - 24
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
                        listOfKeccakHashes = self.createUniqueAbiComparisons(_contractAbiJSONData)
                        count = 0
                        for individualHash in listOfKeccakHashes:
                            if individualHash in transactionData.input:
                                count += 1
                                print("Found a match: %s " % individualHash)
                        if count == len(listOfKeccakHashes):
                            print("All hashes match!")
                            print("Contract address: %s " % transactionContractAddress)
                            try:
                                outerData = {}
                                contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=transactionContractAddress)
                                outerData['abiSha3'] = str(self.web3.toHex(self.web3.sha3(text=json.dumps(contractInstance.abi))))
                                outerData['blockNumber'] = transactionReceipt.blockNumber 
                                outerData['dappVersion'] = _version
                                outerData['contractAddress'] = transactionReceipt.contractAddress
                                functionData = self.fetchPureViewFunctionData(_contractAbiJSONData, contractInstance)
                                theStatus = functionData['status']
                                print("* Status: %s" % theStatus)
                                outerData['status'] = theStatus
                                if theStatus == 0:
                                    outerData['requiresUpdating'] = "yes"
                                elif theStatus == 1:
                                    outerData['requiresUpdating'] = "no"
                                functionDataId = self.getFunctionDataId(functionData)
                                outerData['functionDataId'] = functionDataId
                                outerData['functionData'] = functionData

                                itemId = str(self.web3.toHex(self.web3.sha3(text=transactionReceipt.contractAddress)))
                                dataStatus = self.hasDataBeenIndexed(_esIndex, itemId)
                                if dataStatus == False:
                                    indexResult = self.loadDataIntoElastic(_esIndex, itemId, json.dumps(outerData))
                            except:
                                print("An exception occured! - Please try and load contract at address: %s manually to diagnose." % transactionContractAddress)
                    else:
                        print("This transaction does not involve a contract, so we will ignore it")
                        continue
            else:
                print("Skipping block number %s - No transactions found!" % blockNumber)
                continue


    def fetchUniqueContractList(self, _esIndex):
        uniqueContractList = self.fetchContractAddresses(_esIndex)
        return uniqueContractList

    def fetchContractInstances(self, _contractAbiJSONData):
        contractInstanceList = []
        for uniqueContractAddress in self.uniqueContractList:
            contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=uniqueContractAddress)
            contractInstanceList.append(contractInstance)
        return contractInstanceList

    def refreshContractAddressList(self, _esIndex, _contractAbiJSONData):
        self.upcomingCallTime = time.time()
        while True:
            print("Refreshing the list of indexed contracts")
            self.uniqueContractListHashOld = self.uniqueContractListHashFresh
            self.tmp_uniqueContractList = self.fetchUniqueContractList(_esIndex)
            self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.tmp_uniqueContractList))))
            if self.uniqueContractListHashOld == self.uniqueContractListHashFresh:
                print("No change in contract addresses, for state update, at this stage")
            else:
                self.uniqueContractList = self.tmp_uniqueContractList
                self.contractInstanceList = self.fetchContractInstances(_contractAbiJSONData)
            self.upcomingCallTime = self.upcomingCallTime + 60
            time.sleep(self.upcomingCallTime - time.time())

    def performStateUpdate(self, _esIndex, _contractAbiJSONData):
        while True:
            uniqueFunctionIds = self.fetchFunctionDataIds(_esIndex)
            for uniqueContractInstance in self.contractInstanceList:
                freshFunctionData = self.fetchPureViewFunctionData(_contractAbiJSONData, uniqueContractInstance)
                functionDataId = self.getFunctionDataId(freshFunctionData)
                if functionDataId in uniqueFunctionIds:
                    print("No change to %s " % functionDataId)
                else:
                    print("Hash not found, we must now update this contract instance state")
                    itemId = str(self.web3.toHex(self.web3.sha3(text=uniqueContractInstance.address)))
                    doc = {}
                    outerData = {}
                    outerData["functionData"] = freshFunctionData
                    outerData["functionDataId"] = functionDataId
                    theStatus = freshFunctionData['status']
                    if theStatus == 0:
                        outerData['requiresUpdating'] = "yes"
                    elif theStatus == 1:
                        outerData['requiresUpdating'] = "no"
                    doc["doc"] = outerData
                    indexResult = self.updateDataInElastic(_esIndex, itemId, json.dumps(doc))

    def updateStateDriver(self, _esIndex, _contractAbiJSONData):
        self.stateUpdate = True
        # Initial setup of a list and its hash
        self.uniqueContractList = self.fetchUniqueContractList(_esIndex)
        self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.uniqueContractList))))
        self.contractInstanceList = self.fetchContractInstances(_contractAbiJSONData)
        # Allow a minute for variables to be set
        time.sleep(60)
        self.upcomingCallTime = time.time()
        self.timerThread = threading.Thread(target=self.refreshContractAddressList(_esIndex, _contractAbiJSONData))
        self.timerThread.daemon = True
        self.timerThread.start()
        # Allow a minute for the lists to be created


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup|state]", type=str, default="full")
    args = parser.parse_args()

    harvester = Harvest()
    for (outerKey, outerValue) in harvester.abis.items():
        print("%s:" % outerKey)
        indexName = outerKey.split('_')[0]
        version = outerKey.split('_')[1]
        print("Processing index %s" % indexName)
        print("Version %s" % version)
        jsonObject = json.loads(outerValue['json'])

    if args.mode == "full":
        print("Performing full harvest")
        harvester.harvest(indexName, version, jsonObject)
    elif args.mode == "topup":
        print("Performing topup")
        harvester.harvest(indexName, version, jsonObject, True)
    elif args.mode == "state1":
        print("Performing state update")
        harvester.updateStateDriver(indexName, jsonObject)
    elif args.mode == "state2":
        print("Performing state2 update")
        harvester.performStateUpdate(indexName, jsonObject)
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
        print("harvest.py --mode state")



