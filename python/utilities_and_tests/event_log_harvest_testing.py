import re
import json
import time
import requests
from harvest import Harvest


harvester = Harvest()
latestBlockNumber = harvester.web3.eth.getBlock('latest').number

# Iterate through the individual blocks looking for a transaction which involves event log emit
# TESTING SINGLE EVENT AT BLOCK 6328976
#for b in range(latestBlockNumber - 1, latestBlockNumber):8485195  6328976
transactionCount = harvester.web3.eth.getBlockTransactionCount(6328976)
if(transactionCount >= 1):
    for singleTransactionInt in range(0, transactionCount):
        # transaction = harvester.web3.eth.getTransactionByBlock(b, singleTransactionInt)
        transaction = harvester.web3.eth.getTransactionByBlock(6328976, singleTransactionInt)
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
                            for input in range(0, len(inputs)):
                                for inputKey, inputValue in inputs[input].items():
                                    inputDict[str(inputKey)] = str(inputValue)
                                    # Specifically build the selector string if the input key is type
                                    if str(inputKey) == "type":
                                        if input == len(inputs) - 1:
                                            selectorText = selectorText + str(inputValue) + ")"
                                        else:
                                            selectorText = selectorText + str(inputValue) + ","
                                    # Perform all other operations including if the input key is type
                                    # 
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
                                #contractInstance = harvester.web3.eth.contract(abi=jsonAbi, address=harvester.web3.toChecksumAddress(contractAddress))
                                #eventLogDataObject = contractInstance.eventFilter(str(name), {"filter": {"_from": sentFrom}})
                                print(jsonAbi)
                                print(contractAddress)
                                print(blockNumber)
                                print(sentFrom)
            else:
                print("This contract's ABIs are not known/indexed so we can not read the event names")
        else:
            print("Transaction: " + str(harvester.web3.toHex(transactionHash)) + " has no logs")
else:
    print("Transaction count is 0")

# TODO
# use the selectorHash to create the distinct list (of selector hashes) per contract address (summary of all of the ABIs)
# once you have the distinct list then see if the data has beein indexed as yet (in relation to that specific transaction hash)
# hasDataBeenIndexed(_eventLogIndex, _esId)
# create an ES item for the _eventLogIndex which has an id of harvester.web3.toHex(transaction.hash)
# Index the event as an eventDict object and see how the data looks i.e. if you do a GET request on the _eventLogIndex how many fields will there be. 
# Remember that we would prefer to have the fields inside a list called [0] etc. otherwise we will run out of allowable number of ES index fields



