import os
import re
import sys
import time
import json
import math
import gzip
import boto3
import queue
import random
import eth_abi
import argparse
import requests
import threading
import configparser
from decimal import Decimal
from itertools import chain
import elasticsearch.helpers
from datetime import datetime
from operator import itemgetter
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

        # Master index
        self.masterIndex = self.config['masterindex']['all']
        print("Master index: %s" % self.masterIndex)

        # Common index
        self.commonIndex = self.config['commonindex']['network']
        print("Common index: %s" % self.commonIndex)
            
        # Abi index
        self.abiIndex = self.config['abiindex']['abi']
        print("Abi index: %s" % self.abiIndex)

        # Bytecode index
        self.bytecodeIndex = self.config['bytecodeindex']['bytecode']
        print("Bytecode index: %s" % self.bytecodeIndex)

        # Ignore index
        self.ignoreIndex = self.config['ignoreindex']['ignore']
        print("Ignore index: %s" % self.ignoreIndex)

        # Blockchain RPC
        self.blockchainRpc = self.config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

        # Blockchain, how many seconds per block?
        self.secondsPerBlock = self.config['blockchain']['seconds_per_block']
        print("Block time: %s" % self.secondsPerBlock)

        # Amount of allowable threads on this PC/OS
        self.maxThreads = self.config['system']['max_threads']
        print("Max threads: %s" % self.maxThreads)

        # Initial ABI
        self.initialAbiUrl = self.config['abi_code']['initial_abi_url']
        print("Initial ABI is located at: %s" % self.initialAbiUrl)

        # Elasticsearch endpoint
        self.elasticSearchEndpoint = self.config['elasticSearch']['endpoint']
        print("ElasticSearch Endpoint: %s" % self.elasticSearchEndpoint)

        # Activity index
        self.activityIndex = self.config['activityindex']['activity']
        print("Activity index: %s" % self.activityIndex)

        # Event index
        self.eventIndex = self.config['eventindex']['event']
        print("Event index: %s" % self.eventIndex)

        # Log analytics
        self.logAnalyticsIndex = self.config['loganalyticsindex']['log']
        print("Log analytics index: %s" % self.logAnalyticsIndex)

        # Log directory
        self.logDirectory = self.config['logdirectory']['location']
        print("Log directory location: %s" % self.logDirectory)

        # Log analytics
        self.apiAnalyticsIndex = self.config['apianalyticsindex']['api']
        print("API analytics index: %s" % self.apiAnalyticsIndex)

        # Elasticsearch AWS region
        self.elasticSearchAwsRegion = self.config['elasticSearch']['aws_region']

        # Web 3 init
        self.web3 = Web3(HTTPProvider(str(self.blockchainRpc)))

        # AWS Boto
        self.auth = BotoAWSRequestsAuth(aws_host=self.elasticSearchEndpoint, aws_region=self.elasticSearchAwsRegion, aws_service='es')
        self.es = Elasticsearch(
            hosts=[{'host': self.elasticSearchEndpoint, 'port': 443}],
            retry_on_timeout=True,
            timeout=30,
            max_retries=10,
            region=self.elasticSearchAwsRegion,
            use_ssl=True,
            verify_certs=True,
            http_auth=self.auth,
            connection_class=RequestsHttpConnection
        )

    def fetchAbiShaList(self, _contractAddress):
        query = '''{"query":{"match":{"contractAddress": "'''+ _contractAddress +  '''"}}, "_source": "abiShaList"}'''
        results = self.es.search(index=self.commonIndex, body=query)
        return results

    # This will become a function used to create the index of unique comparisons IUC
    def createUniqueAbiComparisons(self, _contractAbiJSONData):
        keccakHashes = []
        for item in _contractAbiJSONData:
            if item['type'] == 'function':
                if len(item['inputs']) == 0:
                    stringToHash = str(item['name'] + '()')
                    hashCreated = str(self.web3.toHex(self.web3.sha3(text=stringToHash)))[2:10]
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
                    hashCreated = str(self.web3.toHex(self.web3.sha3(text=stringToHash)))[2:10]
                    keccakHashes.append(hashCreated)
        return keccakHashes

    def getBlockInterval(self):
        return self.secondsPerBlock

    def mostRecentIndexedBlockNumber(self):
        query = '''{"aggs":{"most_recent_block":{"max":{"field":"blockNumber"}}}, "size":0}'''
        results = self.es.search(index=self.commonIndex, body=query)
        return results

    def getDataUsingTransactionHash(self, _hash):
        query = '''{"query":{"match":{"TxHash": "'''+ _hash +  '''"}}}'''
        results = self.es.search(index=self.commonIndex, body=query)
        return results

    def getDataUsingAddressHash(self, _hash):
        query = '''{"query":{"match":{"contractAddress": "'''+ _hash +  '''"}}}'''
        results = self.es.search(index=self.commonIndex, body=query)
        return results

    def getOnly100Records(self):
        query = {"query":{"match_all":{}},"size": 100}
        textQuery = json.dumps(query)
        results = self.es.search(index=self.commonIndex, body=textQuery)
        return results

    def getAbiCount(self):
        query = {"query":{"match_all":{}},"size": 0}
        textQuery = json.dumps(query)
        results = self.es.search(index=self.abiIndex, body=textQuery)
        return results

    def getAllCount(self):
        query = {"query":{"match_all":{}},"size": 0}
        textQuery = json.dumps(query)
        results = self.es.search(index=self.masterIndex, body=textQuery)
        return results

    def getContractCount(self):
        query = {"query":{"match_all":{}},"size": 0}
        textQuery = json.dumps(query)
        results = self.es.search(index=self.commonIndex, body=textQuery)
        return results

    def fetchAbiUsingHash(self, _esId):
        try:
            esReponseAbi = self.es.get(index=self.abiIndex , id=_esId)
            stringAbi = json.dumps(esReponseAbi["_source"]["abi"])
            jsonAbi = json.loads(stringAbi)
            #print("Return ABI Object")
            #print(jsonAbi)
            return jsonAbi
        except:
            print("Unable to fetch ABI from the ABI index")

    def loadDataIntoElastic(self, _theIndex, _theId, _thePayLoad):
        esReponseD = self.es.index(index=_theIndex, id=_theId, body=_thePayLoad)
        return esReponseD

    def updateDataInElastic(self, _theIndex, _theId, _thePayLoad):
        esReponseD = self.es.update(index=_theIndex, id=_theId, body=_thePayLoad)
        #print(esReponseD)
        return esReponseD

    def hasDataBeenIndexed(self, _theIndex, _esId):
        returnVal = False
        q = '{"query":{"bool":{"must":[{"match":{"contractAddress":"'+ _esId +'"}}]}}, "size": 0}'
        try:
            esResponse2 = self.es.search(index=_theIndex, body=q)
            print(esResponse2)
            if int(esResponse2["hits"]["total"]) == 1:
                returnVal = True
                print("Item is already indexed.")
            else:
                print("Item does not exist yet.")
                returnVal = False
        except:
            print("Error, unable to test if item exists")
            returnVal = False
        return returnVal

    def hasEventBeenIndexed(self, _theIndex, _esId):
        returnVal = False
        q = '{"query":{"bool":{"must":[{"match":{"txEventKey":"'+ _esId +'"}}]}}, "size": 0}'
        try:
            esResponse2 = self.es.search(index=_theIndex, body=q)
            print(esResponse2)
            if int(esResponse2["hits"]["total"]) == 1:
                returnVal = True
                print("Event is already indexed.")
            else:
                print("Event does not exist yet.")
                returnVal = False
        except:
            print("Error, unable to test if event exists")
            returnVal = False
        return returnVal

    def hasLogBeenIndexed(self, _theIndex, _esId):
        returnVal = False
        q = '{"query":{"bool":{"must":[{"match":{"uniqueHash":"'+ _esId +'"}}]}}, "size": 0}'
        try:
            esResponse2 = self.es.search(index=_theIndex, body=q)
            print(esResponse2)
            if int(esResponse2["hits"]["total"]) == 1:
                returnVal = True
                print("Log is already indexed.")
            else:
                print("Log does not exist yet.")
                returnVal = False
        except:
            print("Error, unable to test if log exists")
            returnVal = False
        return returnVal

    def hasApiBeenIndexed(self, _theIndex, _esId):
        returnVal = False
        q = '{"query":{"bool":{"must":[{"match":{"uniqueHash":"'+ _esId +'"}}]}}, "size": 0}'
        try:
            esResponse2 = self.es.search(index=_theIndex, body=q)
            print(esResponse2)
            if int(esResponse2["hits"]["total"]) == 1:
                returnVal = True
                print("API is already indexed.")
            else:
                print("API does not exist yet.")
                returnVal = False
        except:
            print("Error, unable to test if API exists")
            returnVal = False
        return returnVal

    def performStringConversion(self, _data):
        return str(_data)
    
    def performPossibleStringConversion(self, _data):
        if len(str(_data)) > 10:
            try:
                int(_data)
                return str(_data)
            except:
                return _data
        else:
            return _data

    def performStringConversion(self, _data):
        return str(_data)
    
    def performPossibleStringConversion(self, _data):
        if len(str(_data)) > 10:
            try:
                int(_data)
                return str(_data)
            except:
                return _data
        else:
            return _data

    def fetchPureViewFunctionData(self, _theContractInstance):
        callableFunctions = []
        for item in _theContractInstance.abi:
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
                    innerDataDict = {}
                    for i in range(len(result)):
                        innerDataDict[i] = self.performStringConversion(result[i])
                    theFunctionData[str(callableFunction)] = innerDataDict
            else:
                theFunctionData[str(callableFunction)] = self.performStringConversion(result)
        # Check to see if all of the callable functions
        if len(callableFunctions) == len(theFunctionData):
            return theFunctionData
        else:
            theFunctionDataIsNotComplete = {}
            return theFunctionDataIsNotComplete

    def getFunctionDataId(self, _theFunctionData):
        theId = str(self.web3.toHex(self.web3.sha3(text=json.dumps(_theFunctionData, sort_keys=False))))
        return theId

    def fetchTxHashWithAbis(self, _not):
        self.esAbiAddresses = []
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["abiShaList"] = "0x*"
        dWildCard["wildcard"] = dContractAddress 
        dMatch = {}
        dReauiresUpdating = {}
        dReauiresUpdating["field"] = _not
        dMatch["exists"] = dReauiresUpdating
        lMust = []
        lMust.append(dMatch)
        dBool = {}
        dBool["must_not"] = lMust
        lShould = []
        lShould.append(dWildCard)
        dBool["should"] = lShould
        dOb = {}
        dOb["bool"] = dBool
        dQuery["query"] = dOb
        lContractAddress.append("TxHash")
        lContractAddress.append("abiShaList")
        lContractAddress.append("contractAddress")
        dQuery["_source"] = lContractAddress
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        for item in esReponseAddresses:
            for singleAbi in item["_source"]["abiShaList"]:
                obj = {}
                obj["abiSha3"] = singleAbi
                obj["TxHash"] = item["_source"]["TxHash"]
                obj["contractAddress"] = item["_source"]["contractAddress"]
                self.esAbiAddresses.append(json.dumps(obj))

    # Compare two items and return a bool
    def compareItems(self, a, b):
        try:
            #print("Comparing " + str(a['type']) + " and " + str(b['type']))
            if str(a['type']) > str(b['type']) or str(a['type']) == str(b['type']) and str(a['name']) > str(b['name']) :
                #print("Returning True")
                return True
            else:
                #print("Returning False")
                return False
        except:
            # Caters for cases where the name is not present i.e. a fallback function
            #print("Comparing " + str(a['type']) + " and " + str(b['type']))
            if str(a['type']) > str(b['type']):
                #print("Returning True")
                return True
            else:
                #print("Returning False")
                return False

    # Sort a given json object
    def sortJson(self, _json):
        #print(_json)
        for passnum in range(len(_json)-1,0,-1):
            for item in range(len(_json) - 1):
                if self.compareItems(_json[item], _json[item+1]) == True:
                    temp = _json[item]
                    _json[item] = _json[item+1]
                    _json[item+1] = temp
        return _json

    def sortABIKeys(self, _abi):
        for item in range(len(_abi)):
            itemKeys = list(_abi[item])
            itemKeys.sort()
            sortedDict = {}
            for key in itemKeys:
                sortedDict[key] = _abi[item][key]
            _abi[item] = sortedDict
        return _abi

    def sortInternalListsInJsonObject(self, _abi):
        for listItem in _abi:
            for k, v in listItem.items():
                if type(v) not in (str, bool, int):
                    if len(v) > 1:
                        if type(v[0]) is dict:
                            v = self.sortJson(v)
                    else:
                        print("Not enough items in the list to sort, moving on")
                else:
                    print(str(v) + " is not a list, moving on ...")
        return _abi

    def sanitizeString(self, _dirtyString):
        cleanString = re.sub(r"[\n\t\s]*", "", _dirtyString)
        return cleanString

    def cleanAndConvertAbiToText(self, _theAbi):
        #theAbiWithSortedLists = self.sortInternalListsInJsonObject(_theAbi)
        theAbiWithSortedKeys = self.sortABIKeys(_theAbi)
        theAbiFullySorted = self.sortJson(theAbiWithSortedKeys)
        sanitizedAbiString = self.sanitizeString(json.dumps(theAbiFullySorted, sort_keys=False))
        return sanitizedAbiString

    def createHashFromString(self, _stringToHash):
        hashedString = str(self.web3.toHex(self.web3.sha3(text=_stringToHash)))
        return hashedString

    def shaAnAbi(self, _theAbi):
        theAbiAsString = self.cleanAndConvertAbiToText(_theAbi)
        theAbiHash = str(self.web3.toHex(self.web3.sha3(text=theAbiAsString)))
        return theAbiHash

    def abiCompatabilityUpdate(self, _esAbiSingle, _source):
        print("Processing " + str(self.shaAnAbi(_esAbiSingle)))
        transactionData = self.web3.eth.getTransaction(str(_source["TxHash"]))
        listOfKeccakHashes = self.createUniqueAbiComparisons(_esAbiSingle)
        if len(listOfKeccakHashes) > 0:
            count = 0
            for individualHash in listOfKeccakHashes:
                if individualHash in transactionData.input:
                    count += 1
                else:
                    print("Hash not found, so move on quickly")
                    break
            if count == len(listOfKeccakHashes):
                newAbiSha = self.shaAnAbi(_esAbiSingle)
                newList = []
                found = False
                q = '{"query":{"bool":{"must":[{"match":{"contractAddress":"'+ _source["contractAddress"] +'"}}]}}}'
                newData = self.es.search(index=self.commonIndex, body=q)
                if len(newData["hits"]["hits"][0]["_source"]["abiShaList"]) > 0:
                    for item in newData["hits"]["hits"][0]["_source"]["abiShaList"]:
                        if item == newAbiSha:
                            found = True
                            break
                        else:
                            newList.append(item)
                            print("Still searching")
                    if found == False:
                        print("Did not find " + newAbiSha + " adding it now.")
                        newList.append(newAbiSha)
                else:
                    newList.append(newAbiSha)
                if len(newList) > 0 and found == False:
                    doc = {}
                    outerData = {}
                    outerData["abiShaList"] = newList
                    doc["doc"] = outerData
                    self.updateDataInElastic(self.commonIndex, _source["contractAddress"], json.dumps(doc))
            else:
                print("ABI not compatible, ignoring this abi and address from now on")
                self.addDataToIgnoreIndex(_esAbiSingle, _source["contractAddress"])
        else:
            print("No keccak hashes to compare, ignoring this abi and address from now on")
            self.addDataToIgnoreIndex(_esAbiSingle, _source["contractAddress"])


    def abiCompatabilityUpdateDriverPre2(self, _abi, _esTxs):
        txThreadList = []
        for i, doc2 in _esTxs.items():
            source = doc2['_source']
            abiHash = self.shaAnAbi(_abi)
            uniqueAbiAndAddressKey = str(abiHash) + str(source['contractAddress'])
            uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
            if self.hasDataBeenIndexed(self.ignoreIndex, uniqueAbiAndAddressHash) != True:
                print("Item is NOT in the ignore index so we need to check it out ...")
                tabiCompatabilityUpdateDriverPre2 = threading.Thread(target=self.abiCompatabilityUpdate, args=[_abi, source])
                tabiCompatabilityUpdateDriverPre2.daemon = True
                tabiCompatabilityUpdateDriverPre2.start()
                txThreadList.append(tabiCompatabilityUpdateDriverPre2)
                time.sleep(math.floor(int(self.secondsPerBlock)/10))
            else:
                print("This item is in the ignore index so we are moving on ...")
        for abiCompatabilityUpdateDriverPre2Thread in txThreadList:
            abiCompatabilityUpdateDriverPre2Thread.join()

    def expressUpdateAbiShaList(self, _abiHash):
        jsonAbi = json.loads(self.fetchAbiUsingHash(_abiHash))
        queryForTXs = {"query":{"match":{"indexInProgress": "false"}}, "_source": ["TxHash", "contractAddress", "bytecodeSha3"]}
        esTxs = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=queryForTXs, preserve_order=True)
        TxObj = {}
        num = 1
        for item in esTxs:
            TxObj[str(num)] = item
            num = num+1
        self.abiCompatabilityUpdateDriverPre2(jsonAbi, json.loads(json.dumps(TxObj)))


    def abiCompatabilityUpdateDriverPre1(self):
        self.abiCompatabilityUpdateDriverPre1Timer = time.time()
        while True:
            abiThreadList = []
            queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
            esAbis = self.es.search(index=self.abiIndex, body=queryForAbiIndex)
            # Get all of the contract instance addresses and their respective transaction hashes
            queryForTXs = {"query":{"match":{"indexInProgress": "false"}}, "_source": ["TxHash", "contractAddress", "bytecodeSha3"]}
            esTxs = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=queryForTXs, preserve_order=True)
            TxObj = {}
            num = 1
            for item in esTxs:
                TxObj[str(num)] = item
                num = num+1
            #print(TxObj)
            for doc1 in esAbis["hits"]["hits"]:
                source = doc1['_source']
                tabiCompatabilityUpdateDriverPre1 = threading.Thread(target=self.abiCompatabilityUpdateDriverPre2, args=[json.loads(source["abi"]), json.loads(json.dumps(TxObj))])
                tabiCompatabilityUpdateDriverPre1.daemon = True
                tabiCompatabilityUpdateDriverPre1.start()
                abiThreadList.append(tabiCompatabilityUpdateDriverPre1)
            for abiCompatabilityUpdateDriverPre1Thread in abiThreadList:
                abiCompatabilityUpdateDriverPre1Thread.join()
            self.abiCompatabilityUpdateDriverPre1Timer = self.abiCompatabilityUpdateDriverPre1Timer + math.floor(int(self.secondsPerBlock) * 4)
            if self.abiCompatabilityUpdateDriverPre1Timer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.abiCompatabilityUpdateDriverPre1Timer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the ABI immediately ...")

    def addDataToIgnoreIndex(self, _contractAbiJSONData, _itemId):
        outerData = {}
        outerData['contractAddress'] = _itemId
        abiHash = self.shaAnAbi(_contractAbiJSONData)
        outerData['abiSha3'] = abiHash
        uniqueAbiAndAddressKey = str(abiHash) + str(_itemId)
        uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
        print("Adding to ignore list!")
        ignoreIndexResult = self.loadDataIntoElastic(self.ignoreIndex, uniqueAbiAndAddressHash, json.dumps(outerData))

    def confirmDeployment(self, _transactionHex):
        timeoutValue = time.time() + (int(self.secondsPerBlock * 10))
        event = threading.Event()
        contractAddress = None
        while (event.is_set() == False):
            if timeoutValue >= time.time():
                time.sleep(int(self.secondsPerBlock))
            try:
                transactionReceipt = self.web3.eth.getTransactionReceipt(str(_transactionHex))
                if transactionReceipt.contractAddress == None:
                    event.set()
                else:    
                    contractAddress = self.web3.toChecksumAddress(transactionReceipt.contractAddress)
                    event.set()
            except:
                pass
        return contractAddress

    def processSingleTransaction(self,_contractAbiJSONData, _transactionHex):
        transactionData = self.web3.eth.getTransaction(str(_transactionHex))
        transactionReceipt = self.web3.eth.getTransactionReceipt(str(_transactionHex))
        itemId = None
        try:
            itemId = transactionReceipt.contractAddress
            print("Found contract: " + itemId)
        except:
            print("No contract here ...")
            sys.exit() 
        if itemId != None:
            dataStatus = self.hasDataBeenIndexed(self.commonIndex, itemId)
            if dataStatus == True:
                theAbiHash = self.shaAnAbi(_contractAbiJSONData)
                indexedContractData = self.getDataUsingAddressHash(itemId)
                if theAbiHash in indexedContractData["hits"]["hits"][0]["_source"]["abiShaList"]:
                    print("This ABI and address are already associated")
                else:
                    print("Performing associated ABI compatability update")
                    self.abiCompatabilityUpdate(_contractAbiJSONData, indexedContractData["hits"]["hits"][0]["_source"])
            if dataStatus == False:
                try:                                    
                    contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=self.web3.toChecksumAddress(itemId))
                except:
                    print("Unable to instantiate web3 contract object")
                    self.addDataToIgnoreIndex(_contractAbiJSONData, itemId)
                    sys.exit()
                try:
                    functionData = self.fetchPureViewFunctionData(contractInstance)
                    functionDataId = self.getFunctionDataId(functionData)
                except:
                    print("Got web3 object OK but no data match!")
                    self.addDataToIgnoreIndex(_contractAbiJSONData, itemId)
                    sys.exit()
                if len(functionData) > 0:
                    try:                
                        outerData = {}
                        outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                        abiList = []
                        abiHash = self.shaAnAbi(_contractAbiJSONData)
                        abiList.append(abiHash)
                        outerData['abiShaList'] = abiList
                        outerData['blockNumber'] = transactionReceipt.blockNumber
                        outerData['creator'] = transactionReceipt['from']
                        outerData['contractAddress'] = itemId
                        functionDataList = []
                        functionDataObjectInner = {}
                        functionDataObjectInner['functionDataId'] = functionDataId
                        functionDataObjectInner['functionData'] = functionData
                        uniqueAbiAndAddressKey = str(abiHash) + str(contractInstance.address)
                        uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
                        functionDataObjectInner['uniqueAbiAndAddressHash'] = uniqueAbiAndAddressHash
                        functionDataList.append(functionDataObjectInner)
                        functionDataObjectOuter = {}
                        functionDataObjectOuter["0"] = functionDataList
                        outerData['functionDataList'] = functionDataObjectOuter
                        outerData["requiresUpdating"] = "yes"
                        outerData['quality'] = "50"
                        outerData['indexInProgress'] = "false"
                        indexResult = self.loadDataIntoElastic(self.commonIndex, itemId, json.dumps(outerData))
                    except:
                        print("Got Data OK but no ES index!")
                        sys.exit()
                else:
                    print("There is no function data so we will do an ABI compatibility update")
                    indexedContractData = self.getDataUsingAddressHash(itemId)
                    listOfKeccakHashes = self.createUniqueAbiComparisons(_contractAbiJSONData)
                    if len(listOfKeccakHashes) > 0:
                        count = 0
                        for individualHash in listOfKeccakHashes:
                            if individualHash in transactionData.input:
                                count += 1
                            else:
                                print("Hash not found, so move on quickly")
                                break
                        if count == len(listOfKeccakHashes):
                            try:                
                                outerData = {}
                                outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                abiList = []
                                abiHash = self.shaAnAbi(_contractAbiJSONData)
                                abiList.append(abiHash)
                                outerData['abiShaList'] = abiList
                                outerData['blockNumber'] = transactionReceipt.blockNumber
                                outerData['creator'] = transactionReceipt['from']
                                outerData['contractAddress'] = itemId
                                functionDataList = []
                                functionDataObjectOuter = {}
                                functionDataObjectOuter["0"] = functionDataList
                                outerData['functionDataList'] = functionDataObjectOuter
                                outerData["requiresUpdating"] = "yes"
                                outerData['quality'] = "50"
                                outerData['indexInProgress'] = "false"
                                indexResult = self.loadDataIntoElastic(self.commonIndex, itemId, json.dumps(outerData))
                            except:
                                print("Got Data OK but no ES index!")
                                sys.exit()
            else:
                print("Item is already indexed")
        else:
            print("Problem with transaction hex: " + str(_transactionHex))

    def processMultipleTransactions(self, _esAbiSingle, _esTransactions):
        processMultipleTransactionsThreads = []
        contractAbiJSONData = json.loads(_esAbiSingle)
        txCount = len(_esTransactions)
        for i in range(txCount):
            transactionHash = random.choice(_esTransactions)
            tFullDriver3 = threading.Thread(target=self.processSingleTransaction, args=[contractAbiJSONData, transactionHash])
            tFullDriver3.daemon = True
            tFullDriver3.start()
            #time.sleep(math.floor(int(self.secondsPerBlock) / 3))
            processMultipleTransactionsThreads.append(tFullDriver3)
        for harvestDriverThread3 in processMultipleTransactionsThreads:
            harvestDriverThread3.join()

    def expressHarvestAnAbi(self, _abiSha, _blockFloor):
        blockHeight = self.web3.eth.getBlock('latest').number
        jsonAbi = json.loads(self.fetchAbiUsingHash(_abiSha))
        queryForTransactionIndex = '''{"query":{"bool":{"must":{"range":{"blockNumber":{"gte":"''' + str(_blockFloor) + '''","lte":"''' + str(blockHeight) + '''"}}}}}}'''
        esTransactions = elasticsearch.helpers.scan(client=self.es, index=self.masterIndex, query=queryForTransactionIndex, preserve_order=True)
        localTransactionList = []
        for esTransactionSingle in esTransactions:
            localTransactionList.append(esTransactionSingle['_source']['TxHash'])
        self.processMultipleTransactions(json.dumps(jsonAbi), localTransactionList)
        return True


    # NEW Multi-thread
    def harvestTransactionsDriver2(self, _localEsAbiSingle, _esTransactions):
        localTransactionList = []
        abiHash = self.shaAnAbi(json.loads(_localEsAbiSingle))
        print("Processing of " + abiHash + " has begun!")
        txCount = len(_esTransactions)
        #for i in range(txCount):
        for esTransactionSingle in _esTransactions:
            #esTransactionSingle = random.choice(_esTransactions)
            uniqueAbiAndAddressKey = str(abiHash) + str(esTransactionSingle['contractAddress'])
            uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
            if self.hasDataBeenIndexed(self.ignoreIndex, uniqueAbiAndAddressHash) != True:
                localTransactionList.append(esTransactionSingle['TxHash'])
                if len(localTransactionList) == 15:
                    print("Processing a batch of 15 items")
                    self.processMultipleTransactions(_localEsAbiSingle, localTransactionList)
                    localTransactionList = []
            else:
                print("Ignoring " + uniqueAbiAndAddressHash + " because it is in the ignore index")
        if len(localTransactionList) > 0:
            print("Processing the last few items")
            self.processMultipleTransactions(_localEsAbiSingle, localTransactionList)
        print("Processing of " + abiHash + " is complete!")


    def harvestTransactionsDriver(self):
        self.harvestTransactionsDriverTimer = time.time()
        while True:
            print("Harvesting transactions from masterindex")
            queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
            esAbis = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex, query=queryForAbiIndex, preserve_order=True)
            harvestTransactionsDriverThreads = []
            localAbiList = []
            for esAbiSingle in esAbis:
                localAbiList.append(esAbiSingle['_source']['abi'])
            queryForTransactionIndex = {"query":{"bool":{"must":[{"match":{"indexed":"false"}}]}}}
            # Use the following if you want to query a subset of blocks
            #queryForTransactionIndex = {"query":{"range":{"blockNumber":{"gte" : 5000000,"lte" : 5572036}}}}
            esTransactions = elasticsearch.helpers.scan(client=self.es, index=self.masterIndex, query=queryForTransactionIndex, preserve_order=True)
            localTransactionListPre = []
            for esTransactionSingle in esTransactions:
                aDict = {}
                aDict["TxHash"] = esTransactionSingle['_source']['TxHash']
                aDict["contractAddress"] = esTransactionSingle['_source']['contractAddress']
                localTransactionListPre.append(aDict)
            for localEsAbiSingle in localAbiList:
                tFullDriver2 = threading.Thread(target=self.harvestTransactionsDriver2, args=[localEsAbiSingle, localTransactionListPre])
                tFullDriver2.daemon = True
                tFullDriver2.start()
                harvestTransactionsDriverThreads.append(tFullDriver2)
            for harvestDriverThread2 in harvestTransactionsDriverThreads:
                harvestDriverThread2.join()
            self.harvestTransactionsDriverTimer = self.harvestTransactionsDriverTimer + math.floor(int(self.secondsPerBlock) * 10)
            if self.harvestTransactionsDriverTimer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.harvestTransactionsDriverTimer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the tx immediately ...")


    def fetchContractInstances(self, _contractAbiId, _contractAddress):
        jsonAbiDataForInstance = json.loads(self.fetchAbiUsingHash(_contractAbiId))
        contractInstance = self.web3.eth.contract(abi=jsonAbiDataForInstance, address=self.web3.toChecksumAddress(_contractAddress))
        self.contractInstanceList.append(contractInstance)

    def markMasterTest(self):
        bulkList = []
        body = {}
        outerData = {}
        outerData["indexed"] = "true"
        body["body"] = outerData
        singleItem = {"_index":str(self.masterIndex), "_id": str(0x8DF3fEAb1CA6B112946c5ec231D3517Fa44269B4), "_type": "document", "_op_type": "update", "doc": json.dumps(body)}
        bulkList.append(singleItem)
        elasticsearch.helpers.bulk(self.es, bulkList)


    def markMasterAsIndexed(self):
        self.markMasterAsIndexedTimer = time.time()
        while True:
            indexedAddressesList = []
            queryForCommonIndex = {"query":{"match_all":{}}}
            esAddressesIndexed = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=queryForCommonIndex, preserve_order=True)
            for indexedAddress in esAddressesIndexed:
                indexedAddressesList.append(indexedAddress['_source']['contractAddress'])
            esAddressesIndexed = ""

            queryForMasterIndex = {"query":{"bool":{"must":[{"match":{"indexed":"false"}}]}}}
            # Use the following if you want to query a subset of blocks
            #queryForTransactionIndex = {"query":{"range":{"blockNumber":{"gte" : 5000000,"lte" : 5572036}}}}
            esAddresses = elasticsearch.helpers.scan(client=self.es, index=self.masterIndex, query=queryForMasterIndex, preserve_order=True)
            doc = {}
            outerData = {}
            outerData["indexed"] = "true"
            doc["doc"] = outerData

            localAddressList = []
            for esAddressSingle in esAddresses:
                localAddressList.append(esAddressSingle['_source']['contractAddress'])
            for address in localAddressList:
                print("Processing " + str(address))
                if address in indexedAddressesList:
                    theResponse = self.es.update(index=self.masterIndex, id=address, body=json.dumps(doc))
            self.markMasterAsIndexedTimer = self.markMasterAsIndexedTimer + math.floor(int(self.secondsPerBlock) * 10)
            if self.markMasterAsIndexedTimer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.markMasterAsIndexedTimer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the state immediately ...")

    def updateStateOfSingleAbiAndContractAddressRelationship(self, _abi, _address):
        contractInstance = self.web3.eth.contract(abi=_abi, address=self.web3.toChecksumAddress(_address))
        freshFunctionData = self.fetchPureViewFunctionData(contractInstance)
        functionDataId = self.getFunctionDataId(freshFunctionData)
        abiHash = self.shaAnAbi(contractInstance.abi)
        uniqueAbiAndAddressKey = str(abiHash) + str(contractInstance.address)
        uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
        functionDataObjectOuter = {}
        functionDataObjectInner = {}
        functionDataObjectInner['functionDataId'] = functionDataId
        functionDataObjectInner['functionData'] = freshFunctionData
        functionDataObjectInner['uniqueAbiAndAddressHash'] = uniqueAbiAndAddressHash
        newList = []
        found = False
        q = '{"query":{"bool":{"must":[{"match":{"contractAddress":"'+ contractInstance.address +'"}}]}}}'
        newData = self.es.search(index=self.commonIndex, body=q)
        # es.get does not work on the common index reliably and as such we are replacing it with a better call
        #newData = self.es.get(index=self.commonIndex, id=contractInstance.address)
        if len(newData["hits"]["hits"][0]["_source"]["functionDataList"]["0"]) > 0:
            for item in newData["hits"]["hits"][0]["_source"]["functionDataList"]["0"]:
                for k, v in item.items():
                    if k == "uniqueAbiAndAddressHash":
                        if v == uniqueAbiAndAddressHash:
                            newList.append(functionDataObjectInner)
                            found = True
                        else:
                            newList.append(item)
        else:
            newList.append(functionDataObjectInner)
            found = True
        if found == False:
            newList.append(functionDataObjectInner)
        doc = {}
        outerData = {}
        functionDataObjectOuter["0"] = newList
        outerData["functionDataList"] = functionDataObjectOuter
        doc["doc"] = outerData
        self.updateDataInElastic(self.commonIndex, contractInstance.address, json.dumps(doc))


    def updateStateOfContractAddress(self, _abi, _address):
        try:
            if _abi == "all":
                q = '{"query":{"bool":{"must":[{"match":{"contractAddress":"'+ _address +'"}}]}}}'
                print(q)
                contractItem = self.es.search(index=self.commonIndex, body=q)
                print(contractItem)
                if len( contractItem["hits"]["hits"][0]["_source"]["abiShaList"]) > 0:
                    for abiHash in  contractItem["hits"]["hits"][0]["_source"]["abiShaList"]:
                        print("Processing ABI hash: ")
                        jsonAbi = self.fetchAbiUsingHash(abiHash)
                        self.updateStateOfSingleAbiAndContractAddressRelationship(jsonAbi, _address)
                return True
            else:
                self.updateStateOfSingleAbiAndContractAddressRelationship(_abi, _address)
                return True
        except:
            return False

    def worker(self, _instance):
        freshFunctionData = self.fetchPureViewFunctionData(_instance)
        functionDataId = self.getFunctionDataId(freshFunctionData)
        abiHash = self.shaAnAbi(_instance.abi)
        uniqueAbiAndAddressKey = str(abiHash) + str(_instance.address)
        uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
        if uniqueAbiAndAddressHash not in self.addressAndFunctionDataHashes.keys():
            self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] = ""
        if self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] != functionDataId:
            functionDataObjectOuter = {}
            functionDataObjectInner = {}
            functionDataObjectInner['functionDataId'] = functionDataId
            functionDataObjectInner['functionData'] = freshFunctionData
            functionDataObjectInner['uniqueAbiAndAddressHash'] = uniqueAbiAndAddressHash
            self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] = functionDataId
            newList = []
            found = False
            q = '{"query":{"bool":{"must":[{"match":{"contractAddress":"'+ _instance.address +'"}}]}}}'
            newData = self.es.search(index=self.commonIndex, body=q)
            # es.get does not work on the common index reliably and as such we are replacing it with a better call
            #newData = self.es.get(index=self.commonIndex, id=_instance.address)
            if len(newData["hits"]["hits"][0]["_source"]["functionDataList"]["0"]) > 0:
                for item in newData["hits"]["hits"][0]["_source"]["functionDataList"]["0"]:
                    for k, v in item.items():
                        if k == "uniqueAbiAndAddressHash":
                            if v == uniqueAbiAndAddressHash:
                                newList.append(functionDataObjectInner)
                                found = True
                            else:
                                newList.append(item)
            else:
                newList.append(functionDataObjectInner)
                found = True
            if found == False:
                newList.append(functionDataObjectInner)
            doc = {}
            outerData = {}
            functionDataObjectOuter["0"] = newList
            outerData["functionDataList"] = functionDataObjectOuter
            doc["doc"] = outerData
            self.updateDataInElastic(self.commonIndex, _instance.address, json.dumps(doc))
        else:
            print("The data is still the same so we will move on ...")


    def updateStateDriverPre(self):
        self.updateStateDriverPreTimer = time.time()
        self.addressAndFunctionDataHashes = {}
        self.fetchTxHashWithAbis("potentialFutureFilter")
        self.contractInstanceList = []
        for singleEntry in self.esAbiAddresses:
            abiAndAddress = json.loads(singleEntry)
            self.fetchContractInstances(abiAndAddress["abiSha3"], abiAndAddress["contractAddress"])
        while True:
            print("updateStateDriverPre")           
            originalListOfAddressesAndAbi = self.esAbiAddresses
            origListOfAddresses = []
            for originalItem in originalListOfAddressesAndAbi:
                originalItemJSON = json.loads(originalItem)
                uniqueAbiAndAddressKey = str(originalItemJSON['abiSha3']) + str(originalItemJSON['contractAddress'])
                uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
                if uniqueAbiAndAddressHash not in origListOfAddresses:
                    origListOfAddresses.append(uniqueAbiAndAddressHash)
            self.fetchTxHashWithAbis("potentialFutureFilter")
            for newItem in self.esAbiAddresses:
                newItemJSON = json.loads(newItem)
                uniqueAbiAndAddressKey2 = str(newItemJSON['abiSha3']) + str(newItemJSON['contractAddress'])
                uniqueAbiAndAddressHash2 = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey2)))
                if uniqueAbiAndAddressHash2 not in origListOfAddresses:
                    self.fetchContractInstances(newItemJSON['abiSha3'], newItemJSON['contractAddress'])
                else:
                    print("We already have that address")
            threadsupdateStateDriverPre = []
            # New random functionality
            txCount = len(self.contractInstanceList)
            counter = 0
            maxThreads = self.maxThreads
            for i in range(txCount):
                counter = counter + 1
                contractInstanceItem = random.choice(self.contractInstanceList)
                tupdateStateDriverPre = threading.Thread(target=self.worker, args=[contractInstanceItem])
                tupdateStateDriverPre.daemon = True
                tupdateStateDriverPre.start()
                threadsupdateStateDriverPre.append(tupdateStateDriverPre)
                if counter == math.floor(int(maxThreads) / int(4)):
                    # Processing a batch 
                    for updateStateThreads1 in threadsupdateStateDriverPre:
                        updateStateThreads1.join()
                        counter = 0
                        threadsupdateStateDriverPre = []
                # Process any left overs
            if counter > 0:
                # Processing a batch 
                for updateStateThreads1 in threadsupdateStateDriverPre:
                    updateStateThreads1.join()
                    counter = 0
                    threadsupdateStateDriverPre = []
            # Sleep if task is performed before time is up
            print("Finished updateStateDriverPreTimer...")
            self.updateStateDriverPreTimer = self.updateStateDriverPreTimer + int(self.secondsPerBlock)
            if self.updateStateDriverPreTimer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.updateStateDriverPreTimer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than 10 seconds, need to re-update the state immediately ...")

    def updateBytecodeAndVersion(self, _txHash, _esId):
        print("Creating transaction instance")
        transactionInstance = self.web3.eth.getTransaction(str(_txHash))
        dMatchAllInner = {}
        dMatchAll = {}
        dMatchAll["match_all"] = dMatchAllInner
        dQuery = {}
        dQuery["query"] = dMatchAll
        print("Querying ES " + json.dumps(dQuery))
        esReponseByte = elasticsearch.helpers.scan(client=self.es, index=self.bytecodeIndex , query=json.dumps(dQuery), preserve_order=True)
        for i, doc in enumerate(esReponseByte):
            print("Processing Bytecode items")
            source = doc.get('_source')
            print("Processing " + str(source))
            if source["bytecode"] in transactionInstance.input:
                print("Found bytecode")
                doc = {}
                outerData = {}
                bytecodeSha3 = self.web3.toHex(self.web3.sha3(text=source["bytecode"]))
                outerData["bytecodeSha3"] = bytecodeSha3
                doc["doc"] = outerData
                self.updateDataInElastic(self.commonIndex, _esId, json.dumps(doc))

    def updateBytecode(self):
        self.tupdateBytecode = time.time()
        while True:
            print("Starting ...")
            self.threadsUpdateBytecode = []
            self.fetchTxHashWithAbis("bytecodeSha3")
            for versionlessItem in self.esAbiAddresses:
                print(versionlessItem)
                versionlessItemJSON = json.loads(versionlessItem)
                tVersionless = threading.Thread(target=self.updateBytecodeAndVersion, args=[versionlessItemJSON["TxHash"], versionlessItemJSON["contractAddress"]])
                tVersionless.daemon = True
                tVersionless.start()
                self.threadsUpdateBytecode.append(tVersionless)
            for individualVersionlessThread in self.threadsUpdateBytecode:
                individualVersionlessThread.join()
            print("Finished")
            self.tupdateBytecode = self.tupdateBytecode + int(self.secondsPerBlock)
            if self.tupdateBytecode > time.time():
                time.sleep(self.tupdateBytecode - time.time())

    def stateOfRecentBlocksOnly(self, _abiData, _calledAddress):
        contractInstance = self.web3.eth.contract(abi=_abiData, address=self.web3.toChecksumAddress(_calledAddress))
        self.worker(contractInstance)


    def stateOfRecentBlocksOnlyPre(self, esIndex):
        self.tstateOfRecentBlocksOnly = time.time()
        self.addressAndFunctionDataHashes = {}
        while True:
            self.threadsstateOfRecentBlocksOnly = []
            latestBlockNumber = self.web3.eth.getBlock('latest').number
            # Allow this function to calculate how many blocks to go back based on config
            stopAtBlock = latestBlockNumber - math.floor(100 / int(self.secondsPerBlock))
            for blockNumber in reversed(range(stopAtBlock, latestBlockNumber)):
                print("\nProcessing block number %s" % blockNumber)
                blockTransactionCount = self.web3.eth.getBlockTransactionCount(blockNumber)
                if blockTransactionCount > 0:
                    block = self.web3.eth.getBlock(blockNumber)
                    for singleTransaction in block.transactions:
                        singleTransactionHex = singleTransaction.hex()
                        print("Processing transaction: " + singleTransactionHex)
                        transactionData = self.web3.eth.getTransaction(str(singleTransactionHex))
                        transactionReceipt = self.web3.eth.getTransactionReceipt(str(singleTransactionHex))
                        print("Transaction receipt:\n")
                        print(transactionReceipt)
                        calledAddress = transactionReceipt['to']
                        if calledAddress != None:
                            print("Searching for contract address of : " + calledAddress)
                            dataStatus = self.hasDataBeenIndexed(esIndex, calledAddress)
                            if dataStatus == True:
                                contractToProcess = self.getDataUsingAddressHash(calledAddress)
                                print(contractToProcess)
                                for abiShaItem in contractToProcess["hits"]["hits"][0]["_source"]["abiShaList"]:
                                    abiData = self.fetchAbiUsingHash(abiShaItem)
                                    tData = threading.Thread(target=self.stateOfRecentBlocksOnly, args=[abiData, calledAddress])
                                    tData.daemon = True
                                    tData.start()
                                    self.threadsstateOfRecentBlocksOnly.append(tData)
            for individualVersionlessThread in self.threadsstateOfRecentBlocksOnly:
                individualVersionlessThread.join()
            self.tstateOfRecentBlocksOnly = self.tstateOfRecentBlocksOnly + int(self.secondsPerBlock)
            if self.tstateOfRecentBlocksOnly > time.time():
                time.sleep(self.tstateOfRecentBlocksOnly - time.time())

    def harvestAllEvents(self, _esIndex, _argList=[], _topup=False):
        self.upcomingCallTimeEventHarvest = time.time()
        while True:
            latestBlockNumber = self.web3.eth.getBlock('latest').number
            print("Latest block is %s" % latestBlockNumber)
            stopAtBlock = 0
            if _topup == True and len(_argList) == 0:
                # This takes time so therefore 10 second block time goes back 10 blocks, 1 second block time goes back 100 blocks etc.
                stopAtBlock = latestBlockNumber - math.floor(100 / int(self.secondsPerBlock))
            if _topup == False and len(_argList) == 2:
                latestBlockNumber = _argList[0]
                stopAtBlock = latestBlockNumber - _argList[1]
                if stopAtBlock < 0:
                    stopAtBlock = 0
                print("Reverse processing from block %s to block %s" %(latestBlockNumber, stopAtBlock))
            for b in reversed(range(stopAtBlock, latestBlockNumber)):
                blockIteration = self.web3.eth.getBlock(b)
                transactionCount = self.web3.eth.getBlockTransactionCount(b)
                if(transactionCount >= 1):
                    for singleTransactionInt in range(0, transactionCount):
                        transaction = self.web3.eth.getTransactionByBlock(b, singleTransactionInt)
                        transactionHash = transaction.hash
                        transactionReceipt = self.web3.eth.getTransactionReceipt(transaction.hash)
                        transactionLogs = transactionReceipt.logs
                        if (len(transactionLogs) >= 1):
                            for transactionLog in transactionLogs:
                                contractAddress = transactionLog["address"]
                                blockNumber = transactionReceipt["blockNumber"]
                                sentFrom = transactionReceipt["from"]
                                if self.hasDataBeenIndexed(self.commonIndex, contractAddress) == True:
                                    listOfAbis = self.fetchAbiShaList(contractAddress)
                                    if listOfAbis["hits"]["total"] > 0:
                                        for item in listOfAbis["hits"]["hits"][0]["_source"]["abiShaList"]:
                                            jsonAbi = json.loads(self.fetchAbiUsingHash(str(item)))
                                            for abiComponents in jsonAbi:
                                                isEvent = False
                                                name = ""
                                                inputs = []
                                                for key, value in abiComponents.items():
                                                    if key == "inputs":
                                                        inputs = value
                                                    if key == "name":
                                                        name = value
                                                    if key == "type":
                                                        if value == "event":
                                                            isEvent = True
                                                if isEvent is True and name is not "":
                                                    outerData = {}
                                                    # Create a selector hash
                                                    selectorText = str(name) + "("
                                                    inputList = []
                                                    inputTypeList = []
                                                    inputNameList = []
                                                    indexedInputTypeList = []
                                                    indexedInputNameList = []
                                                    for input in range(0, len(inputs)):
                                                        inputDict = {}
                                                        # Set the status of a particular input's index attribute
                                                        inputIndexed = False
                                                        for inputKey, inputValue in inputs[input].items():
                                                            # Create a list of input key values for the ES index
                                                            inputDict[str(inputKey)] = str(inputValue)
                                                            if str(inputKey) == "indexed":
                                                                if inputValue == False:
                                                                    inputIndexed = False
                                                                else:
                                                                    if inputValue == True:
                                                                        inputIndexed = True
                                                        inputList.append(inputDict)
                                                        # With the given status, go ahead and create the respective lists of values (indexed vs not indexed)
                                                        for inputKey, inputValue in inputs[input].items():
                                                            if str(inputKey) == "name":
                                                                if inputIndexed == False:
                                                                    inputNameList.append(str(inputValue))
                                                                elif inputIndexed == True:
                                                                    indexedInputNameList.append(str(inputValue))
                                                            if str(inputKey) == "type":
                                                                if inputIndexed == False:
                                                                    inputTypeList.append(str(inputValue))
                                                                elif inputIndexed == True:
                                                                    indexedInputTypeList.append(str(inputValue))
                                                                if input == len(inputs) - 1:
                                                                    selectorText = selectorText + str(inputValue) + ")"
                                                                else:
                                                                    selectorText = selectorText + str(inputValue) + ","
                                                    # Creating a unique identifier for this event for ES 
                                                    selectorHash = "0x" + str(self.web3.toHex(self.web3.sha3(text=selectorText)))[2:10]
                                                    txEventString = str(selectorHash) + str(self.web3.toHex(transaction.hash))
                                                    txEventKey = str(self.web3.toHex(self.web3.sha3(text=txEventString)))
                                                    if self.hasEventBeenIndexed(self.eventIndex, txEventKey) != True:
                                                        # Calculate the hash to that we can see if the transaction's topic has a match
                                                        eventSignature = self.web3.toHex(self.web3.sha3(text=selectorText))
                                                        # Obtain the transaction's topics so we can compare
                                                        topics = self.web3.toHex(transactionLog['topics'][0])
                                                        # Check to see that the topic in this transaction matches the particular ABI event that we are currently iterating over
                                                        if topics == eventSignature:
                                                            print(str(name))
                                                            outerData["timestamp"] = blockIteration["timestamp"]
                                                            outerData["txEventKey"] = txEventKey
                                                            outerData["id"] = str(selectorHash)
                                                            outerData["name"] = str(name)
                                                            outerData["contractAddress"] = contractAddress
                                                            outerData["TxHash"] = str(self.web3.toHex(transaction.hash))
                                                            outerData["blockNumber"] = blockNumber
                                                            outerData["from"] = sentFrom
                                                            outerData["inputs"] = inputList
                                                            print(transactionLog)
                                                            data = transactionLog.data
                                                            eventLogData = {}
                                                            # If all of the event inputs are declared in the smart contract as indexed the data will be 0x
                                                            try:
                                                                if data != "0x":
                                                                    print("This event has a combination of indexed and non indexed inputs")
                                                                    print("inputList"  + str(inputList))
                                                                    print("inputTypeList" + str(inputTypeList))
                                                                    print("inputNameList" + str(inputNameList))
                                                                    print("indexedInputTypeList" + str(indexedInputTypeList))
                                                                    print("indexedInputNameList" + str(indexedInputNameList))
                                                                    print(data)
                                                                    print(inputTypeList)
                                                                    print("0")
                                                                    values = eth_abi.decode_abi(inputTypeList, bytes.fromhex(re.split("0x", data)[1]))
                                                                    indexedValues = [eth_abi.decode_single(t, v) for t, v in zip(indexedInputTypeList, transactionLog['topics'][1:])]
                                                                    eventLogData = dict(chain(zip(inputNameList, values), zip(indexedInputNameList, indexedValues)))
                                                                    fdoo = {}
                                                                    fdl = []
                                                                    fdl.append(eventLogData)
                                                                    fdoo["0"] = fdl
                                                                    outerData["eventLogData"] = fdoo
                                                                else:
                                                                    indexedValues = [eth_abi.decode_single(t, v) for t, v in zip(indexedInputTypeList, transactionLog['topics'][1:])]
                                                                    eventLogData = dict(zip(indexedInputNameList, indexedValues))
                                                                    fdoo = {}
                                                                    fdl = []
                                                                    fdl.append(eventLogData)
                                                                    fdoo["0"] = fdl
                                                                    outerData["eventLogData"] = fdoo
                                                                if len(eventLogData) >= 1:
                                                                    indexResult = self.loadDataIntoElastic(self.eventIndex, txEventKey, json.dumps(outerData))
                                                            except:
                                                                print("Data creation and indexing section's exception - this can trigger if ABIs share the same event function signature so please ignore unless data is not being indexed as intended")
                                                    else:
                                                        print("We have already indexed this event log")
                                    else:
                                        print("This contract's ABIs are not known/indexed so we can not read the event names")
                                else:
                                    print("We have not idexed this contract and therefore do not have the ABIs")
                        else:
                            print("Transaction: " + str(self.web3.toHex(transactionHash)) + " has no logs")
                else:
                    print("Transaction count is 0")
            if _topup == True and len(_argList) == 0:
                self.upcomingCallTimeEventHarvest = self.upcomingCallTimeEventHarvest + int(self.secondsPerBlock)
                if self.upcomingCallTimeEventHarvest > time.time():
                    time.sleep(self.upcomingCallTimeEventHarvest - time.time())
            else:
                if _topup == False and len(_argList) == 2:
                    break



    def harvestAllContracts(self, esIndex,  _argList=[], _topup=False):
        self.upcomingCallTimeHarvest = time.time()
        while True:
            #bulkList = []
            latestBlockNumber = self.web3.eth.getBlock('latest').number
            print("Latest block is %s" % latestBlockNumber)
            stopAtBlock = 0
            if _topup == True and len(_argList) == 0:
                # This takes time so therefore 10 second block time goes back 10 blocks, 1 second block time goes back 100 blocks etc.
                stopAtBlock = latestBlockNumber - math.floor(100 / int(self.secondsPerBlock))
            if _topup == False and len(_argList) == 2:
                latestBlockNumber = _argList[0]
                stopAtBlock = latestBlockNumber - _argList[1]
                if stopAtBlock < 0:
                    stopAtBlock = 0
                print("Reverse processing from block %s to block %s" %(latestBlockNumber, stopAtBlock))
            for blockNumber in reversed(range(stopAtBlock, latestBlockNumber)):
                try:
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
                                outerData = {}
                                outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                outerData['blockNumber'] = transactionReceipt.blockNumber
                                outerData['contractAddress'] = transactionReceipt.contractAddress
                                outerData['from'] = transactionReceipt['from']
                                outerData['to'] = transactionReceipt['to']
                                outerData["indexed"] = "false"
                                itemId = transactionReceipt.contractAddress
                                dataStatus = self.hasDataBeenIndexed(esIndex, itemId)
                                if dataStatus == False:
                                    if _topup == True:
                                        indexResult = self.loadDataIntoElastic(esIndex, itemId, json.dumps(outerData))
                                        self.threadsAddNewItem = []
                                        dMatchAllInner = {}
                                        dMatchAll = {}
                                        dMatchAll["match_all"] = dMatchAllInner
                                        dQuery = {}
                                        dQuery["query"] = dMatchAll
                                        print("Querying ES " + json.dumps(dQuery))
                                        esReponseAbi = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex , query=json.dumps(dQuery), preserve_order=True)
                                        for item in esReponseAbi:
                                            jsonAbi = json.loads(item["_source"]["abi"])
                                            tAddNewItem = threading.Thread(target=self.processSingleTransaction, args=[jsonAbi , str(self.web3.toHex(transactionData.hash))])
                                            tAddNewItem.daemon = True
                                            tAddNewItem.start()
                                            self.threadsAddNewItem.append(tAddNewItem)
                                        for individualAddNewItemThread in self.threadsAddNewItem:
                                            individualAddNewItemThread.join()
                                    else:
                                        indexResult = self.loadDataIntoElastic(esIndex, itemId, json.dumps(outerData))
                                        #singleItem = {"_index":str(esIndex), "_id": str(itemId), "_type": "_doc", "_op_type": "index", "_source": json.dumps(outerData)}
                                        #bulkList.append(singleItem)
                                        #print("Added item to BULK list, we now have " + str(len(bulkList)))
                                        #if len(bulkList) == 50:
                                        #    elasticsearch.helpers.bulk(self.es, bulkList)
                                        #    bulkList = []
                            else:
                                dataStatus = self.hasDataBeenIndexed(self.activityIndex, str(self.web3.toHex(transactionData.hash)))
                                print("Indexing transaction activity because this one is not contract related")
                                if dataStatus == False:
                                    outerData = {}
                                    outerData['timestamp'] = block['timestamp']
                                    outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                    outerData['blockNumber'] = transactionData['blockNumber']
                                    outerData['from'] = transactionData['from']
                                    outerData['to'] = transactionData['to']
                                    outerData['valueWei'] = str(transactionData['value'])
                                    outerData['valueEth'] = float(round(self.web3.fromWei(transactionData['value'], 'ether'), 6))
                                    outerData['gasUsed'] = transactionReceipt.gasUsed
                                    #singleItem = {"_index":str(self.activityIndex), "_id": str(self.web3.toHex(transactionData.hash)), "_type": "_doc", "_op_type": "index", "_source": json.dumps(outerData)}
                                    indexResult = self.loadDataIntoElastic(self.activityIndex, str(self.web3.toHex(transactionData.hash)), json.dumps(outerData))
                                else:
                                    print("We already have this transaction: " + str(self.web3.toHex(transactionData.hash)))
                    else:
                        print("Skipping block number %s - No transactions found!" % blockNumber)
                        continue
                except:
                    print("Problems at block height " + str(blockNumber))
            #if len(bulkList) >= 1:
            #    print("Adding the last few items which were not bulk loaded already")
            #    elasticsearch.helpers.bulk(self.es, bulkList)
            #    bulkList = []
            if _topup == True and len(_argList) == 0:
                self.upcomingCallTimeHarvest = self.upcomingCallTimeHarvest + int(self.secondsPerBlock)
                if self.upcomingCallTimeHarvest > time.time():
                    time.sleep(self.upcomingCallTimeHarvest - time.time())
            else:
                if _topup == False and len(_argList) == 2:
                    break

    def initiate(self):
        print("Checking to see if " + str(self.abiIndex) + " exists ...")
        if self.es.indices.exists(index=self.abiIndex) == False:
            print("Creating " + str(self.abiIndex))
            self.es.indices.create(index=self.abiIndex)
            print("Fetching ABI to load from " + str(self.initialAbiUrl))
            abiData = requests.get(self.initialAbiUrl).content
            abiDataJSON = json.loads(abiData)
            theDeterministicHash = self.shaAnAbi(abiDataJSON)
            cleanedAndOrderedAbiText = self.cleanAndConvertAbiToText(abiDataJSON)
            data = {}
            data['indexInProgress'] = "false"
            data['epochOfLastUpdate'] = int(time.time())
            data['abi'] = cleanedAndOrderedAbiText
            print("Uploading ABI into the newly created ABI index")
            self.es.index(index=self.abiIndex, id=theDeterministicHash, body=data)
            print("Success")
        else:
            print(str(self.abiIndex) + ", index already exists")
        print("Checking to see if " + str(self.masterIndex) + " exists ...")
        if self.es.indices.exists(index=self.masterIndex) == False:
            print("Creating " + str(self.masterIndex))
            self.es.indices.create(index=self.masterIndex)
        else:
            print(str(self.masterIndex) + ", index already exists")
        print("Checking to see if " + str(self.commonIndex) + " exists ...")
        if self.es.indices.exists(index=self.commonIndex) == False:
            print("Creating " + str(self.commonIndex))
            self.es.indices.create(index=self.commonIndex)
        else:
            print(str(self.commonIndex) + ", index already exists")
        print("Checking to see if " + str(self.bytecodeIndex) + " exists ...")
        if self.es.indices.exists(index=self.bytecodeIndex) == False:
            print("Creating " + str(self.bytecodeIndex))
            self.es.indices.create(index=self.bytecodeIndex)
        else:
            print(str(self.bytecodeIndex) + ", index already exists")
        print("Checking to see if " + str(self.ignoreIndex) + " exists ...")
        if self.es.indices.exists(index=self.ignoreIndex) == False:
            print("Creating " + str(self.ignoreIndex))
            self.es.indices.create(index=self.ignoreIndex)
        else:
            print(str(self.ignoreIndex) + ", index already exists")
        print("Checking to see if " + str(self.eventIndex) + " exists ...")
        if self.es.indices.exists(index=self.eventIndex) == False:
            print("Creating " + str(self.eventIndex))
            self.es.indices.create(index=self.eventIndex)
        else:
            print(str(self.eventIndex) + ", index already exists")
        print("Checking to see if " + str(self.activityIndex) + " exists ...")
        if self.es.indices.exists(index=self.activityIndex) == False:
            print("Creating " + str(self.activityIndex))
            self.es.indices.create(index=self.activityIndex)
        else:
            print(str(self.activityIndex) + ", index already exists")
        print("Checking to see if " + str(self.logAnalyticsIndex) + " exists ...")
        if self.es.indices.exists(index=self.logAnalyticsIndex) == False:
            print("Creating " + str(self.logAnalyticsIndex))
            self.es.indices.create(index=self.logAnalyticsIndex)
        else:
            print(str(self.logAnalyticsIndex) + ", index already exists")
        print("Checking to see if " + str(self.apiAnalyticsIndex) + " exists ...")
        if self.es.indices.exists(index=self.apiAnalyticsIndex) == False:
            print("Creating " + str(self.apiAnalyticsIndex))
            self.es.indices.create(index=self.apiAnalyticsIndex)
        else:
            print(str(self.apiAnalyticsIndex) + ", index already exists")
        print("Initialisation complete!")

    def withinApiRequestsLimit(self, _hits, _seconds, _Ip):
        now = math.floor(time.time())
        before = math.floor(now - _seconds)
        q='''{"query":{"bool":{"must":[{"match":{"callingIp":"''' + str(_Ip) + '''"}},{"range":{"timestamp":{"gte":''' + str(before) + ''',"lt":''' + str(now) + '''}}}]}}, "size": 0}'''
        esResponse = self.es.search(index=self.apiAnalyticsIndex, body=q)
        if int(esResponse["hits"]["total"]) >= int(_hits):
            return False
        else:
            return True

    def processApiAccessLog(self, _data):
        uniqueHash = str(self.web3.toHex(self.web3.sha3(text=str(_data))))
        if self.hasApiBeenIndexed(self.apiAnalyticsIndex, uniqueHash) != True:
            _data["uniqueHash"] = uniqueHash
            indexingResult = self.loadDataIntoElastic(self.apiAnalyticsIndex, uniqueHash, json.dumps(_data))

    def processSingleApacheAccessLogLine(self, _line):
        split_line = _line.split()
        # IP
        try:
            callingIP = str(split_line[0])
        except:
            callingIP = ""
        # Time
        try:
            time = str.join(" ",(split_line[3], split_line[4]))
            time = time.replace("[", "")
            time = time.replace("]", "")
            d = datetime.strptime(time, "%d/%b/%Y:%H:%M:%S %z")
            timestamp = math.floor(d.timestamp())
        except:
            timestamp = 0
        # Request
        try:
            request = str(split_line[5])
            request = request.replace("\"", "")
        except:
            request = ""
        # Response status code
        try:
            responseStatus = str(split_line[8])
        except:
            responseStatus = ""
        # Referer
        try:
            referer = str(split_line[10])
            referer = referer.replace("\"", "")
        except:
            referer = ""
        if timestamp > 0 and len(callingIP) > 0:
            uniqueHash = str(self.web3.toHex(self.web3.sha3(text=str(split_line))))
            if self.hasLogBeenIndexed(self.logAnalyticsIndex, uniqueHash) != True:
                data = {}
                data["timestamp"] = timestamp
                data["callingIp"] = callingIP
                data["request"] = request
                data["responseStatus"] = responseStatus
                data["referer"] = referer
                data["uniqueHash"] = uniqueHash
                data["rawLog"] = split_line
                indexingResult = self.loadDataIntoElastic(self.logAnalyticsIndex, uniqueHash, json.dumps(data))

    def processCurrentApache2AccessLog(self):
        while True:
            with open(os.path.join(self.logDirectory, "access.log"), 'rt') as f:
                for line in f:
                    self.processSingleApacheAccessLogLine(line)
            f.close()

    def processApache2AccessLogs(self):
        self.logHarvestTime = time.time()
        while True:
            for subdir, dirs, files in os.walk(self.logDirectory):
                for file in files:
                    if file.startswith("access"):
                        if file.endswith(".gz"):
                            print("Extracting: " + file)
                            with gzip.open(os.path.join(self.logDirectory, file), 'rt') as fGz:
                                for line in fGz:
                                    self.processSingleApacheAccessLogLine(line)
                            fGz.close()
                        else:
                            print("Processing: " + file)
                            with open(os.path.join(self.logDirectory, file), 'rt') as f:
                                for line in f:
                                    self.processSingleApacheAccessLogLine(line)
                            f.close()
            self.logHarvestTime = self.logHarvestTime + math.floor(int(self.secondsPerBlock)*10)
            if self.logHarvestTime > time.time():
                time.sleep(self.logHarvestTime - time.time())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup|state|faster_state|tx|abi|bytecode|indexed]", type=str, default="init")
    args = parser.parse_args()
    harvester = Harvest()
    if args.mode == "init":
        harvester.initiate()
    elif args.mode == "full":
        while True:
            print("Performing full harvest")
            latestBlockNumber = harvester.web3.eth.getBlock('latest').number
            threadsFromConf = harvester.maxThreads
            # Learned that there is a limitation in the number of bulk transactions which ES can process, have to throttle this here but threads can be used elsewhere i.e. state are which does not use bulk
            if int(threadsFromConf) > 50:
                threadsToUse = 50
            else:
                threadsToUse = int(threadsFromConf)
            blocksPerThread = int(latestBlockNumber / threadsToUse)
            harvester.fastThreads = []
            for startingBlock in range(1, latestBlockNumber, blocksPerThread):
                argList = []
                argList.append(startingBlock)
                argList.append(blocksPerThread)
                tFullDriver = threading.Thread(target=harvester.harvestAllContracts, args=[harvester.masterIndex, argList, False])
                tFullDriver.daemon = True
                tFullDriver.start()
                harvester.fastThreads.append(tFullDriver)
            for tt in harvester.fastThreads:
                tt.join()
            print("Full harvest has fully completed, sleeping for 5 seconds and then restarting again ...")
            time.sleep(5)
            print("Restarting now ...")
    elif args.mode == "topup":
        print("Performing topup")
        argsList = []
        harvester.harvestAllContracts(harvester.masterIndex, argsList, True)
    elif args.mode == "full_event":
        while True:
            print("Performing full Event harvest")
            latestBlockNumber = harvester.web3.eth.getBlock('latest').number
            threadsFromConf = harvester.maxThreads
            # Learned that there is a limitation in the number of bulk transactions which ES can process, have to throttle this here but threads can be used elsewhere i.e. state are which does not use bulk
            if int(threadsFromConf) > 50:
                threadsToUse = 50
            else:
                threadsToUse = int(threadsFromConf)
            blocksPerThread = int(latestBlockNumber / threadsToUse)
            harvester.fastThreads = []
            for startingBlock in range(1, latestBlockNumber, blocksPerThread):
                argList = []
                argList.append(startingBlock)
                argList.append(blocksPerThread)
                tFullDriver = threading.Thread(target=harvester.harvestAllEvents, args=[harvester.eventIndex, argList, False])
                tFullDriver.daemon = True
                tFullDriver.start()
                harvester.fastThreads.append(tFullDriver)
            for tt in harvester.fastThreads:
                tt.join()
            print("Full event log harvest has fully completed, sleeping for 5 seconds and then restarting again ...")
            time.sleep(5)
            print("Restarting now ...")
    elif args.mode == "topup_event":
        print("Performing event log topup")
        argsList = []
        harvester.harvestAllEvents(harvester.eventIndex, argsList, True)
    elif args.mode == "tx":
        print("Performing harvest of masterindex transactions")
        harvester.harvestTransactionsDriver()
    elif args.mode == "state":
        print("Performing state update")
        harvester.updateStateDriverPre()
    elif args.mode == "faster_state":
        print("Performing fast state update of only the most recent blocks")
        harvester.stateOfRecentBlocksOnlyPre(harvester.commonIndex)
    elif args.mode == "bytecode":
        print("Performing bytecode update")
        harvester.updateBytecode()
    elif args.mode == "abi":
        print("Performing abi comparison update")
        harvester.abiCompatabilityUpdateDriverPre1()
    elif args.mode == "indexed":
        print("Updating master index to reflect items which are already indexed")
        harvester.markMasterAsIndexed()
    elif args.mode == "analyse":
        print("Harvesting Apache2 logs for analysis")
        harvester.processApache2AccessLogs()
    elif args.mode == "analyse_real_time":
        print("Harvesting Apache2 access.log for analysis")
        harvester.processCurrentApache2AccessLog()
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode init")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
        print("harvest.py --mode full_event")
        print("harvest.py --mode topup_event")
        print("harvest.py --mode state")
        print("harvest.py --mode faster_state")
        print("harvest.py --mode tx")
        print("harvest.py --mode bytecode")
        print("harvest.py --mode abi")
        print("harvest.py --mode indexed")
        print("harvest.py --mode analyse")
        print("harvest.py --mode analyse_real_time")


# Monitor the total number of threads on the operating system
# ps -eo nlwp | tail -n +2 | awk '{ total_threads += $1 } END { print total_threads }'

# Monitor the number of threads per pid; run any of the following commands and paste THE_PID into the watch command below
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m tx >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m bytecode >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m abi >/dev/null 2>&1 &

# watch -n 2 -d "ps -eL THE_PID | wc -l"
