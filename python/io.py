import re
import json
import time
import math
import requests
from harvest import Harvest
import elasticsearch.helpers
from flask import Flask, jsonify, request

harvester = Harvest()

app = Flask(__name__)

def logApi(_request):
    data = {}
    timestamp = math.floor(time.time())
    data["timestamp"] = timestamp
    callingIp = _request.headers.get('X-Forwarded-For', request.remote_addr)
    data["callingIp"] = callingIp
    endpoint = _request.endpoint
    data["endpoint"] = endpoint
    harvester.processApiAccessLog(data)

@app.route("/api/get_block_interval", methods=['GET', 'POST'])
def get_block_interval():
    blockInterval = harvester.getBlockInterval()
    logApi(request)
    return jsonify(blockInterval)

@app.route("/api/confirm_deployment", methods=['GET', 'POST'])
def confirm_deployment():
    print(request)
    jsonRequestData = json.loads(request.data)
    transactionHash = jsonRequestData["hash"]
    returnValue = harvester.confirmDeployment(transactionHash)
    doc = {}
    doc["response"] = str(returnValue)
    logApi(request)
    return jsonify(doc)

@app.route("/api/update_state_of_contract_address", methods=['GET', 'POST'])
def update_state_of_contract_address():
    jsonRequestData = json.loads(request.data)
    if jsonRequestData["abi"] == "all":
        abi = "all"
    else:
        abi = json.loads(jsonRequestData["abi"])
    address = jsonRequestData["address"]
    try:
        result = harvester.updateStateOfContractAddress(abi, address)
        doc = {}
        if result == True:
            doc["response"] = 'true'
        elif result == False:
            doc["response"] = 'false'
        logApi(request)
        return jsonify(doc)
    except:
        doc = {}
        doc["response"] = 'false'
        return jsonify(doc)

@app.route("/api/express_harvest_an_abi", methods=['GET', 'POST'])
def express_harvest_an_abi():
    #print(request)
    jsonRequestData = json.loads(request.data)
    abiHash = jsonRequestData["abiHash"]
    blockFloor = jsonRequestData["blockFloor"]
    try:
        result = harvester.expressHarvestAnAbi(abiHash, blockFloor)
        doc = {}
        if result == True:
            doc["response"] = 'true'
        elif result == False:
            doc["response"] = 'false'
        logApi(request)
        return jsonify(doc)
    except:
        doc = {}
        doc["response"] = 'false'
        return jsonify(doc)


@app.route("/api/most_recent_indexed_block_number", methods=['GET', 'POST'])
def most_recent_indexed_block_number():
    mostRecentIndexedBlockNumber = harvester.mostRecentIndexedBlockNumber()
    logApi(request)
    return jsonify(mostRecentIndexedBlockNumber)

@app.route("/api/describe_using_tx", methods=['GET', 'POST'])
def describe_using_tx():
    jsonRequestData = json.loads(request.data)
    transactionHash = jsonRequestData["hash"]
    rawData = harvester.getDataUsingTransactionHash(transactionHash)
    logApi(request)
    return jsonify(rawData)

@app.route("/api/describe_using_address", methods=['GET', 'POST'])
def describe_using_address():
    jsonRequestData = json.loads(request.data)
    address = jsonRequestData["address"]
    rawData = harvester.getDataUsingAddressHash(address)
    logApi(request)
    return jsonify(rawData)

@app.route("/api/submit_abi", methods=['GET', 'POST'])
def submit_abi():
    jsonRequestData = json.loads(request.data)
    jsonAbiObj = json.loads(jsonRequestData["abi"])
    theDeterministicHash = harvester.shaAnAbi(jsonAbiObj)
    cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(jsonAbiObj)
    transactionHash = jsonRequestData["hash"]
    success = False
    try:
        # Try and index the contract instance directly into the common index
        harvester.processSingleTransaction(json.loads(cleanedAndOrderedAbiText), transactionHash)
        success = True
    except:
        print("Unable to process that single transaction")
        doc = {}
        doc["response"] = 'Failed to index contract'
        return jsonify(doc)
    # If that succeded then it is safe to go ahead and permanently store the ABI in the abi index
    if success == True:
        data = {}
        data['indexInProgress'] = "false"
        data['epochOfLastUpdate'] = int(time.time())
        data['abi'] = cleanedAndOrderedAbiText
        harvester.loadDataIntoElastic(harvester.abiIndex, theDeterministicHash, data)
        print("Index was a success")
        doc = {}
        doc["response"] = 'Successfully indexed contract.'
        logApi(request)
        return jsonify(doc)

