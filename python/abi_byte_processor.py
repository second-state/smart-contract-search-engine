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

        # Add list for unique queueing

        self.qList = []

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
        # dQuery
        # {'query': {'bool': {'must': [{'match': {'requiresUpdating': 'yes'}}], 'should': [{'wildcard': {'contractAddress': '0x*'}}]}}, '_source': ['contractAddress']}
        # {"query":{"match":{"indexingInProgress": "false"}}}
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=_theIndex, query=json.dumps(dQuery), preserve_order=True)
        uniqueList = []
        for i, doc in enumerate(esReponseAddresses):
            source = doc.get('_source')
            if source['contractAddress'] not in uniqueList:
                uniqueList.append(source['contractAddress'])
        return uniqueList

    def fetchContractAddressesWithAbis(self):
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
        return esReponseAddresses

    def fetchTxHashWithAbis(self):
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
        lContractAddress.append("TxHash")
        dQuery["_source"] = lContractAddress
        esReponseAddresses = elasticsearch.helpers.scan(client=self.es, index=self.commonIndex, query=json.dumps(dQuery), preserve_order=True)
        return esReponseAddresses

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

    def harvest(self, _esAbiSingle,  _stop=False):
        self.upcomingCallTimeHarvest = time.time()
        contractAbiJSONData = json.loads(_esAbiSingle['_source']['abi'])

        # binObject = requests.get(self.config['bytecode'][itemConf[0]]).content
        # binJSONObject = json.loads(binObject)
        # byteCode = "0x" + binJSONObject['object']

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
                            # This will be a list of a list of unique ABI comparisons which we get from the IUAC index
                            # the IUAC index will already have been populated using the createUniqueAbiComparisons functions before hand by another process
                            listOfKeccakHashes = self.createUniqueAbiComparisons(contractAbiJSONData)
                            
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
                                    outerData = {}
                                    contractInstance = self.web3.eth.contract(abi=contractAbiJSONData, address=transactionContractAddress)
                                    outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                    outerData['abiSha3'] = str(self.web3.toHex(self.web3.sha3(text=json.dumps(contractInstance.abi))))
                                    outerData['blockNumber'] = transactionReceipt.blockNumber
                                    outerData['contractAddress'] = transactionReceipt.contractAddress
                                    functionData = self.fetchPureViewFunctionData(contractAbiJSONData, contractInstance)
                                    functionDataId = self.getFunctionDataId(functionData)
                                    outerData['functionDataId'] = functionDataId
                                    outerData['functionData'] = functionData
                                    itemId = transactionReceipt.contractAddress
                                    dataStatus = self.hasDataBeenIndexed(self.commonIndex, itemId)
                                    if dataStatus == False:
                                        indexResult = self.loadDataIntoElastic(self.commonIndex, itemId, json.dumps(outerData))
                                except:
                                    print("An exception occured! - Please try and load contract at address: %s manually to diagnose." % transactionContractAddress)
                        else:
                            print("This transaction does not involve a contract, so we will ignore it")
                            continue
                else:
                    print("Skipping block number %s - No transactions found!" % blockNumber)
                    continue
            if _stop == False:
                self.qList[_queueIndex].task_done()
            self.upcomingCallTimeHarvest = self.upcomingCallTimeHarvest + 10
            if self.upcomingCallTimeHarvest > time.time():
                time.sleep(self.upcomingCallTimeHarvest - time.time())

    def harvestDriver(self, _stop=False):
        print("harvestDriver")
        queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
        esAbis = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex, query=queryForAbiIndex, preserve_order=True)
        harvestDriverThreads = []
        # Creating a thread for every available ABI, however this can be set to a finite amount when sharded indexers/harvesters are in
        # TODO we will also have to set both the indexingInProgress to true and the epochOfLastUpdate to int(time.time) via the updateDataInElastic fuction in this class once we move to sharded indexers/harvesters
        for esAbiSingle in esAbis:
            tFullDriver = threading.Thread(target=self.harvest, args=[esAbiSingle, _stop])
            tFullDriver.daemon = True
            tFullDriver.start()
            harvestDriverThreads.append(tFullDriver)
        for harvestDriverThread in harvestDriverThreads:
            harvestDriverThread.join()

    def bytecodeDriver(self, _stop=False):
        print("harvestDriver")
        queryForAbiIndex = {"query":{"match":{"indexInProgress": "false"}}}
        esAbis = elasticsearch.helpers.scan(client=self.es, index=self.abiIndex, query=queryForAbiIndex, preserve_order=True)
        harvestDriverThreads = []
        # Creating a thread for every available ABI, however this can be set to a finite amount when sharded indexers/harvesters are in
        # TODO we will also have to set both the indexingInProgress to true and the epochOfLastUpdate to int(time.time) via the updateDataInElastic fuction in this class once we move to sharded indexers/harvesters
        for esAbiSingle in esAbis:
            tFullDriver = threading.Thread(target=self.harvest, args=[esAbiSingle, _stop])
            tFullDriver.daemon = True
            tFullDriver.start()
            harvestDriverThreads.append(tFullDriver)
        for harvestDriverThread in harvestDriverThreads:
            harvestDriverThread.join()


    # State related
    def fetchUniqueContractList(self, _esIndex):
        self.uniqueContractList = []
        self.uniqueContractList = self.fetchContractAddresses(_esIndex)

    def fetchContractInstances(self, _contractAbiJSONData):
        #TODO this assumes that there is only one contract abi we need to pass in both the abi and the address for this to work
        self.contractInstanceList = []
        for uniqueContractAddress in self.uniqueContractList:
            contractInstance = self.web3.eth.contract(abi=_contractAbiJSONData, address=uniqueContractAddress)
            self.contractInstanceList.append(contractInstance)

    def worker(self, _esIndex, _contractAbiJSONData, _queueIndex):
        while True:
            item = self.qList[_queueIndex].get()
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
                theStatus = freshFunctionData['info'][0]
                if theStatus == 0:
                    outerData['requiresUpdating'] = "yes"
                elif theStatus == 1:
                    outerData['requiresUpdating'] = "no"
                doc["doc"] = outerData
                indexResult = self.updateDataInElastic(_esIndex, itemId, json.dumps(doc))
            self.qList[_queueIndex].task_done()

    def performStateUpdate(self, _esIndex, _contractAbiJSONData):
        self.upcomingCallTimeState = time.time()
        while True:
            self.fetchUniqueContractList(_esIndex)
            self.uniqueContractListHashOrig = self.uniqueContractListHashFresh
            self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.uniqueContractList))))
            if self.uniqueContractListHashFresh != self.uniqueContractListHashOrig:
                self.fetchContractInstances(_contractAbiJSONData)
            q = queue.Queue()
            queueIndex = len(self.qList)
            self.qList.append(q)
            self.threads = []
            # Set the number of threads
            threadCount = len(self.uniqueContractList)
            for i in range(threadCount):
                t = threading.Thread(target=self.worker, args=[_esIndex, _contractAbiJSONData, queueIndex])
                t.start()
                self.threads.append(t)
            for uniqueContractInstance in self.contractInstanceList:
                # Put a web3 contract object instance in the queue
                self.qList[queueIndex].put(uniqueContractInstance)
            # block untill all tasks are done
            self.qList[queueIndex].join()
            for i in range(threadCount):
                self.qList[queueIndex].put(None)
            for t in self.threads:
                t.join()
            # set the time interval for when this task will be repeated
            self.upcomingCallTimeState = self.upcomingCallTimeState + 10
            # If this takes longer than the break time, then just continue straight away
            if self.upcomingCallTimeState > time.time():
                time.sleep(self.upcomingCallTimeState - time.time())

    def updateStateDriver(self, _esAbiSingle):
        contractAbiJSONData = json.loads(_esAbiSingle['_source']['abi'])
        self.fetchUniqueContractList(esIndex)
        self.fetchContractInstances(contractAbiJSONData)
        self.uniqueContractListHashFresh = str(self.web3.toHex(self.web3.sha3(text=str(self.uniqueContractList))))
        self.performStateUpdate(esIndex, contractAbiJSONData)

    def updateStateDriverPre(self):
        print("updateStateDriverPre")
        esAbiHashes = fetchContractAddressesWithAbis()
        self.threadsupdateStateDriverPre = []
        # Creating a thread for every available ABI, however this can be set to a finite amount when sharded indexers/harvesters are in
        for esAbiSingle in esAbiHashes:

            tupdateStateDriverPre = threading.Thread(target=self.updateStateDriver, args=[esAbiSingle])
            tupdateStateDriverPre.daemon = True
            tupdateStateDriverPre.start()
            self.threadsupdateStateDriverPre.append(tupdateStateDriverPre)
        for updateStateThreads1 in self.threadsupdateStateDriverPre:
            updateStateThreads1.join()

    def loadConfigIniToES(self):
        for key in self.config['abis']:
            stringKey = str(key)
            tempData = {}
            tempData["url"] = self.config['abis'][key]
            tempData["json"] = re.sub(r"[\n\t\s]*", "", json.dumps(json.loads(requests.get(self.config['abis'][key]).content)))

    def fetchAbiUsingHash(self, _esId):
        #try:
        print("ID=" + _esId)
        esReponseAbi = self.es.get(index=self.abiIndex , id=_esId)
        stringAbi = json.dumps(esReponseAbi["_source"]["abi"])
        jsonAbi = json.loads(stringAbi)
        return jsonAbi
        #except:
        #    print("Unable to fetch ABI from the ABI index")
        

    def updateBytecodeAndVersion(self, _txHash):
        transactionInstance = self.web3.eth.getTransaction(str(_txHash))
        print(transactionInstance)
        


    def updateBytecode(self):
        self.threadsUpdateBytecode = []
        versionless = self.fetchTxHashWithAbis()
        for i, doc in enumerate(versionless):
            source = doc.get('_source')
            print(source)
            tVersionless = threading.Thread(target=self.updateBytecodeAndVersion, args=[source["TxHash"]])
            tVersionless.daemon = True
            tVersionless.start()
            self.threadsUpdateBytecode.append(tVersionless)
        for individualVersionlessThread in self.threadsUpdateBytecode:
            individualVersionlessThread.join()


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
