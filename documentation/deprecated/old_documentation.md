**Please note that there is a convention which must be followed in the configuration.**
Please use index name underscore contract version i.e. `fairlpay_v1` as shown below. For example, do not use double underscores or more than one underscore in the string. If this convention is properly followed, the harvester will automatically create an index called "fairplay" (if it does not already exist) and it will also index all contracts which match the abi and bytecode with a version attribute of "v1".

You can add multiple abi URLs and bytecode URLs, but remember - they are in relation to specific smart contract and as such they need to be appropriately named with the convention.

- Provide one or more links to each specific RAW abi file under the abis section heading
```
[abis]
fairplay_v1 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi
fairplay_v2 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.abi
```
- Provide one or more links to each specific RAW bytecode file under the bytecode section heading
```
[bytecode]
fairplay_v1 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin
fairplay_v2 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.bin
```


Creating a web3 contract instance in the command line for testing

```python
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
# Testnet
blockchainRpc = "https://testnet-rpc.cybermiles.io:8545"
web3 = Web3(HTTPProvider(blockchainRpc))
#transactionData = web3.eth.getTransaction("0x3c1bfa6806800adee8b8e9e60421e54cc3b7a9cf0f41aaabcdb21636efb27f29")

#blockchainRpc = "http://35.161.237.144:8545"



auth = BotoAWSRequestsAuth(aws_host="search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com", aws_region="ap-southeast-2", aws_service='es')
es = Elasticsearch(
    hosts=[{'host': "search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com", 'port': 443}],
    region="ap-southeast-2",
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)
```


This is how we create the abi record in the abi index

```python
abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
abiData = re.sub(r"[\n\t\s]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))
abiSha = web3.toHex(web3.sha3(text=json.dumps(abiData)))
data = {}
data['abi'] = abiData
es.index(index="abi", id=abiSha, body=data)
```

This is now we create the bytecode record in the bytecode index
```python
# This must be the raw URL (raw.githubusercontent.com...) not just the GitHub URL
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCodeSha = web3.toHex(web3.sha3(text=byteCode))
data = {}
data['bytecode'] = byteCode
es.index(index="bytecode", id=byteCodeSha, body=data)
```
