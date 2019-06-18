
#IMPORTS
import os
import time
import json
import boto3 
import requests
import configparser
import elasticsearch.helpers
from flask import Flask, jsonify, request
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection 

# CONFIG

# CWD
scriptExecutionLocation = os.getcwd()
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(os.path.join(scriptExecutionLocation, 'config.ini'))

host = config['elasticSearch']['endpoint']
print("ElasticSearch Endpoint: %s" % host)

masterIndex = config['masterindex']['all']
print("masterIndex: %s" % masterIndex)

commonIndex = config['commonindex']['network']
print("commonIndex: %s" % commonIndex)

abiIndex = config['abiindex']['abi']
print("abiIndex: %s" % abiIndex)

bytecodeIndex = config['bytecodeindex']['bytecode']
print("bytecodeIndex: %s" % bytecodeIndex)

elasticSearchAwsRegion = config['elasticSearch']['aws_region']

auth = BotoAWSRequestsAuth(aws_host=host, aws_region=elasticSearchAwsRegion, aws_service='es')
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    region=elasticSearchAwsRegion,
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

app = Flask(__name__)


@app.route("/api/submit_abi", methods=['GET', 'POST'])
def submit_abi():
    jsonRequestData = json.loads(request.data)
    ## The users would have visited the upload_abi page which would have displayed all of the contracts without ABIShA3 field. 
    ## The "all" index is the one which has all of the contract addresses we refer to it as the masterIndex
    ## Instantiate a web3 contract instance using the abi and the address provided from the submit_api page
    ## If this passes then create an ES update query like this
    ## The ABI
    ## abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
    ## abiData = re.sub(r"[\n\t\s]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))

    ## Once we have cleaned the ABI we create the hash of it 
    ## abiSha = web3.toHex(web3.sha3(text=json.dumps(abiData)))
    ## Use Elasticsearch to update the record 
    ## data = {}
    ## data['abi'] = abiData
    ## es.index(index="abi", id=abiSha, body=abiData)


@app.route("/api/es_search", methods=['GET', 'POST'])
def es_search():
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=es, index=commonIndex, query=jsonRequestData)
    uniqueDict = {}
    for returnedItem in results:
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                for sKey, sValue in rValue.items():
                    if str(sKey) == "functionDataList":
                        for functionDataListItem in sValue:
                            for fKey, fValue in functionDataListItem.items():
                                if fKey in uniqueDict:
                                    print("We already have " + str(fKey))
                                else:
                                    uniqueDict[fKey] = fValue
                    else:
                        if sKey in uniqueDict:
                            print("We already have " + str(sKey))
                        else:
                            uniqueDict[sKey] = sValue
    print(uniqueDict)
    obj = {}
    num = 1
    for item in uniqueDict:
        obj[str(num)] = item
        num = num+1
    return jsonify(obj)

@app.route("/api/getAll", methods=['GET', 'POST'])
def getAll():
    matchAll = {}
    matchAll["match_all"] = {}
    query = {}
    query["query"] = matchAll
    allQuery = json.loads(json.dumps(query))
    results = elasticsearch.helpers.scan(client=es, index=commonIndex, query=allQuery)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
        num = num+1
    return jsonify(obj)

@app.route("/api/es_update_quality", methods=['GET', 'POST'])
def es_update_quality():
    jsonRequestData = json.loads(request.data)
    itemId = jsonRequestData["contractAddress"]
    qualityScore = jsonRequestData["qualityScore"]
    if int(qualityScore) >= 0 and int(qualityScore) <= 100:
        doc = {}
        outerData = {}
        outerData["quality"] = qualityScore
        doc["doc"] = outerData
        theResponse = es.update(index=commonIndex, id=itemId, body=json.dumps(doc))
        return jsonify(theResponse)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True)
