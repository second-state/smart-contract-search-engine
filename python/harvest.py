import os
import re
import sys
import time
import json
import boto3
import queue
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

    def fetchAbiUsingHash(self, _esId):
        try:
            #print("ID=" + _esId)
            esReponseAbi = self.es.get(index=self.abiIndex , id=_esId)
            stringAbi = json.dumps(esReponseAbi["_source"]["abi"])
            jsonAbi = json.loads(stringAbi)
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
                        innerDataDict[i] = self.performPossibleStringConversion(result[i])
                    theFunctionData[str(callableFunction)] = innerDataDict
            else:
                theFunctionData[str(callableFunction)] = self.performPossibleStringConversion(result)
        return theFunctionData

    def getFunctionDataId(self, _theFunctionData):
        theId = str(self.web3.toHex(self.web3.sha3(text=json.dumps(_theFunctionData))))
        return theId

    # This is a specific function which restricts the amount of data being returned i.e. instead of getting the entire record it only asks for and then returns the contractAddress and the abiSha3
    def fetchContractAddressesWithAbis(self):
        self.esAbiAddresses = []
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["abiShaList"] = "0x*"
        dWildCard["wildcard"] = dContractAddress 
        dMatch = {}
        dReauiresUpdating = {}
        dReauiresUpdating["field"] = "potentialFutureFilter"
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
        lContractAddress.append("contractAddress")
        lContractAddress.append("abiShaList")
        dQuery["_source"] = lContractAddress
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        for item in esReponseAddresses:
            for singleAbi in item["_source"]["abiShaList"]:
                obj = {}
                obj["abiSha3"] = singleAbi
                obj["contractAddress"] = item["_source"]["contractAddress"]
                self.esAbiAddresses.append(json.dumps(obj))
        #{'query': {'bool': {'must_not': [{'exists': {'field': 'byteSha3'}}], 'should': [{'wildcard': {'abiShaList': '0x*'}}]}}, '_source': ['contractAddress', 'abiShaList']}

    # This is a specific function which also restricts what is asked for and what is returned. More efficient on the ES instance.
    def fetchTxHashWithAbis(self):
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["abiShaList"] = "0x*"
        dWildCard["wildcard"] = dContractAddress 
        dMatch = {}
        dReauiresUpdating = {}
        dReauiresUpdating["field"] = "bytecodeSha3"
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
        #print(dQuery)
        # {"query": {"bool": {"must_not": [{"exists": {"field": "bytecodeSha3"}}], "should": [{"wildcard": {"abiShaList": "0x*"}}]}}, "_source": ["TxHash", "abiShaList"]}
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        listForResponse = []
        for item in esReponseAddresses:
            for singleAbi in item["_source"]["abiShaList"]:
                obj = {}
                obj["abiSha3"] = singleAbi
                obj["TxHash"] = item["_source"]["TxHash"]
                obj["contractAddress"] = item["_source"]["contractAddress"]
                listForResponse.append(json.dumps(obj))
        print("Found the following transactions that have abis but no bytecode:")
        #print(listForResponse)
        return listForResponse

    def sortInternalListsInJsonObject(self, _json):
        for listItem in _json:
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
        transactionData = self.web3.eth.getTransaction(str(_source["TxHash"]))
        listOfKeccakHashes = self.createUniqueAbiComparisons(_esAbiSingle)
        # for listOfKeccakHashes in theMasterList
        count = 0
        for individualHash in listOfKeccakHashes:
            if individualHash in transactionData.input:
                count += 1
            else:
                print("Hash not found, so move on quickly")
                # break out of this inner loop and keep trying the theMasterList
                break
        # If all hashes match then the abi in the master list belongs to this contract
        if count == len(listOfKeccakHashes):
            #try:
            newAbiSha = self.shaAnAbi(_esAbiSingle)
            newList = []
            found = False
            newData = self.es.get(index=self.commonIndex, id=_source["contractAddress"])
            if len(newData["_source"]["abiShaList"]) > 0:
                for item in newData["_source"]["abiShaList"]:
                    print("Comparing old and new abiSha")
                    print(item)
                    print(newAbiSha)
                    print("Finished comparing")
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

            # Update the ABI list in ES
            if len(newList) > 0 and found == False:
                doc = {}
                outerData = {}
                outerData["abiShaList"] = newList
                doc["doc"] = outerData
                self.updateDataInElastic(self.commonIndex, _source["contractAddress"], json.dumps(doc))
    
    def abiCompatabilityUpdateDriverPre2(self, _abi, _esTxs):
        txThreadList = []
        for i, doc2 in _esTxs.items():
            source = doc2['_source']
            tabiCompatabilityUpdateDriverPre2 = threading.Thread(target=self.abiCompatabilityUpdate, args=[_abi, source])
            tabiCompatabilityUpdateDriverPre2.daemon = True
            tabiCompatabilityUpdateDriverPre2.start()
            txThreadList.append(tabiCompatabilityUpdateDriverPre2)
        for abiCompatabilityUpdateDriverPre2Thread in txThreadList:
            abiCompatabilityUpdateDriverPre2Thread.join()


    def abiCompatabilityUpdateDriverPre1(self):
        self.abiCompatabilityUpdateDriverPre1Timer = time.time()
        while True:
            # Multithread lists
            abiThreadList = []
            # Get all of the ABIs
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
            print(TxObj)
            for doc1 in esAbis["hits"]["hits"]:
                source = doc1['_source']
                tabiCompatabilityUpdateDriverPre1 = threading.Thread(target=self.abiCompatabilityUpdateDriverPre2, args=[json.loads(source["abi"]), json.loads(json.dumps(TxObj))])
                tabiCompatabilityUpdateDriverPre1.daemon = True
                tabiCompatabilityUpdateDriverPre1.start()
                abiThreadList.append(tabiCompatabilityUpdateDriverPre1)
            for abiCompatabilityUpdateDriverPre1Thread in abiThreadList:
                abiCompatabilityUpdateDriverPre1Thread.join()
                        # Sleep if you have to
            self.abiCompatabilityUpdateDriverPre1Timer = self.abiCompatabilityUpdateDriverPre1Timer + 20
            if self.abiCompatabilityUpdateDriverPre1Timer > time.time():
                print("Finished before time limit, will sleep now ...")
                time.sleep(self.abiCompatabilityUpdateDriverPre1Timer - time.time())
                print("Back awake and ready to go ...")
            else:
                print("It has been longer than the desired time, need to re-update the state immediately ...")

    def processSingleTransaction(self,_contractAbiJSONData, _transactionHex):
        #print("Transaction Hex: \n" + str(_transactionHex))
        transactionData = self.web3.eth.getTransaction(str(_transactionHex))
        #print("Transaction Data: \n" + str(transactionData))
        transactionReceipt = self.web3.eth.getTransactionReceipt(str(_transactionHex))
        #print("Transaction Receipt: \n" + str(transactionReceipt))
        itemId = None
        try:
            itemId = transactionReceipt.contractAddress
            print("Found contract: " + itemId)
        except:
            print("No contract here ...")
        if itemId != None:
            dataStatus = self.hasDataBeenIndexed(self.commonIndex, itemId)
            if dataStatus == False:
                try:                                    
                    contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=itemId)
                    functionData = self.fetchPureViewFunctionData(contractInstance)
                    functionDataId = self.getFunctionDataId(functionData)
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
                    #print(json.dumps(outerData))
                    print("************** LOADING DATA INTO ELASTICSEARCH **************")
                    indexResult = self.loadDataIntoElastic(self.commonIndex, itemId, json.dumps(outerData))
                except:
                    print("Unable to instantiate web3 contract object")
            else:
                print("Item is already indexed")
        else:
            print("Problem with transaction hex: " + str(_transactionHex))


    def harvest(self, _esAbiSingle, _argList,  _topup=False):
        self.upcomingCallTimeHarvest = time.time()
        contractAbiJSONData = json.loads(_esAbiSingle['_source']['abi'])
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
                print("\nProcessing block number %s" % blockNumber)
                blockTransactionCount = self.web3.eth.getBlockTransactionCount(blockNumber)
                if blockTransactionCount > 0:
                    block = self.web3.eth.getBlock(blockNumber)
                    for singleTransaction in block.transactions:
                        singleTransactionHex = str(self.web3.toHex(singleTransaction))
                        self.processSingleTransaction(contractAbiJSONData, singleTransactionHex)
                else:
                    print("Skipping block number %s - No transactions found!" % blockNumber)
                    continue

            if _topup == True and len(_argList) == 0:
                self.upcomingCallTimeHarvest = self.upcomingCallTimeHarvest + 10
                if self.upcomingCallTimeHarvest > time.time():
                    time.sleep(self.upcomingCallTimeHarvest - time.time())
            else:
                if _topup == False and len(_argList) == 2:
                    break

    def harvestBlocksDriver(self, _stop=False):
        print("harvestDriver")
        queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
        esAbis = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex, query=queryForAbiIndex, preserve_order=True)
        harvestDriverThreads = []
        # Creating a thread for every available ABI, however this can be set to a finite amount when sharded indexers/harvesters are in
        # TODO we will also have to set both the indexingInProgress to true and the epochOfLastUpdate to int(time.time) via the updateDataInElastic fuction in this class once we move to sharded indexers/harvesters
        latestBlockNumber = self.web3.eth.getBlock('latest').number
        threadsToUse = 100
        blocksPerThread = int(latestBlockNumber / threadsToUse)
        for esAbiSingle in esAbis:
            if _stop == False:
                for startingBlock in range(1, latestBlockNumber, blocksPerThread):
                    argList = []
                    argList.append(startingBlock)
                    argList.append(blocksPerThread)
                    tFullDriver = threading.Thread(target=self.harvest, args=[esAbiSingle, argList, _stop])
                    tFullDriver.daemon = True
                    tFullDriver.start()
                    harvestDriverThreads.append(tFullDriver)
            else:
                if _stop == True:
                    argList = []
                    tFullDriver = threading.Thread(target=self.harvest, args=[esAbiSingle, argList, _stop])
                    tFullDriver.daemon = True
                    tFullDriver.start()
                    harvestDriverThreads.append(tFullDriver)
        for harvestDriverThread in harvestDriverThreads:
            harvestDriverThread.join()

    def processMultipleTransactions(self, _esAbiSingle, _esTransactions):
        processMultipleTransactionsThreads = []
        contractAbiJSONData = json.loads(_esAbiSingle)
        for transactionHash in reversed(_esTransactions):
            tFullDriver3 = threading.Thread(target=self.processSingleTransaction, args=[contractAbiJSONData, transactionHash])
            tFullDriver3.daemon = True
            tFullDriver3.start()
            time.sleep(4)
            processMultipleTransactionsThreads.append(tFullDriver3)
        for harvestDriverThread3 in processMultipleTransactionsThreads:
            harvestDriverThread3.join()


    def harvestTransactionsDriver(self):
        print("Harvesting transactions from masterindex")
        # Fetch the ABIs from the abi index
        queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
        esAbis = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex, query=queryForAbiIndex, preserve_order=True)
        harvestTransactionsDriverThreads = []
        # Store the results from the generator in a local list because we can only have one generator open at a time
        localAbiList = []
        for esAbiSingle in esAbis:
            #print("Adding: " + esAbiSingle['_source']['abi'])
            localAbiList.append(esAbiSingle['_source']['abi'])
        # Fetch the transactions from the master index
        queryForTransactionIndex = {"query":{"bool":{"must":[{"match":{"indexed":"false"}}]}}}
        esTransactions = elasticsearch.helpers.scan(client=self.es, index=self.masterIndex, query=queryForTransactionIndex, preserve_order=True)
        # Creating a thread for every available ABI, however this can be set to a finite amount when sharded indexers/harvesters are in
        # TODO we will also have to set both the indexingInProgress to true and the epochOfLastUpdate to int(time.time) via the updateDataInElastic fuction in this class once we move to sharded indexers/harvesters
        localTransactionList = []
        #i = 0
        for esTransactionSingle in esTransactions:
        #    i = i + 1
        #    if i < 200:
        #        print("Adding: " + esTransactionSingle['_source']['TxHash'])
            localTransactionList.append(esTransactionSingle['_source']['TxHash'])
        for localEsAbiSingle in localAbiList:
            tFullDriver2 = threading.Thread(target=self.processMultipleTransactions, args=[localEsAbiSingle, localTransactionList])
            tFullDriver2.daemon = True
            tFullDriver2.start()
            harvestTransactionsDriverThreads.append(tFullDriver2)
        for harvestDriverThread2 in harvestTransactionsDriverThreads:
            harvestDriverThread2.join()


    def fetchContractInstances(self, _contractAbiId, _contractAddress):
        jsonAbiDataForInstance = json.loads(self.fetchAbiUsingHash(_contractAbiId))
        contractInstance = self.web3.eth.contract(abi=jsonAbiDataForInstance, address=_contractAddress)
        self.contractInstanceList.append(contractInstance)


    def worker(self, _instance):
        print("Processing Instance With Address Of: " + _instance.address)
        #if _instance.address == "0x63Da8D2d6dEa6635E5aeb2150cF3E7D2bB23D604":
        freshFunctionData = self.fetchPureViewFunctionData(_instance)
        functionDataId = self.getFunctionDataId(freshFunctionData)
        abiHash = self.shaAnAbi(_instance.abi)
        uniqueAbiAndAddressKey = str(abiHash) + str(_instance.address)
        uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
        if uniqueAbiAndAddressHash not in self.addressAndFunctionDataHashes.keys():
            print("Instance " + uniqueAbiAndAddressHash + " not in the list yet")
            self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] = ""
        if self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] != functionDataId:
            print("The data is different so we will update " + uniqueAbiAndAddressHash + " record now")
            functionDataObjectOuter = {}
            functionDataObjectInner = {}
            functionDataObjectInner['functionDataId'] = functionDataId
            functionDataObjectInner['functionData'] = freshFunctionData
            functionDataObjectInner['uniqueAbiAndAddressHash'] = uniqueAbiAndAddressHash
            self.addressAndFunctionDataHashes[uniqueAbiAndAddressHash] = functionDataId
            newList = []
            found = False
            print(newList)
            newData = self.es.get(index=self.commonIndex, id=_instance.address)
            if len(newData["_source"]["functionDataList"]["0"]) > 0:
                for item in newData["_source"]["functionDataList"]["0"]:
                    for k, v in item.items():
                        if k == "uniqueAbiAndAddressHash":
                            if v == uniqueAbiAndAddressHash:
                            # Override the existing data with the newly fetched data
                                newList.append(functionDataObjectInner)
                                found = True
                            else:
                                # Just place this already existing item in the list so it can remain in the index as is
                                print("Adding existing data to newList")
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
            print(newList)
            print("\n")
            print(json.dumps(doc))
            print("\n")

            # Now we can add our updated list 
            self.updateDataInElastic(self.commonIndex, _instance.address, json.dumps(doc))
        else:
            print("The data is still the same so we will move on ...")


    def updateStateDriverPre(self):
        self.updateStateDriverPreTimer = time.time()
        self.addressAndFunctionDataHashes = {}
        # Fetch the addresses and ABI hash of records that have an ABI Hash stored (abiSha3)
        self.fetchContractAddressesWithAbis()
        # Purge the contract instance list as we are about to freshly populate it
        self.contractInstanceList = []
        # Populate the global cache of web3 contract instances by instantiating the using the ABI and address from the previously fetched list
        for singleEntry in self.esAbiAddresses:
            print(singleEntry)
            abiAndAddress = json.loads(singleEntry)
            self.fetchContractInstances(abiAndAddress["abiSha3"], abiAndAddress["contractAddress"])
        while True:
            print("updateStateDriverPre")           
            originalListOfAddressesAndAbi = self.esAbiAddresses
            origListOfAddresses = []
            for originalItem in originalListOfAddressesAndAbi:
                originalItemJSON = json.loads(originalItem)
                #TODO
                uniqueAbiAndAddressKey = str(originalItemJSON['abiSha3']) + str(originalItemJSON['contractAddress'])
                uniqueAbiAndAddressHash = str(self.web3.toHex(self.web3.sha3(text=uniqueAbiAndAddressKey)))
                if uniqueAbiAndAddressHash not in origListOfAddresses:
                    origListOfAddresses.append(uniqueAbiAndAddressHash)
            self.fetchContractAddressesWithAbis()
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
            # Join all of the instances in the list to end this round
            for updateStateThreads1 in threadsupdateStateDriverPre:
                updateStateThreads1.join()
            print("Finished updateStateDriverPreTimer...")
            # Sleep if you have to
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
        # Run this once every 5 minutes
        while True:
            print("Starting ...")
            self.threadsUpdateBytecode = []
            versionless = self.fetchTxHashWithAbis()
            for versionlessItem in versionless:
                print(versionlessItem)
                versionlessItemJSON = json.loads(versionlessItem)
                tVersionless = threading.Thread(target=self.updateBytecodeAndVersion, args=[versionlessItemJSON["TxHash"], versionlessItemJSON["contractAddress"]])
                tVersionless.daemon = True
                tVersionless.start()
                self.threadsUpdateBytecode.append(tVersionless)
            for individualVersionlessThread in self.threadsUpdateBytecode:
                individualVersionlessThread.join()
            print("Finished")
            self.tupdateBytecode = self.tupdateBytecode + 30
            if self.tupdateBytecode > time.time():
                time.sleep(self.tupdateBytecode - time.time())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup|state]", type=str, default="full")
    args = parser.parse_args()

    harvester = Harvest()

    if args.mode == "full":
        print("Performing full harvest")
        harvester.harvestBlocksDriver()
    elif args.mode == "topup":
        print("Performing topup")
        harvester.harvestBlocksDriver(True)
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
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
        print("harvest.py --mode state")
        print("harvest.py --mode tx")
        print("harvest.py --mode bytecode")
        print("harvest.py --mode abi")

# Monitor the total number of threads on the operating system
# ps -eo nlwp | tail -n +2 | awk '{ total_threads += $1 } END { print total_threads }'

# Monitor the number of threads per pid; run any of the following commands and paste THE_PID into the watch command below
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m full >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m topup >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &

# watch -n 2 -d "ps -eL THE_PID | wc -l"
