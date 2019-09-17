import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()
latestBlockNumber = harvester.web3.eth.getBlock('latest').number
for b in range(latestBlockNumber - 1, latestBlockNumber):
    print("\n")
    transactionCount = harvester.web3.eth.getBlockTransactionCount(b)
    if(transactionCount >= 1):
        print("Transaction count is " + str(transactionCount))
        for singleTransactionInt in range(0, transactionCount):
            print("\n")
            print("Processing transaction " + str(singleTransactionInt)+ " of block " + str(b))
            transaction = harvester.web3.eth.getTransactionByBlock(b, singleTransactionInt)
            transactionHash = transaction.hash
            transactionReceipt = harvester.web3.eth.getTransactionReceipt(transaction.hash)
            transactionLogs = transactionReceipt.logs
            if (len(transactionLogs) >= 1):
                print("Block " + str(b) + "\'s transaction log[s] are below.")
                print(transactionLogs)
            else:
                print("Block " + str(b) + "has no logs")
    else:
        print("Transaction count is 0")