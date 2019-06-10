import os
import re
import time
import json
import argparse
import requests
import configparser
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

# CWD
scriptExecutionLocation = os.getcwd()

# Config
print("Reading configuration file")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(os.path.join(scriptExecutionLocation, '../config.ini'))

abiIndex = config['abiindex']['abi']
print("Abi index: %s" % abiIndex)

# Bytecode index
bytecodeIndex = config['bytecodeindex']['bytecode']
print("Bytecode index: %s" % bytecodeIndex)

# Elasticsearch endpoint
elasticSearchEndpoint = config['elasticSearch']['endpoint']
print("ElasticSearch Endpoint: %s" % elasticSearchEndpoint)

# Elasticsearch AWS region
elasticSearchAwsRegion = config['elasticSearch']['aws_region']

auth = BotoAWSRequestsAuth(aws_host=elasticSearchEndpoint, aws_region=elasticSearchAwsRegion, aws_service='es')
es = Elasticsearch(
    hosts=[{'host': elasticSearchEndpoint, 'port': 443}],
    region=elasticSearchAwsRegion,
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

blockchainRpc = config['blockchain']['rpc']

web3 = Web3(HTTPProvider(str(blockchainRpc)))

# This is an example of a blank name which is present in Maker contract ABI
#{'constant': True, 'inputs': [], 'name': 'owner', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}

# The above ABI entry causes the following error
# web3.exceptions.BadFunctionCallOutput: Could not decode contract function call name return data b'' for output_types ['bytes32']


def fetchPureViewFunctionData(_theContractInstance):
    callableFunctions = []
    for item in _theContractInstance.abi:
        if item['type'] == 'function':
            if len(item['inputs']) == 0:
                if len(item['outputs']) > 0:
                    callableFunctions.append(str(item['name']))
    theFunctionData = {}
    print(_theContractInstance.functions.name().call(block_identifier=4620854))
    # for callableFunction in callableFunctions:
    #     contract_func = _theContractInstance.functions[str(callableFunction)]
    #     result = contract_func().call()
    #     if type(result) is list:
    #         if len(result) > 0:
    #             innerData = {}
    #             for i in range(len(result)):
    #                 innerData[i] = result[i]
    #             theFunctionData[str(callableFunction)] = innerData
    #     else:
    #         theFunctionData[str(callableFunction)] = result

abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2&format=raw"
abiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(requests.get(abiUrl).content), sort_keys=True))
abiData = re.sub(r"[\s]+", " ", abiData)
makerAbi = json.loads(abiData)
txReceipt = web3.eth.getTransactionReceipt("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
tx = web3.eth.getTransaction("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
makerInstance = web3.eth.contract(abi=makerAbi, address=txReceipt.contractAddress)
functionData = fetchPureViewFunctionData(makerInstance)

