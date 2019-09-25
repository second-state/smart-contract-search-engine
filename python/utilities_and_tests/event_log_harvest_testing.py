import re
import json
import time
import requests
from harvest import Harvest

# import functools
# from web3.contract import get_event_data

harvester = Harvest()
latestBlockNumber = harvester.web3.eth.getBlock('latest').number

# Iterate through the individual blocks looking for a transaction which involves event log emit
# TESTING SINGLE EVENT AT BLOCK 6328976
while True:
    latestBlockNumber = harvester.web3.eth.getBlock('latest').number
    for b in range(latestBlockNumber - 10, latestBlockNumber):
        transactionCount = harvester.web3.eth.getBlockTransactionCount(b)
        #transactionCount = harvester.web3.eth.getBlockTransactionCount(6509882)
        if(transactionCount >= 1):
            for singleTransactionInt in range(0, transactionCount):
                transaction = harvester.web3.eth.getTransactionByBlock(b, singleTransactionInt)
                # transaction = harvester.web3.eth.getTransactionByBlock(6509882, singleTransactionInt)
                transactionHash = transaction.hash
                # Check to see if this TxHash is indexed 
                transactionReceipt = harvester.web3.eth.getTransactionReceipt(transaction.hash)
                transactionLogs = transactionReceipt.logs
                if (len(transactionLogs) >= 1):
                    contractAddress = transactionReceipt.logs[0]["address"]
                    blockNumber = transactionReceipt["blockNumber"]
                    sentFrom = transactionReceipt["from"]
                    listOfAbis = harvester.fetchAbiShaList(contractAddress)
                    if listOfAbis["hits"]["total"] > 0:
                        for item in listOfAbis["hits"]["hits"][0]["_source"]["abiShaList"]:
                            jsonAbi = json.loads(harvester.fetchAbiUsingHash(str(item)))
                            for abiComponents in jsonAbi:
                                isEvent = False
                                name = ""
                                inputs = []
                                for key, value in abiComponents.items():
                                    if key == "inputs":
                                        inputs = value
                                    if key == "name":
                                        name = value
                                    if key == "type":
                                        if value == "event":
                                            isEvent = True
                                if isEvent is True and name is not "":
                                    eventDict = {}
                                    # Create a selector hash
                                    selectorText = str(name) + "("
                                    inputDict = {}
                                    inputTypeList = []
                                    inputNameList = []
                                    for input in range(0, len(inputs)):
                                        for inputKey, inputValue in inputs[input].items():
                                            inputDict[str(inputKey)] = str(inputValue)
                                            # Specifically build the selector string if the input key is type
                                            if str(inputKey) == "name":
                                                inputNameList.append(str(inputValue))
                                            if str(inputKey) == "type":
                                                inputTypeList.append(str(inputValue))
                                                if input == len(inputs) - 1:
                                                    selectorText = selectorText + str(inputValue) + ")"
                                                else:
                                                    selectorText = selectorText + str(inputValue) + ","
                                    selectorHash = "0x" + str(harvester.web3.toHex(harvester.web3.sha3(text=selectorText)))[2:10]
                                    txEventString = str(selectorHash) + str(harvester.web3.toHex(transaction.hash))
                                    txEventKey = str(harvester.web3.toHex(harvester.web3.sha3(text=txEventString)))
                                    if harvester.hasEventBeenIndexed(harvester.eventIndex, txEventKey) != True:
                                        eventDict["txEventKey"] = txEventKey
                                        eventDict["id"] = str(selectorHash)
                                        eventDict["name"] = str(name)
                                        eventDict["contractAddress"] = contractAddress
                                        eventDict["TxHash"] = str(harvester.web3.toHex(transaction.hash))
                                        eventDict["blockNumber"] = blockNumber
                                        eventDict["from"] = sentFrom
                                        eventDict["inputs"] = inputDict
                                        # print("Transaction receipt:")
                                        print(transactionReceipt)
                                        # print("Topics:")
                                        topics = transactionReceipt.logs[0].topics
                                        # print(topics)
                                        # print("Data:")
                                        data = transactionReceipt.logs[0].data
                                        print(data)
                                        # print("Event signature")
                                        eventSignature = harvester.web3.toHex(harvester.web3.sha3(text=selectorText))
                                        # print(eventSignature)
                                        # print("Input type list")
                                        # print(inputTypeList)
                                        if data != "0x":
                                            print("Event Log Values")
                                            values = eth_abi.decode_abi(inputTypeList, bytes.fromhex(re.split("0x", data)[1]))
                                            print(values)
                                        #     eventLogDataDict = dict(zip(inputNameList, values))
                                        #     print(eventLogDataDict)
                                        # else:
                                        #     print("Indexed Log Values")
                                        #contractInstance = harvester.web3.eth.contract(abi=jsonAbi, address=harvester.web3.toChecksumAddress(contractAddress)) 
                                        #logs = contractInstance.events.EventOne().processReceipt(transactionReceipt)
                                        # event_filter = harvester.web3.eth.filter({'topics': [event_signature_transfer]})
                                        # transfer_events = harvester.web3.eth.getFilterChanges(event_filter.filter_id)
                                        # print(transfer_events)
                                        # a = functools.partial(get_event_data, jsonAbi)
                                        # print(a)
                                        # loggy = harvester.web3.eth.getLogs({'fromBlock': blockNumber, 'toBlock': blockNumber, 'address': contractAddress})
                                        # print(loggy)
                                        #contractInstance = harvester.web3.eth.contract(abi=jsonAbi, address=harvester.web3.toChecksumAddress(contractAddress))
                                        #myfilter_new=contractInstance.events.EventOne.createFilter(fromBlock=blockNumber, toBlock=blockNumber)
                                        #print(myfilter_new)
                                        #entries = myfilter_new.get_all_entries()
                                        #print(entries)
                                        #print(selectorHash)
                                        #event_filter = harvester.web3.eth.filter({"address": contractAddress, "topics": [event_signature_hash]})
                                        #print(event_filter)
                                        #eventLogDataObject = contractInstance.eventFilter(str(name), {"filter": {"_from": sentFrom}})
                                        # print(jsonAbi)
                                        # print(contractAddress)
                                        # print(blockNumber)
                                        #print(sentFrom)
                    else:
                        print("This contract's ABIs are not known/indexed so we can not read the event names")
                else:
                    print("Transaction: " + str(harvester.web3.toHex(transactionHash)) + " has no logs")
        else:
            print("Transaction count is 0")



