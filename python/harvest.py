import os
import sys
import time
import json
import boto3
import queue
import argparse
import requests
import threading
import configparser
#from threading import Thread
import elasticsearch.helpers
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

class Harvest:
    def __init__(self):

        # Add list for unique queueing
        self.qList = []

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

    def harvest(self, _stop=False):
        self.upcomingCallTimeHarvest = time.time()
        itemConf = self.qHarvestDriver.get()
        if itemConf is None:
            print("itemConf is None")
        
        esIndex = itemConf[0].split('_')[0]
        version = itemConf[0].split('_')[1]
        contractAbiJSONData = json.loads(itemConf[1]['json'])
        while True:

            latestBlockNumber = self.web3.eth.getBlock('latest').number
            print("Latest block is %s" % latestBlockNumber)
            stopAtBlock = 0
            if _stop == True:
                stopAtBlock = latestBlockNumber - 24
            for blockNumber in reversed(range(stopAtBlock, latestBlockNumber)):
                print("\nProcessing block number %s" % blockNumber)
                blockTransactionCount = self.web3.eth.getBlockTransactionCount(blockNumber)
                if blockTransactionCount > 0:
                    block = self.web3.eth.getBlock(blockNumber)
                    for singleTransaction in block.transactions:
                        singleTransactionHex = singleTransaction.hex()
                        transactionData = self.web3.eth.getTransaction(str(singleTransactionHex))
                        transactionReceipt = self.web3.eth.getTransactionReceipt(str(singleTransactionHex))
                        transactionContractAddress = transactionReceipt.contractAddress
                        if transactionContractAddress != None:
                            listOfKeccakHashes = self.createUniqueAbiComparisons(contractAbiJSONData)
                            count = 0
                            for individualHash in listOfKeccakHashes:
                                if individualHash in transactionData.input:
                                    count += 1
                            if count == len(listOfKeccakHashes):
                                try:
                                    outerData = {}
                                    contractInstance = self.web3.eth.contract(abi=contractAbiJSONData, address=transactionContractAddress)
                                    outerData['abiSha3'] = str(self.web3.toHex(self.web3.sha3(text=json.dumps(contractInstance.abi))))
                                    outerData['blockNumber'] = transactionReceipt.blockNumber 
                                    outerData['dappVersion'] = version
                                    outerData['contractAddress'] = transactionReceipt.contractAddress
                                    functionData = self.fetchPureViewFunctionData(contractAbiJSONData, contractInstance)
                                    theStatus = functionData['status']
                                    outerData['status'] = theStatus
                                    if theStatus == 0:
                                        outerData['requiresUpdating'] = "yes"
                                    elif theStatus == 1:
                                        outerData['requiresUpdating'] = "no"
                                    functionDataId = self.getFunctionDataId(functionData)
                                    outerData['functionDataId'] = functionDataId
                                    outerData['functionData'] = functionData

                                    itemId = str(self.web3.toHex(self.web3.sha3(text=transactionReceipt.contractAddress)))
                                    dataStatus = self.hasDataBeenIndexed(esIndex, itemId)
                                    if dataStatus == False:
                                        indexResult = self.loadDataIntoElastic(esIndex, itemId, json.dumps(outerData))
                                except:
                                    print("An exception occured! - Please try and load contract at address: %s manually to diagnose." % transactionContractAddress)
                        else:
                            print("This transaction does not involve a contract, so we will ignore it")
                            continue
                else:
                    print("Skipping block number %s - No transactions found!" % blockNumber)
                    continue
            if _stop == False:
                self.qHarvestDriver.task_done()
            self.upcomingCallTimeHarvest = self.upcomingCallTimeHarvest + 12
            if self.upcomingCallTimeHarvest > time.time():
                time.sleep(self.upcomingCallTimeHarvest - time.time())

    def harvestDriver(self, _stop=False):
        self.qHarvestDriver = queue.Queue()
        self.threadsFullDriver = []
        for i in range(2):
            tFullDriver = threading.Thread(target=self.harvest, args=[_stop])
            tFullDriver.daemon = True
            tFullDriver.start()
            self.threadsFullDriver.append(tFullDriver)
        for abiConfig in self.abis.items():
            self.qHarvestDriver.put(abiConfig)
        self.qHarvestDriver.join()

    # State related
    def fetchUniqueContractList(self, _esIndex):
        self.uniqueContractList = []
        self.uniqueContractList = self.fetchContractAddresses(_esIndex)
        #print(self.uniqueContractList)

    def fetchContractInstances(self, _contractAbiJSONData):
        self.contractInstanceList = []
        for uniqueContractAddress in self.uniqueContractList:
            contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=uniqueContractAddress)
            self.contractInstanceList.append(contractInstance)

    def worker(self, _esIndex, _contractAbiJSONData):
        while True:
            item = self.q.get()
            if item is None:
                break
            uniqueFunctionIds = self.fetchFunctionDataIds(_esIndex)
            freshFunctionData = self.fetchPureViewFunctionData(_contractAbiJSONData, item)
            functionDataId = self.getFunctionDataId(freshFunctionData)
            if functionDataId in uniqueFunctionIds:
                print("No change to %s " % functionDataId)
            else:
                print("Hash not found, we must now update this contract instance state")
                itemId = str(self.web3.toHex(self.web3.sha3(text=item.address)))
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
            # do the work
            self.q.task_done()

    def performStateUpdate(self, _esIndex, _contractAbiJSONData):
        self.upcomingCallTimeState = time.time()
        while True:
            self.fetchUniqueContractList(_esIndex)
            self.uniqueContractListHashOrig = self.uniqueContractListHashFresh
            self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.uniqueContractList))))
            print("Comparing:")
            print(self.uniqueContractListHashOrig)
            print(self.uniqueContractListHashFresh)
            if self.uniqueContractListHashFresh != self.uniqueContractListHashOrig:
                print("New contract instances are available, we will go and fetch them now ...")
                self.fetchContractInstances(_contractAbiJSONData)
            else:
                print("The unique contract list is the same, we will just recheck the existing contract instances")
            
            print("Creating a blank queue")
            q = queue.Queue()
            queueIndex = len(qList)
            self.qList.append(q)
            # Create a blank threads list
            print("Creating blank threads list")
            self.threads = []
            print(self.threads)
            # Set the number of threads
            print("Setting the number of threads")
            for i in range(32):
                t = threading.Thread(target=self.worker, args=[_esIndex, _contractAbiJSONData, queueIndex])
                t.start()
                self.threads.append(t)
            print("Checking thread count")
            print(self.threads)
            print("Adding contract instances to the queue")
            for uniqueContractInstance in self.contractInstanceList:
                # Put a web3 contract object instance in the queue
                self.qList[queueIndex].put(uniqueContractInstance)

            # block untill all tasks are done
            self.qList[queueIndex].join()
            # set the time interval for when this task will be repeated
            self.upcomingCallTimeState = self.upcomingCallTimeState + 12
            # If this takes longer than the break time, then just continue straight away
            if self.upcomingCallTimeState > time.time():
                time.sleep(self.upcomingCallTimeState - time.time())

    def updateStateDriver(self):
        itemConf = self.qupdateStateDriverPre.get()
        if itemConf is None:
            print("itemConf is None")
        esIndex = itemConf[0].split('_')[0]
        version = itemConf[0].split('_')[1]
        contractAbiJSONData = json.loads(itemConf[1]['json'])
        while True:
            self.fetchUniqueContractList(esIndex)
            self.fetchContractInstances(contractAbiJSONData)
            self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.uniqueContractList))))
            self.timerThread = threading.Thread(target=self.performStateUpdate(esIndex, contractAbiJSONData))
            self.timerThread.daemon = True
            self.timerThread.start()
            self.qupdateStateDriverPre.task_done()

    def updateStateDriverPre(self):
        self.qupdateStateDriverPre = queue.Queue()
        self.threadsupdateStateDriverPre = []
        for i in range(2):
            tupdateStateDriverPre = threading.Thread(target=self.updateStateDriver)
            tupdateStateDriverPre.daemon = True
            tupdateStateDriverPre.start()
            self.threadsupdateStateDriverPre.append(tupdateStateDriverPre)
        for abiConfig in self.abis.items():
            self.qupdateStateDriverPre.put(abiConfig)
        self.qupdateStateDriverPre.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup|state]", type=str, default="full")
    args = parser.parse_args()

    harvester = Harvest()

    if args.mode == "full":
        print("Performing full harvest")
        harvester.harvestDriver()
    elif args.mode == "topup":
        print("Performing topup")
        harvester.harvestDriver(True)
    elif args.mode == "state":
        print("Performing state update")
        harvester.updateStateDriverPre()
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
        print("harvest.py --mode state")



