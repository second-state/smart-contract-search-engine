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
config.read(os.path.join(scriptExecutionLocation, 'config.ini'))

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

#v1
abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
abiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))
abiData = re.sub(r"[\s]+", " ", abiData)
abiSha = web3.toHex(web3.sha3(text=abiData))
print(abiSha)
print(abiData)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['abi'] = abiData
es.index(index=abiIndex, id=abiSha, body=data)
#v2
abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.abi"
abiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))
abiData = re.sub(r"[\s]+", " ", abiData)
abiSha = web3.toHex(web3.sha3(text=abiData))
print(abiSha)
print(abiData)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['abi'] = abiData
es.index(index=abiIndex, id=abiSha, body=data)

#v1
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCodeSha = web3.toHex(web3.sha3(text=byteCode))
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
es.index(index=bytecodeIndex, id=byteCodeSha, body=data)
#v2
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCodeSha = web3.toHex(web3.sha3(text=byteCode))
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
es.index(index=bytecodeIndex, id=byteCodeSha, body=data)