@app.route("/api/submit_many_abis", methods=['GET', 'POST'])
def submit_many_abis():
    jsonRequestData = json.loads(request.data)
    transactionHash = jsonRequestData["hash"]
    firstPass = True
    for k, v in jsonRequestData["abis"].items():
        jsonAbiObj = json.loads(json.dumps(v["abi"]))
        theDeterministicHash = harvester.shaAnAbi(jsonAbiObj)
        cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(jsonAbiObj)
        success = False
        if success == False:
            try:
                # Try and index the contract instance directly into the common index.
                harvester.processSingleTransaction(json.loads(cleanedAndOrderedAbiText), transactionHash)
                success = True
                if firstPass == True:
                    # Allow Elasticsearch to respond
                    time.sleep(2)
                    firstPass = False
                print("Indexing of single transaction was a success")
            except:
                print("Unable to process that single transaction")
        # If that succeded then it is safe to go ahead and permanently store the ABI in the abi index
        if success == True:
            # Adding this current ABI to the ABI index
            data = {}
            data['indexInProgress'] = "false"
            data['epochOfLastUpdate'] = int(time.time())
            data['abi'] = cleanedAndOrderedAbiText
            harvester.loadDataIntoElastic(harvester.abiIndex, theDeterministicHash, data)
            print("Index ABI was a success")
            # Adding this current ABI to the abiShaList of the transaction which has already been indexed using one of its other ABIs
            time.sleep(1)
            source = harvester.getDataUsingTransactionHash(transactionHash)
            print(source)
            sourceDataObject = json.loads(json.dumps(source))
            harvester.abiCompatabilityUpdate(jsonAbiObj, source["hits"]["hits"][0]["_source"])
    doc = {}
    doc["response"] = 'Completed ABI submissions'
    logApi(request)
    return jsonify(doc)

@app.route("/api/sha_an_abi", methods=['GET', 'POST'])
def sha_an_abi():
    print(request)
    jsonRequestData = json.loads(request.data)
    abi = json.loads(jsonRequestData["abi"])
    abiHash = harvester.shaAnAbi(abi)
    result = {}
    result["abiSha3"] = abiHash
    print(result)
    logApi(request)
    return jsonify(result)

@app.route("/api/sort_an_abi", methods=['GET', 'POST'])
def sort_an_abi():
    print(request)
    jsonRequestData = json.loads(request.data)
    abi = json.loads(jsonRequestData["abi"])
    abiHash = harvester.cleanAndConvertAbiToText(abi)
    result = {}
    result["abiSorted"] = abiHash
    print(result)
    logApi(request)
    return jsonify(result)

@app.route("/api/es_get_abi_count", methods=['GET', 'POST'])
def es_get_abi_count():
    print("Checking API usage limits")
    # Allowed 10 hits per 60 seconds for that IP
    if harvester.withinApiRequestsLimit(10, 60, request.headers.get('X-Forwarded-For', request.remote_addr)) == True:
        results = harvester.getAbiCount()
        logApi(request)
        return jsonify(results)
    else:
        print("Please wait ... exceeded API limits")

@app.route("/api/es_get_all_count", methods=['GET', 'POST'])
def es_get_all_count():
    print(request)
    #jsonRequestData = json.loads(request.data)
    results = harvester.getAllCount()
    logApi(request)
    return jsonify(results)

@app.route("/api/es_get_contract_count", methods=['GET', 'POST'])
def es_get_contract_count():
    print(request)
    #jsonRequestData = json.loads(request.data)
    results = harvester.getContractCount()
    logApi(request)
    return jsonify(results)

