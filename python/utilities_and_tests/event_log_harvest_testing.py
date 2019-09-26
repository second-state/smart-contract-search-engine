import re
import json
import time
import requests
from itertools import chain
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
                    for transactionLog in transactionLogs:
                        contractAddress = transactionLog["address"]
                        blockNumber = transactionReceipt["blockNumber"]
                        sentFrom = transactionReceipt["from"]
                        if harvester.hasDataBeenIndexed(harvester.commonIndex, contractAddress) == True:
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
                                            inputList = []
                                            inputTypeList = []
                                            inputNameList = []
                                            indexedInputTypeList = []
                                            indexedInputNameList = []
                                            for input in range(0, len(inputs)):
                                                inputDict = {}
                                                # Set the status of a particular input's index attribute
                                                inputIndexed = False
                                                for inputKey, inputValue in inputs[input].items():
                                                    # Create a list of input key values for the ES index
                                                    inputDict[str(inputKey)] = str(inputValue)
                                                    if str(inputKey) == "indexed":
                                                        if inputValue == False:
                                                            inputIndexed = False
                                                        else:
                                                            if inputValue == True:
                                                                inputIndexed = True
                                                inputList.append(inputDict)
                                                # With the given status, go ahead and create the respective lists of values (indexed vs not indexed)
                                                for inputKey, inputValue in inputs[input].items():
                                                    if str(inputKey) == "name":
                                                        if inputIndexed == False:
                                                            inputNameList.append(str(inputValue))
                                                        elif inputIndexed == True:
                                                            indexedInputNameList.append(str(inputValue))
                                                    if str(inputKey) == "type":
                                                        if inputIndexed == False:
                                                            inputTypeList.append(str(inputValue))
                                                        elif inputIndexed == True:
                                                            indexedInputTypeList.append(str(inputValue))
                                                        if input == len(inputs) - 1:
                                                            selectorText = selectorText + str(inputValue) + ")"
                                                        else:
                                                            selectorText = selectorText + str(inputValue) + ","
                                            # Creating a unique identifier for this event for ES 
                                            selectorHash = "0x" + str(harvester.web3.toHex(harvester.web3.sha3(text=selectorText)))[2:10]
                                            txEventString = str(selectorHash) + str(harvester.web3.toHex(transaction.hash))
                                            txEventKey = str(harvester.web3.toHex(harvester.web3.sha3(text=txEventString)))
                                            if harvester.hasEventBeenIndexed(harvester.eventIndex, txEventKey) != True:
                                                # Calculate the hash to that we can see if the transaction's topic has a match
                                                eventSignature = harvester.web3.toHex(harvester.web3.sha3(text=selectorText))
                                                # Obtain the transaction's topics so we can compare
                                                topics = harvester.web3.toHex(transactionLog['topics'][0])
                                                # Check to see that the topic in this transaction matches the particular ABI event that we are currently iterating over
                                                if topics == eventSignature:
                                                    print(str(name))
                                                    eventDict["txEventKey"] = txEventKey
                                                    eventDict["id"] = str(selectorHash)
                                                    eventDict["name"] = str(name)
                                                    eventDict["contractAddress"] = contractAddress
                                                    eventDict["TxHash"] = str(harvester.web3.toHex(transaction.hash))
                                                    eventDict["blockNumber"] = blockNumber
                                                    eventDict["from"] = sentFrom
                                                    eventDict["inputs"] = inputList
                                                    data = transactionLog.data
                                                    # If all of the event inputs are declared in the smart contract as indexed the data will be 0x
                                                    if data != "0x":
                                                        print("This event has a combination of indexed and non indexed inputs")
                                                        values = eth_abi.decode_abi(inputTypeList, bytes.fromhex(re.split("0x", data)[1]))
                                                        indexedValues = [eth_abi.decode_single(t, v) for t, v in zip(indexedInputTypeList, transactionLog['topics'][1:])]
                                                        eventLogData = dict(chain(zip(inputNameList, values), zip(indexedInputNameList, indexedValues)))
                                                        eventDict["eventLogData"] = eventLogData
                                                    else:
                                                        print(transactionLog['topics'][1:])
                                                        print(indexedInputNameList)
                                                        print(indexedInputTypeList)
                                                        indexedValues = [eth_abi.decode_single(t, v) for t, v in zip(indexedInputTypeList, transactionLog['topics'][1:])]
                                                        eventLogData = dict(zip(indexedInputNameList, indexedValues))
                                                        eventDict["eventLogData"] = eventLogData
                                                print(eventDict)
                            else:
                                print("This contract's ABIs are not known/indexed so we can not read the event names")
                        else:
                            print("We have not idexed this contract and therefore do not have the ABIs")
                else:
                    print("Transaction: " + str(harvester.web3.toHex(transactionHash)) + " has no logs")
        else:
            print("Transaction count is 0")



