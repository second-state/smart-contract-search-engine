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

# Official ABI copied verbatim from the ETH Wiki at https://github.com/ethereum/wiki/wiki/Contract-ERC20-ABI
officialAbi = '''[
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": true,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]
'''

#ABI Text
officialAbiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(officialAbi), sort_keys=True))
officialAbiData = re.sub(r"[\s]+", " ", officialAbiData)
#Abi Sha
officialAbiSha = web3.toHex(web3.sha3(text=officialAbiData))
# Abi JSON
officialAbiJSON = json.loads(officialAbiData)
# Abi Functions
keccakHashes = []
for item in officialAbiJSON:
    if item['type'] == 'function':
        if len(item['inputs']) == 0:
            stringToHash = str(item['name'] + '()')
            hashCreated = str(web3.toHex(web3.sha3(text=stringToHash)))[2:10]
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
            hashCreated = str(web3.toHex(web3.sha3(text=stringToHash)))[2:10]
            keccakHashes.append(hashCreated)

print("Keccak Hashes for official ERC20 ABI:")
print(keccakHashes)