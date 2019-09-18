import re
import json
import time
import requests
from harvest import Harvest


harvester = Harvest()
latestBlockNumber = harvester.web3.eth.getBlock('latest').number

# Iterate through the individual blocks looking for a transaction which involves event log emit
for b in range(latestBlockNumber - 1, latestBlockNumber):
    transactionCount = harvester.web3.eth.getBlockTransactionCount(b)
    if(transactionCount >= 1):
        for singleTransactionInt in range(0, transactionCount):
            transaction = harvester.web3.eth.getTransactionByBlock(b, singleTransactionInt)
            transactionHash = transaction.hash
            transactionReceipt = harvester.web3.eth.getTransactionReceipt(transaction.hash)
            transactionLogs = transactionReceipt.logs
            if (len(transactionLogs) >= 1):
                contractAddress = transactionReceipt.logs[0]["address"]
                blockNumber = transactionReceipt["blockNumber"]
                sentFrom = transactionReceipt["from"]
                # Get list of ABIs from the abiShaList at this point
                ## Perhaps get a distinct list of events from all of the abis 
                ## distinctEventList = []
                # for abiComponents in abiShaList:
                #     isEvent = False
                #     name = ""
                #     inputs = []
                #     for key, value in abiComponents.items():
                #         if key == "inputs":
                #             inputs = value
                #         if key == "name":
                #             name = value
                #         if key == "type":
                #             if value == "event":
                #                 isEvent = True
                #     if isEvent is True and name is not "":
                #         print("\nEvent Log Name:" + name)
                #         print("Inputs:")
                #         ## Make sure that this goes into the distinctEventList if it is not there already
                #         inputCounter = 1
                #         for input in inputs:
                #             print("\t" + "Input" + str(inputCounter))
                #             for inputKey, inputValue in input.items():
                #                 print("\t\t" + str(inputKey) + ":" + str(inputValue))
                #             inputCounter = inputCounter + 1
            else:
                print("Transaction: " + str(harvester.web3.toHex(transactionHash)) + " has no logs")
        print("\n")
    else:
        print("Transaction count is 0")

# TODO
# hasDataBeenIndexed(_eventLogaIndex, _esId)
# fetchAbiUsingHash(_abiHash)

