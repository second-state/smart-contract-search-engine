import re
import json
import time
import requests
from harvest import Harvest
import elasticsearch.helpers
from flask import Flask, jsonify, request

harvester = Harvest()

app = Flask(__name__)


@app.route("/api/describe_using_tx", methods=['GET', 'POST'])
def describe_using_tx():
    jsonRequestData = json.loads(request.data)
    transactionHash = jsonRequestData["hash"]
    rawData = harvester.getDataUsingTransactionHash(transactionHash)
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
        return jsonify(doc)

@app.route("/api/submit_many_abis", methods=['GET', 'POST'])
def submit_many_abis():
    jsonRequestData = json.loads(request.data)
    transactionHash = jsonRequestData["hash"]
    for k, v in jsonRequestData["abis"].items():
        jsonAbiObj = json.loads(json.dumps(v["abi"]))
        theDeterministicHash = harvester.shaAnAbi(jsonAbiObj)
        cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(jsonAbiObj)
        success = False
        try:
            # Try and index the contract instance directly into the common index.
            harvester.processSingleTransaction(json.loads(cleanedAndOrderedAbiText), transactionHash)
            success = True
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
            source = {}
            source["TxHash"] = transactionHash
            harvester.abiCompatabilityUpdate(jsonAbiObj, source)
    doc = {}
    doc["response"] = 'Completed ABI submissions'
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
    return jsonify(result)

@app.route("/api/es_get_abi_count", methods=['GET', 'POST'])
def es_get_abi_count():
    print(request)
    #jsonRequestData = json.loads(request.data)
    results = harvester.getAbiCount()
    return jsonify(results)

@app.route("/api/es_get_all_count", methods=['GET', 'POST'])
def es_get_all_count():
    print(request)
    #jsonRequestData = json.loads(request.data)
    results = harvester.getAllCount()
    return jsonify(results)

@app.route("/api/es_get_contract_count", methods=['GET', 'POST'])
def es_get_contract_count():
    print(request)
    #jsonRequestData = json.loads(request.data)
    results = harvester.getContractCount()
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
        return jsonify(theResponse)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True)
