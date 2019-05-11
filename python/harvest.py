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

        # FUNCTIONS
        def fetchAbi():
            contractAbiFileLocation = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
            contractAbiFileData = requests.get(contractAbiFileLocation)
            contractAbiJSONData = json.loads(contractAbiFileData.content)
            return contractAbiJSONData
        Abi = fetchAbi()


# Driver - Start
harvester = Harvest()

