import os
import re
import sys
import time
import json
import boto3
import queue
import random
import argparse
import requests
import threading
import configparser
import elasticsearch.helpers
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

        # Blockchain RPC
        self.blockchainRpc = self.config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

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
        print(esReponseD)
        return esReponseD

    def hasDataBeenIndexed(self, _theIndex, _esId):
        returnVal = False
        try:
            esReponse2 = self.es.get(index=_theIndex, id=_esId, _source="false")
            if esReponse2['found'] == True:
                returnVal = True
                print("Item is already indexed.")
        except:
            print("Item does not exist yet.")
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
        theId = str(self.web3.toHex(self.web3.sha3(text=json.dumps(_theFunctionData))))
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


    def sortInternalListsInJsonObject(self, _json):
        for listItem in _json:
            #print("List item")
            #print(listItem)
            for k, v in listItem.items():
                if type(v) not in (str, bool, int) and len(v) > 1:
                    if type(v[0]) is dict:
                        v.sort(key=itemgetter("name"))
                    else:
                        v.sort()
        return _json

    def cleanAndConvertAbiToText(self, _theAbi):
        theAbiWithSortedLists = self.sortInternalListsInJsonObject(_theAbi)
        theAbiAsString = json.dumps(theAbiWithSortedLists, sort_keys=True)
        theAbiAsString2 = re.sub(r"[\n\t]*", "", theAbiAsString)
        theAbiAsString3 = re.sub(r"[\s]+", " ", theAbiAsString2)
        return theAbiAsString3

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
                newData = self.es.get(index=self.commonIndex, id=_source["contractAddress"])
                if len(newData["_source"]["abiShaList"]) > 0:
                    for item in newData["_source"]["abiShaList"]:
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
                print("ABI not compatible")
        else:
            print("No keccak hashes to compare")


    def abiCompatabilityUpdateDriverPre2(self, _abi, _esTxs):
        txThreadList = []
        for i, doc2 in _esTxs.items():
            source = doc2['_source']
            tabiCompatabilityUpdateDriverPre2 = threading.Thread(target=self.abiCompatabilityUpdate, args=[_abi, source])
            tabiCompatabilityUpdateDriverPre2.daemon = True
            tabiCompatabilityUpdateDriverPre2.start()
            txThreadList.append(tabiCompatabilityUpdateDriverPre2)
            time.sleep(1)
        for abiCompatabilityUpdateDriverPre2Thread in txThreadList:
            abiCompatabilityUpdateDriverPre2Thread.join()

    def expressUpdateAbiShaList(self, _abiHash):
        jsonAbi = json.loads(self.fetchAbiUsingHash(_abiHash))
        #print("JSON ABI")
        #print(jsonAbi)
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
            self.abiCompatabilityUpdateDriverPre1Timer = self.abiCompatabilityUpdateDriverPre1Timer + 300
            if self.abiCompatabilityUpdateDriverPre1Timer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.abiCompatabilityUpdateDriverPre1Timer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the state immediately ...")

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
            if dataStatus == False:
                try:                                    
                    contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=itemId)
                except:
                    print("Unable to instantiate web3 contract object")
                    sys.exit() 
                try:
                    functionData = self.fetchPureViewFunctionData(contractInstance)
                    functionDataId = self.getFunctionDataId(functionData)
                except:
                    print("Got web3 object OK but no data match!")
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
                    # This is required because if a minimalistic ABI is in place it will still instantiate a web3 object and add the ABI to the abiShaList which is incorrect. 
                    # In order to index this item we need to know that the web3 object can talk to the functions of the contract. 
                    print("There is no function data so moving on")
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
            time.sleep(5)
            processMultipleTransactionsThreads.append(tFullDriver3)
        for harvestDriverThread3 in processMultipleTransactionsThreads:
            harvestDriverThread3.join()

    def expressHarvestAnAbi(self, _abiSha):
        jsonAbi = self.fetchAbiUsingHash(_abiSha)
        queryForTransactionIndex = {"query":{"bool":{"must":[{"match":{"indexed":"false"}}]}}}
        esTransactions = elasticsearch.helpers.scan(client=self.es, index=self.masterIndex, query=queryForTransactionIndex, preserve_order=True)
        localTransactionList = []
        for esTransactionSingle in esTransactions:
            localTransactionList.append(esTransactionSingle['_source']['TxHash'])
        self.processMultipleTransactions(json.dumps(jsonAbi), localTransactionList)


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
            localTransactionList = []
            for esTransactionSingle in esTransactions:
                localTransactionList.append(esTransactionSingle['_source']['TxHash'])
            for localEsAbiSingle in localAbiList:
                tFullDriver2 = threading.Thread(target=self.processMultipleTransactions, args=[localEsAbiSingle, localTransactionList])
                tFullDriver2.daemon = True
                tFullDriver2.start()
                harvestTransactionsDriverThreads.append(tFullDriver2)
            for harvestDriverThread2 in harvestTransactionsDriverThreads:
                harvestDriverThread2.join()
            self.harvestTransactionsDriverTimer = self.harvestTransactionsDriverTimer + 1800
            if self.harvestTransactionsDriverTimer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.harvestTransactionsDriverTimer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the state immediately ...")


    def fetchContractInstances(self, _contractAbiId, _contractAddress):
        jsonAbiDataForInstance = json.loads(self.fetchAbiUsingHash(_contractAbiId))
        contractInstance = self.web3.eth.contract(abi=jsonAbiDataForInstance, address=_contractAddress)
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
            self.markMasterAsIndexedTimer = self.markMasterAsIndexedTimer + 1800
            if self.markMasterAsIndexedTimer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.markMasterAsIndexedTimer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the state immediately ...")

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
            newData = self.es.get(index=self.commonIndex, id=_instance.address)
            if len(newData["_source"]["functionDataList"]["0"]) > 0:
                for item in newData["_source"]["functionDataList"]["0"]:
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
            for contractInstanceItem in self.contractInstanceList:
                tupdateStateDriverPre = threading.Thread(target=self.worker, args=[contractInstanceItem])
                tupdateStateDriverPre.daemon = True
                tupdateStateDriverPre.start()
                threadsupdateStateDriverPre.append(tupdateStateDriverPre)
            for updateStateThreads1 in threadsupdateStateDriverPre:
                updateStateThreads1.join()
            print("Finished updateStateDriverPreTimer...")
            self.updateStateDriverPreTimer = self.updateStateDriverPreTimer + 10
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
            self.tupdateBytecode = self.tupdateBytecode + 10
            if self.tupdateBytecode > time.time():
                time.sleep(self.tupdateBytecode - time.time())

    def harvestAllContracts(self, esIndex,  _argList=[], _topup=False):
        bulkList = []
        self.upcomingCallTimeHarvest = time.time()
        while True:
            latestBlockNumber = self.web3.eth.getBlock('latest').number
            print("Latest block is %s" % latestBlockNumber)
            stopAtBlock = 0
            if _topup == True and len(_argList) == 0:
                stopAtBlock = latestBlockNumber - 24
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
                                outerData["indexed"] = "false"
                                itemId = transactionReceipt.contractAddress
                                dataStatus = self.hasDataBeenIndexed(esIndex, itemId)
                                if dataStatus == False:
                                    singleItem = {"_index":str(esIndex), "_id": str(itemId), "_type": "_doc", "_op_type": "index", "_source": json.dumps(outerData)}
                                    if _topup == True:
                                        bulkList.append(singleItem)
                                        elasticsearch.helpers.bulk(self.es, bulkList)
                                        bulkList = []
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
                                        bulkList.append(singleItem)
                                        print("Added item to BULK list, we now have " + str(len(bulkList)))
                                        if len(bulkList) == 50:
                                            elasticsearch.helpers.bulk(self.es, bulkList)
                                            bulkList = []
                            else:
                                continue
                    else:
                        print("Skipping block number %s - No transactions found!" % blockNumber)
                        continue
                except:
                    print("Problems at block height " + str(blockNumber))
            if len(bulkList) > 1:
                print("Adding the last few items which were not bulk loaded already")
                elasticsearch.helpers.bulk(self.es, bulkList)
                bulkList = []
            if _topup == True and len(_argList) == 0:
                self.upcomingCallTimeHarvest = self.upcomingCallTimeHarvest + 10
                if self.upcomingCallTimeHarvest > time.time():
                    time.sleep(self.upcomingCallTimeHarvest - time.time())
            else:
                if _topup == False and len(_argList) == 2:
                    break



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup|state|tx|abi|bytecode|indexed]", type=str, default="full")
    args = parser.parse_args()
    harvester = Harvest()
    # Ensure that the ABI index exists (others are created programatically but ABI needs to exist up front)
    if harvester.es.indices.exists(index=harvester.abiIndex) == False:
        harvester.es.indices.create(index=harvester.abiIndex)
    else:
        print("Index already exists")
    if args.mode == "full":
        print("Performing full harvest")
        latestBlockNumber = harvester.web3.eth.getBlock('latest').number
        threadsToUse = 654
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
    elif args.mode == "topup":
        print("Performing topup")
        argsList = []
        harvester.harvestAllContracts(harvester.masterIndex, argsList, True)
    elif args.mode == "tx":
        print("Performing harvest of masterindex transactions")
        harvester.harvestTransactionsDriver()
    elif args.mode == "state":
        print("Performing state update")
        harvester.updateStateDriverPre()
    elif args.mode == "bytecode":
        print("Performing bytecode update")
        harvester.updateBytecode()
    elif args.mode == "abi":
        print("Performing abi comparison update")
        harvester.abiCompatabilityUpdateDriverPre1()
    elif args.mode == "indexed":
        print("Updating master index to reflect items which are already indexed")
        harvester.markMasterAsIndexed()
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
        print("harvest.py --mode state")
        print("harvest.py --mode tx")
        print("harvest.py --mode bytecode")
        print("harvest.py --mode abi")
        print("harvest.py --mode indexed")


# Monitor the total number of threads on the operating system
# ps -eo nlwp | tail -n +2 | awk '{ total_threads += $1 } END { print total_threads }'

# Monitor the number of threads per pid; run any of the following commands and paste THE_PID into the watch command below
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m tx >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m bytecode >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m abi >/dev/null 2>&1 &

# watch -n 2 -d "ps -eL THE_PID | wc -l"
