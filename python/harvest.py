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

    # This is a specific function which restricts the amount of data being returned i.e. instead of getting the entire record it only asks for and then returns the contractAddress and the abiSha3
    def fetchContractAddressesWithAbis(self):
        self.esAbiAddresses = []
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["abiSha3"] = "0x*"
        dWildCard["wildcard"] = dContractAddress 
        dMatch = {}
        dReauiresUpdating = {}
        dReauiresUpdating["field"] = "byteSha3"
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
        lContractAddress.append("abiSha3")
        dQuery["_source"] = lContractAddress
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        for item in esReponseAddresses:
            self.esAbiAddresses.append(item["_source"])
        #{'query': {'bool': {'must_not': [{'exists': {'field': 'byteSha3'}}], 'should': [{'wildcard': {'abiSha3': '0x*'}}]}}, '_source': ['contractAddress', 'abiSha3']}

    # This is a specific function which also restricts what is asked for and what is returned. More efficient on the ES instance.
    def fetchTxHashWithAbis(self):
        dQuery = {}
        dWildCard = {}
        dContractAddress = {}
        lContractAddress = []
        dContractAddress["abiSha3"] = "0x*"
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
        lContractAddress.append("abiSha3")
        dQuery["_source"] = lContractAddress
        # {"query": {"bool": {"must_not": [{"exists": {"field": "bytecodeSha3"}}], "should": [{"wildcard": {"abiSha3": "0x*"}}]}}, "_source": ["TxHash", "abiSha3"]}
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        return esReponseAddresses


    def shaAnAbiWithOrderedKeys(self, _theAbi):
        theAbiHash = str(self.web3.toHex(self.web3.sha3(text=json.dumps(_theAbi, sort_keys=True))))
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
            try:
                newAbiSha = shaAnAbiWithOrderedKeys(_esAbiSingle)
                newList = []
                found = False
                newData = es.get(index=commonIndex, id=_source["contractAddress"])
                if len(newData["_source"]["abiShaList"]) > 0:
                    for item in newData["_source"]["abiShaList"]:
                        if item == newAbiSha:
                            print("Already have hash of " + item)
                            found = True
                            break
                        else:
                            newList.append(newAbiSha)
                            print("Keep comparing")
                    if found == False:
                        newList.append(newAbiSha)
                else:
                    newList.append(newAbiSha)

                # Update the ABI list in ES
                doc = {}
                outerData = {}
                outerData["abiShaList"] = newList
                doc["doc"] = outerData
                updateDataInElastic(index=commonIndex, id=_source["contractAddress"], body=json.dumps(doc))

                # Update the version in ES
                stringToHash = ""
                for abiItem in newList:
                    print("Adding %s " % str(abiItem))
                    stringToHash = stringToHash + str(abiItem)
                stringToHash = stringToHash + str(_source["bytecodeSha3"])
                newVersionHash = self.web3.toHex(self.web3.sha3(text=stringToHash))
                # Update the version list in ES
                doc = {}
                outerData = {}
                outerData["abiSha3BytecodeSha3"] = newVersionHash
                doc["doc"] = outerData
                updateDataInElastic(index=commonIndex, id=_source["contractAddress"], body=json.dumps(doc))
            except:
                print("An exception occured! - Please try and load contract at address: %s manually to diagnose." % transactionContractAddress)
    
    def abiCompatabilityUpdateDriverPre2(self, _abi, _esTxs):
        txThreadList = []
        for doc2 in _esTxs:
            print(doc2)
            source = doc2['_source']
            tabiCompatabilityUpdateDriverPre2 = threading.Thread(target=self.abiCompatabilityUpdate, args=[_abi, source])
            tabiCompatabilityUpdateDriverPre2.daemon = True
            tabiCompatabilityUpdateDriverPre2.start()
            txThreadList.append(tabiCompatabilityUpdateDriverPre2)
        for abiCompatabilityUpdateDriverPre2Thread in txThreadList:
            abiCompatabilityUpdateDriverPre2Thread.join()


    def abiCompatabilityUpdateDriverPre1(self):
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
                        singleTransactionHex = singleTransaction.hex()
                        transactionData = self.web3.eth.getTransaction(str(singleTransactionHex))
                        transactionReceipt = self.web3.eth.getTransactionReceipt(str(singleTransactionHex))
                        itemId = transactionReceipt.contractAddress
                        dataStatus = self.hasDataBeenIndexed(self.commonIndex, itemId)
                        if dataStatus == False:
                            transactionContractAddress = transactionReceipt.contractAddress
                            if transactionContractAddress != None:
                                try:                                    
                                    contractInstance = self.web3.eth.contract(abi=contractAbiJSONData, address=transactionContractAddress)
                                    functionData = self.fetchPureViewFunctionData(contractInstance)
                                    functionDataId = self.getFunctionDataId(functionData)
                                except:
                                    print("Not able to create a contract instance using that ABI")
                                    continue
                                outerData = {}
                                outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                outerData['abiShaList'] = []
                                outerData['blockNumber'] = transactionReceipt.blockNumber
                                outerData['contractAddress'] = transactionReceipt.contractAddress
                                outerData['functionDataId'] = functionDataId
                                outerData['functionData'] = functionData
                                outerData["requiresUpdating"] = "yes"
                                outerData['quality'] = "50"
                                outerData['indexInProgress'] = "false"
                                indexResult = self.loadDataIntoElastic(self.commonIndex, itemId, json.dumps(outerData))

                            else:
                                print("This transaction does not involve a contract, so we will ignore it")
                                continue
                        else:
                            print("Item is already indexed")
                            continue
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

    def harvestDriver(self, _stop=False):
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


    def fetchContractInstances(self, _contractAbiId, _contractAddress):
        jsonAbiDataForInstance = json.loads(self.fetchAbiUsingHash(_contractAbiId))
        contractInstance = self.web3.eth.contract(abi=jsonAbiDataForInstance, address=_contractAddress)
        self.contractInstanceList.append(contractInstance)

    def worker(self, _instance):
        #print(self.addressAndFunctionDataHashes)
        freshFunctionData = self.fetchPureViewFunctionData(_instance)
        functionDataId = self.getFunctionDataId(freshFunctionData)
        #print("functionDataId")
        #print(functionDataId)
        if _instance.address not in self.addressAndFunctionDataHashes.keys():
            print("Instance " +  _instance.address + "not in the list yet")
            self.addressAndFunctionDataHashes[_instance.address] = ""
        if self.addressAndFunctionDataHashes[_instance.address] != functionDataId:
            print("The data is different so we will update " + _instance.address + " record now")
            #try:
            self.addressAndFunctionDataHashes[_instance.address] = functionDataId
            #print(self.addressAndFunctionDataHashes)
            itemId = _instance.address
            doc = {}
            outerData = {}
            outerData["functionData"] = freshFunctionData
            outerData["functionDataId"] = functionDataId
            doc["doc"] = outerData
            indexResult = self.updateDataInElastic(self.commonIndex, itemId, json.dumps(doc))
            #except:
            #    print("Unable to update the state data in the worker function")
        else:
            print("The data is still the same so we will move on ...")

    def updateStateDriverPre(self):
        self.firstRun = True
        self.updateStateDriverPreTimer = time.time()
        self.addressAndFunctionDataHashes = {}
        # Fetch the addresses and ABI hash of records that have an ABI Hash stored (abiSha3)
        self.fetchContractAddressesWithAbis()
        #print(self.esAbiAddresses)
        # Create a hash of the list which holds both the address and the ABI hash
        self.esAbiAddressesHash = self.web3.toHex(self.web3.sha3(text=str(self.esAbiAddresses)))
        # Purge the contract instance list as we are about to freshly populate it
        self.contractInstanceList = []
        # Populate the global cache of web3 contract instances by instantiating the using the ABI and address from the previously fetched list
        for esAbiSingle in self.esAbiAddresses:                    
            self.fetchContractInstances(esAbiSingle['abiSha3'], esAbiSingle['contractAddress'])
            print("Instantiated address " + esAbiSingle['contractAddress'])
        print("The following contract instances now exist")
        #print(self.contractInstanceList)
        
        while True:
            print("updateStateDriverPre")           
            originalListOfAddressesAndAbi = self.esAbiAddresses
            origListOfAddresses = []
            for originalItem in originalListOfAddressesAndAbi:
                if originalItem['contractAddress'] not in origListOfAddresses:
                    origListOfAddresses.append(originalItem['contractAddress'])
            self.fetchContractAddressesWithAbis()
            for newItem in self.esAbiAddresses:
                if newItem['contractAddress'] not in origListOfAddresses:
                    print("Found a new contract " + newItem['contractAddress'] + ", creating a new web3 instance")
                    self.fetchContractInstances(newItem['abiSha3'], newItem['contractAddress'])
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

    def updateBytecodeAndVersion(self, _txHash, _abiSha3, _esId):
        transactionInstance = self.web3.eth.getTransaction(str(_txHash))
        dMatchAllInner = {}
        dMatchAll = {}
        dMatchAll["match_all"] = dMatchAllInner
        dQuery = {}
        dQuery["query"] = dMatchAll
        esReponseByte = elasticsearch.helpers.scan(client=self.es, index=self.bytecodeIndex , query=json.dumps(dQuery), preserve_order=True)
        for i, doc in enumerate(esReponseByte):
            source = doc.get('_source')
            print("Processing " + str(source))
            if source["bytecode"] in transactionInstance.input:
                print("Found bytecode")
                doc = {}
                outerData = {}
                bytecodeSha3 = self.web3.toHex(self.web3.sha3(text=source["bytecode"]))
                abiBytecode = _abiSha3 + bytecodeSha3
                abiSha3BytecodeSha3 = self.web3.toHex(self.web3.sha3(text=abiBytecode))
                outerData["bytecodeSha3"] = bytecodeSha3
                outerData["abiSha3BytecodeSha3"] = abiSha3BytecodeSha3
                doc["doc"] = outerData
                self.updateDataInElastic(self.commonIndex, _esId, json.dumps(doc))
            # else:
            #     print("Did not find bytecode:")
            #     print(str(source["bytecode"]))
            #     print("inside the following transaction input")
            #     print(transactionInstance.input)

    def updateBytecode(self):
        self.tupdateBytecode = time.time()
        # Run this once every 5 minutes
        while True:
            print("Starting ...")
            self.threadsUpdateBytecode = []
            versionless = self.fetchTxHashWithAbis()
            for i, doc in enumerate(versionless):
                source = doc.get('_source')
                #print(source)
                tVersionless = threading.Thread(target=self.updateBytecodeAndVersion, args=[source["TxHash"], source["abiSha3"], doc.get('_id')])
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
        harvester.harvestDriver()
    elif args.mode == "topup":
        print("Performing topup")
        harvester.harvestDriver(True)
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
        print("harvest.py --mode bytecode")

# Monitor the total number of threads on the operating system
# ps -eo nlwp | tail -n +2 | awk '{ total_threads += $1 } END { print total_threads }'

# Monitor the number of threads per pid; run any of the following commands and paste THE_PID into the watch command below
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m full >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m topup >/dev/null 2>&1 &
#cd ~/htdocs/python && nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &

# watch -n 2 -d "ps -eL THE_PID | wc -l"