@app.route("/api/es_quick_100_search", methods=['GET', 'POST'])
def es_quick_100_search():
    print(request)
    jsonRequestData = json.loads(request.data)
    results = harvester.getOnly100Records()
    outerList = []
    print(results)
    for returnedItem in results["hits"]["hits"]:
        uniqueDict = {}
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                for sKey, sValue in rValue.items():
                    if str(sKey) == "functionDataList":
                        for functionDataListItem in sValue['0']:
                            for fKey, fValue in functionDataListItem.items():
                                if fKey in uniqueDict:
                                    #print("We already have " + str(fKey))
                                    print(".")
                                else:
                                    uniqueDict[fKey] = fValue
                    else:
                        if sKey in uniqueDict:
                            #print("We already have " + str(sKey))
                            print(".")
                        else:
                            uniqueDict[sKey] = sValue
        outerList.append(uniqueDict)
    resultsDict = {}
    resultsDict["results"] = outerList
    #print(resultsDict)
    logApi(request)
    return jsonify(resultsDict["results"])

@app.route("/api/es_search", methods=['GET', 'POST'])
def es_search():
    print(request)
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=harvester.es, index=harvester.commonIndex, query=jsonRequestData)
    outerList = []
    for returnedItem in results:
        uniqueDict = {}
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                for sKey, sValue in rValue.items():
                    if str(sKey) == "functionDataList":
                        for functionDataListItem in sValue['0']:
                            for fKey, fValue in functionDataListItem.items():
                                if fKey in uniqueDict:
                                    #print("We already have " + str(fKey))
                                    print(".")
                                else:
                                    uniqueDict[fKey] = fValue
                    else:
                        if sKey in uniqueDict:
                            #print("We already have " + str(sKey))
                            print(".")
                        else:
                            uniqueDict[sKey] = sValue
        outerList.append(uniqueDict)
    resultsDict = {}
    resultsDict["results"] = outerList
    #print(resultsDict)
    logApi(request)
    return jsonify(resultsDict["results"])

@app.route("/api/es_event_search", methods=['GET', 'POST'])
def es_event_search():
    print(request)
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=harvester.es, index=harvester.eventIndex, query=jsonRequestData)
    outerList = []
    for returnedItem in results:
        uniqueDict = {}
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                uniqueDict["_source"] = rValue
                outerList.append(uniqueDict)
    resultsDict = {}
    resultsDict["results"] = outerList
    #print(resultsDict)
    logApi(request)
    return jsonify(resultsDict["results"])

@app.route("/api/es_tx_search", methods=['GET', 'POST'])
def es_tx_search():
    print(request)
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=harvester.es, index=harvester.activityIndex, query=jsonRequestData)
    outerList = []
    for returnedItem in results:
        uniqueDict = {}
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                uniqueDict["_source"] = rValue
                outerList.append(uniqueDict)
    resultsDict = {}
    resultsDict["results"] = outerList
    #print(resultsDict)
    logApi(request)
    return jsonify(resultsDict["results"])

@app.route("/api/es_access_search", methods=['GET', 'POST'])
def es_access_search():
    print(request)
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=harvester.es, index=harvester.logAnalyticsIndex, query=jsonRequestData)
    outerList = []
    for returnedItem in results:
        uniqueDict = {}
        for rKey, rValue in returnedItem.items():
            if str(rKey) == "_source":
                uniqueDict["_source"] = rValue
                outerList.append(uniqueDict)
    resultsDict = {}
    resultsDict["results"] = outerList
    #print(resultsDict)
    logApi(request)
    return jsonify(resultsDict["results"])


@app.route("/api/getAll", methods=['GET', 'POST'])
def getAll():
    matchAll = {}
    matchAll["match_all"] = {}
    query = {}
    query["query"] = matchAll
    allQuery = json.loads(json.dumps(query))
    results = elasticsearch.helpers.scan(client=harvester.es, index=harvester.commonIndex, query=allQuery)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
        num = num+1
    logApi(request)
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
        theResponse = harvester.es.update(index=harvester.commonIndex, id=itemId, body=json.dumps(doc))
        logApi(request)
        return jsonify(theResponse)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True)
