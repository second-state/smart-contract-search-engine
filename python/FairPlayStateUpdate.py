#IMPORTS
import json
import boto3 # pip3 install boto3
import requests
import elasticsearch.helpers
from web3 import Web3, HTTPProvider
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth # pip3 install aws_requests_auth
from elasticsearch import Elasticsearch, RequestsHttpConnection # pip3 install elasticsearch 


# CONFIG
web3 = Web3(HTTPProvider('https://testnet-rpc.cybermiles.io:8545'))
host = 'search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com'
auth = BotoAWSRequestsAuth(aws_host='search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com', aws_region='ap-southeast-2', aws_service='es')
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    region='ap-southeast-2',
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

def fetchAbi():
    contractAbiFileLocation = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/dapp/FairPlay.abi"
    contractAbiFileData = requests.get(contractAbiFileLocation)
    contractAbiJSONData = json.loads(contractAbiFileData.content)
    return contractAbiJSONData

Abi = fetchAbi()


def fetchContractAddresses():
    dQuery = {}
    dWildCard = {}
    dContractAddress = {}
    lContractAddress = []
    dContractAddress["contractAddress"] = "0x*"
    dWildCard["wildcard"] = dContractAddress
    lContractAddress.append("contractAddress")
    dQuery["query"] = dWildCard
    dQuery["_source"] = lContractAddress
    esReponseAddresses = elasticsearch.helpers.scan(client=es, index="fairplay", query=json.dumps(dQuery), preserve_order=True)
    uniqueList = []
    for i, doc in enumerate(esReponseAddresses):
        source = doc.get('_source')
        if source['contractAddress'] not in uniqueList:
            uniqueList.append(source['contractAddress'])
    return uniqueList

def fetchFunctionDataIds():
    dQuery = {}
    dWildCard = {}
    dFunctionDataId = {}
    lFunctionId = []
    dFunctionDataId["functionDataId"] = "0x*"
    dWildCard["wildcard"] = dFunctionDataId
    lFunctionId.append("functionDataId")
    dQuery["query"] = dWildCard
    dQuery["_source"] = lFunctionId
    esReponseIds = elasticsearch.helpers.scan(client=es, index="fairplay", query=json.dumps(dQuery), preserve_order=True)
    uniqueList = []
    for i, doc in enumerate(esReponseIds):
        source = doc.get('_source')
        if source['functionDataId'] not in uniqueList:
            uniqueList.append(source['functionDataId'])
    return uniqueList
    

def getPureOrViewFunctionNames():
    pureOrViewFunctions = []
    
    for item in Abi:
        if item['type'] == 'function':
            if len(item['inputs']) == 0:
                if len(item['outputs']) > 0:
                    pureOrViewFunctions.append(str(item['name']))
    return pureOrViewFunctions

def fetchPureViewFunctionData(theContractInstance):
# Contract pure and view functions
    callableFunctions = getPureOrViewFunctionNames()
    theFunctionData = {}
    for callableFunction in callableFunctions:
        contract_func = theContractInstance.functions[str(callableFunction)]
        result = contract_func().call()
        if type(result) is list:
            if len(result) > 0:
                innerData = {}
                for i in range(len(result)):
                    innerData[i] = result[i]
                theFunctionData[str(callableFunction)] = innerData
        else:
            theFunctionData[str(callableFunction)] = result
    return theFunctionData

def getFunctionDataId(theFunctionData):
    theId = str(web3.toHex(web3.sha3(text=json.dumps(theFunctionData))))
    return theId

def updateDataInElastic(theContractName, theId, thePayLoad):
    esReponseD = es.update(index=theContractName, id=theId, body=thePayLoad)
    print("\n %s \n" % thePayLoad)
    return esReponseD

Abi = fetchAbi()

uniqueContractList = fetchContractAddresses()

uniqueFunctionIds = fetchFunctionDataIds()
for ifi in uniqueFunctionIds:
    print(ifi)

contractInstanceList = []
for uniqueContracAddress in uniqueContractList:
    #print("Processing: %s " % uniqueContracAddress)
    contractInstance = web3.eth.contract(abi=Abi, address=uniqueContracAddress)
    contractInstanceList.append(contractInstance)
    #print("Added contract to list")

# These happen about once every second, we can make this faster by spawning a check per contract #TODO

for uniqueContractInstance in contractInstanceList:
    freshFunctionData = fetchPureViewFunctionData(uniqueContractInstance)
    functionDataId = getFunctionDataId(freshFunctionData)
    if functionDataId in uniqueFunctionIds:
        print("No change to %s " % functionDataId)
    else:
        print("Hash not found, we must now update this contract instance state")
        itemId = str(web3.toHex(web3.sha3(text=uniqueContractInstance.address)))
        doc = {}
        outerData = {}
        outerData["functionData"] = freshFunctionData
        outerData["functionDataId"] = functionDataId
        doc["doc"] = outerData
        #print(json.dumps(doc))
        indexResult = updateDataInElastic("fairplay", itemId, json.dumps(doc))
        


