import os
import json
import boto3 
import requests
import configparser
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

class Harvest:
    def __init__(self):

        # CWD
        self.scriptExecutionLocation = os.getcwd()

        # Config
        print("Reading configuration file")
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(os.path.join(self.scriptExecutionLocation, 'config.ini'))

        # ABI (single abi)
        self.fairPlayAbi = config['abis']['fair_play_v_one']
        print("FairPlay ABI: %s" % self.fairPlayAbi)

        self.contractAbiFileData = requests.get(self.fairPlayAbi)
        print("ABI file data")
        print(self.contractAbiFileData)

        self.contractAbiJSONData = json.loads(self.contractAbiFileData.content)
        print("ABI JSON data")
        print(self.contractAbiJSONData)

        # ABI[s] possible future use, if storing abis in the configuration (for now use single abi option above)
        self.abis = {}
        for key in config['abis']:
            stringKey = str(key)
            self.abis[stringKey] = config['abis'][key]
        print("\nABIs:")
        for (ufaKey, ufaValue) in self.abis.items():
            print(ufaKey + ": " + ufaValue)
        # Blockchain RPC
        self.blockchainRpc = config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)

        # Elasticsearch index
        self.elasticSearchIndex = config['elasticSearch']['index']
        print("ElasticSearch Index: %s" % self.elasticSearchIndex)

        # Elasticsearch endpoint
        self.elasticSearchEndpoint = config['elasticSearch']['endpoint']
        print("ElasticSearch Endpoint: %s" % self.elasticSearchEndpoint)

        # Elasticsearch AWS region
        self.elasticSearchAwsRegion = config['elasticSearch']['aws_region']

        # Web 3 init
        web3 = Web3(HTTPProvider(self.blockchainRpc))

        # AWS Boto
        auth = BotoAWSRequestsAuth(aws_host=self.elasticSearchEndpoint, aws_region=self.elasticSearchAwsRegion, aws_service='es')
        es = Elasticsearch(
            hosts=[{'host': self.elasticSearchEndpoint, 'port': 443}],
            region=self.elasticSearchAwsRegion,
            use_ssl=True,
            verify_certs=True,
            http_auth=auth,
            connection_class=RequestsHttpConnection
        )

        ############################################
        # Functions
    def createUniqueAbiComparisons(self):
        keccakHashes = []
        for item in self.contractAbiJSONData:
            if item['type'] == 'function':
                if len(item['inputs']) == 0:
                    stringToHash = str(item['name'] + '()')
                    print("String to be hashed: %s" % stringToHash)
                    hashCreated = str(web3.toHex(web3.sha3(text=stringToHash)))[2:10]
                    print("Hash: %s" + hashCreated)
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
                    hashCreated = str(web3.toHex(web3.sha3(text=stringToHash)))[2:10]
                    print("Hash: %s" + hashCreated)
                    keccakHashes.append(hashCreated)
        return keccakHashes



# Driver - Start
harvester = Harvest()

# TEST functions
harvester.createUniqueAbiComparisons()

