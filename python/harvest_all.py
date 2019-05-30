import os
import sys
import json
import boto3
import time
import argparse
import threading
import configparser
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
                            try:
                                outerData = {}
                                outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                outerData['blockNumber'] = transactionReceipt.blockNumber
                                outerData['contractAddress'] = transactionReceipt.contractAddress
                                outerData['from'] = transactionReceipt['from']
                                outerData['abi'] = "false"
                                outerData['bytecode'] = "false"
                                outerData['inProgress'] = "false"
                                outerData['epochOfLastUpdate'] = block.timestamp
                                itemId = str(self.web3.toHex(self.web3.sha3(text=transactionReceipt.contractAddress)))
                                dataStatus = self.hasDataBeenIndexed(esIndex, itemId)
                                if dataStatus == False:
                                    indexResult = self.loadDataIntoElastic(esIndex, itemId, json.dumps(outerData))
                            except:
                                print("Error indexing contract")
                        else:
                            print("This transaction does not involve a contract, so we will ignore it")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvester < https://github.com/second-state/smart-contract-search-engine >")
    parser.add_argument("-m", "--mode", help="[full|topup]", type=str, default="full")
    args = parser.parse_args()

    harvester = Harvest()

    if args.mode == "full":
        print("Performing full harvest")
        latestBlockNumber = harvester.web3.eth.getBlock('latest').number
        threadsToUse = 100
        blocksPerThread = int(latestBlockNumber / threadsToUse)
        harvester.fastThreads = []
        for startingBlock in range(1, latestBlockNumber, blocksPerThread):
            argList = []
            argList.append(startingBlock)
            argList.append(blocksPerThread)
            tFullDriver = threading.Thread(target=harvester.harvestAllContracts, args=["all", argList, False])
            tFullDriver.daemon = True
            tFullDriver.start()
            harvester.fastThreads.append(tFullDriver)
        for tt in harvester.fastThreads:
            tt.join()

        harvester.harvestAllContracts("all")
    elif args.mode == "topup":
        print("Performing topup")
        argsList = []
        harvester.harvestAllContracts("all", argsList, True)
    else:
        print("Invalid argument, please try any of the following")
        print("harvest.py --mode full")
        print("harvest.py --mode topup")
