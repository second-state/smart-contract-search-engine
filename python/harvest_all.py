# Harvest all is a script that will find (and index in the masterindex->all index which is set in the config.ini) every transaction receipt which has a contract address associated with it.
# More specifically, it is a quick reference index which can provide a) the transactionHash to a caller who can provide an actual contract address.
# Once the caller has the transactionHash, they can go ahead and fetch any and all information such as receipts, block number etc. In addition, if they also have the correct ABI, they can even create a web3 contract instance.
# The search engine uses this file to rapidly index all of the transactions that involve a contract. If a user uploads an ABI and contract address the code for the upload can quickly obtain everything it needs in order to properly index that contract in the common index (the commonindex->network which is set in the config.ini)


import os
import sys
import json
import boto3
import time
import argparse
import threading
import configparser
import elasticsearch.helpers
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

class Harvest:
    def __init__(self):
        self.scriptExecutionLocation = os.getcwd()

        # Config
        print("Reading configuration file")
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.config.read(os.path.join(self.scriptExecutionLocation, 'config.ini'))

        # Blockchain RPC
        self.blockchainRpc = self.config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

        # Master index
        self.masterIndex = self.config['masterindex']['all']
        print("Master index: %s" % self.masterIndex)

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

    def loadDataIntoElastic(self, _theIndex, _theId, _thePayLoad):
        esReponseD = self.es.index(index=_theIndex, id=_theId, body=_thePayLoad)
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
                            #try:
                            outerData = {}
                            outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                            outerData['blockNumber'] = transactionReceipt.blockNumber
                            outerData['contractAddress'] = transactionReceipt.contractAddress
                            # from is the contract's creator
                            outerData['from'] = transactionReceipt['from']
                            outerData["indexed"] = "false"
                            #outerData['abi'] = "false"
                            #outerData['bytecode'] = "false"
                            #outerData['abiSha3'] = "false"
                            #outerData['bytecodeSha3'] = "false"
                            #outerData['abiSha3bytecodeSha3'] = "false"
                            # indexingInProgress is a placeholder/lock for sharded harvesting in the future
                            #outerData['indexingInProgress'] = "false"
                            # contractDestructed will be set by external web3 script
                            #outerData['contractDestructed'] = "false"
                            # epochOfLastUpdate will be updated by each sharded harvester/indexer and used to detect if a sharded harvester/indexer has gone off line with the indexingInProgress flag set to true
                            # epochOfLastUpdate will be monitored by external script (the purpose to set the indexingInProgress to false in cases where no recent activity is detected)
                            # i.e. if contractDestructed == "false" and indexingInProgress == "true" and (time.now - epochOfLastUpdate > 24 hours)
                            #outerData['epochOfLastUpdate'] = block.timestamp
                            itemId = transactionReceipt.contractAddress
                            dataStatus = self.hasDataBeenIndexed(esIndex, itemId)
                            if dataStatus == False:
                                singleItem = {"_index":str(esIndex), "_id": str(itemId), "_type": "_doc", "_op_type": "index", "_source": json.dumps(outerData)}
                                bulkList.append(singleItem)
                                print("Added item to BULK list, we now have " + str(len(bulkList)))
                                if len(bulkList) == 50:
                                    elasticsearch.helpers.bulk(self.es, bulkList)
                                    time.sleep(2)
                                    bulkList = []
                                    time.sleep(2)
                                    #indexResult = self.loadDataIntoElastic(esIndex, itemId, json.dumps(outerData))
                            #except:
                            #    print("Error indexing contract")
                        else:
                            #print("This transaction does not involve a contract, so we will ignore it")
                            continue
                else:
                    print("Skipping block number %s - No transactions found!" % blockNumber)
                    continue
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
    parser.add_argument("-m", "--mode", help="[full|topup]", type=str, default="full")
    args = parser.parse_args()

    harvester = Harvest()

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
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
