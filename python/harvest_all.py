import os
import sys
import json
import boto3
import configparser
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

class Harvest:
    def __init__(self):

        self.scriptExecutionLocation = os.getcwd()
       
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

    def harvestAllContracts(self, esIndex,  _stop=False):
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
                            try:
                                outerData = {}
                                outerData['TxHash'] = str(self.web3.toHex(transactionData.hash))
                                outerData['blockNumber'] = transactionReceipt.blockNumber
                                outerData['contractAddress'] = transactionReceipt.contractAddress

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

if __name__ == "__main__":
    harvester = Harvest()
    harvester.harvest("all")
