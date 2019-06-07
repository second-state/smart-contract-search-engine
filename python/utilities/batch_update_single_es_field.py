# This file came about when we wanted to add an additional fields called "quality" to the Elasticsearch index. 
# As you can see, we simply loop through all of the items, create a new field (with a default value of 50) called quality and then update the index.
# This file can be used to create other new fields, you just have to create a doc object like we have done below and then pass that into Elasticsearch at the appropriate ID.

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

# CWD
scriptExecutionLocation = os.getcwd()

# Config
print("Reading configuration file")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(os.path.join(scriptExecutionLocation, '../config.ini'))

# Master index
masterIndex = config['masterindex']['all']
print("Master index: %s" % masterIndex)

# Common index
commonIndex = config['commonindex']['network']
print("Common index: %s" % commonIndex)
    
# Abi index
abiIndex = config['abiindex']['abi']
print("Abi index: %s" % abiIndex)

# Bytecode index
bytecodeIndex = config['bytecodeindex']['bytecode']
print("Bytecode index: %s" % bytecodeIndex)

# Blockchain RPC
blockchainRpc = config['blockchain']['rpc']
print("Blockchain RPC: %s" % blockchainRpc)

# Elasticsearch endpoint
elasticSearchEndpoint = config['elasticSearch']['endpoint']
print("ElasticSearch Endpoint: %s" % elasticSearchEndpoint)

# Elasticsearch AWS region
elasticSearchAwsRegion = config['elasticSearch']['aws_region']

# Web 3 init
web3 = Web3(HTTPProvider(str(blockchainRpc)))

# AWS Boto
auth = BotoAWSRequestsAuth(aws_host=elasticSearchEndpoint, aws_region=elasticSearchAwsRegion, aws_service='es')
es = Elasticsearch(
    hosts=[{'host': elasticSearchEndpoint, 'port': 443}],
    region=elasticSearchAwsRegion,
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

# New data
doc = {}
outerData = {}
outerData["quality"] = "50"
doc["doc"] = outerData
# Match all to access all records
dMatchAllInner = {}
dMatchAll = {}
dMatchAll["match_all"] = dMatchAllInner
dQuery = {}
dQuery["query"] = dMatchAll
# Fetch the items
esReponseByte = elasticsearch.helpers.scan(client=es, index=commonIndex , query=json.dumps(dQuery), preserve_order=True)
# Access each of the item IDs
for i, doc in enumerate(esReponseByte):
	itemId = doc.get('_id')
	print("Updating ID: %s" % itemId)
	# Write the new data from above into the index at the current ID
	reponse = es.update(index=commonIndex, id=itemId, body=json.dumps(doc))


