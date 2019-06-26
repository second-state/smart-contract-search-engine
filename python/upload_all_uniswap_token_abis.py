import re
import json
import time
import requests
from harvest import Harvest
from web3.auto import w3

harvester = Harvest()

# Get the events 
abi = [{"name": "NewExchange", "inputs": [{"type": "address", "name": "token", "indexed": True}, {"type": "address", "name": "exchange", "indexed": True}], "anonymous": False, "type": "event"}]
uniswap = w3.eth.contract('0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95', abi=abi)

events = uniswap.events.NewExchange.createFilter(fromBlock=6627917).get_all_entries()
#abiUrl1 = "https://raw.githubusercontent.com/Uniswap/contracts-vyper/master/abi/uniswap_exchange.json"
abiUrl1 = "https://raw.githubusercontent.com/Uniswap/contracts-vyper/master/abi/uniswap_factory.json"
abiData1 = requests.get(abiUrl1).content
abiData1JSON = json.loads(abiData1)
theDeterministicHash1 = harvester.shaAnAbi(abiData1JSON)
cleanedAndOrderedAbiText1 = harvester.cleanAndConvertAbiToText(abiData1JSON)

i = 0
for e in events:
    # Exchange contract instances
    if e.event == "NewExchange":
        i = i + 1
        if i == 1:
            print("Processing Exchange: " + e.args.exchange)
            print("Tx: " + harvester.web3.toHex(e.transactionHash))
            harvester.processSingleTransaction(json.loads(cleanedAndOrderedAbiText1), str(harvester.web3.toHex(e.transactionHash)))
            tokenAbiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=" + e.args.token + "&format=raw"
            rawTokenAbi = requests.get(tokenAbiUrl).content
            abiData1JSON = json.loads(rawTokenAbi)
            theDeterministicHash = harvester.shaAnAbi(abiData1JSON)
            cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(abiData1JSON)
            data2 = {}
            data2['indexInProgress'] = "false"
            data2['epochOfLastUpdate'] = int(time.time())
            data2['abi'] = cleanedAndOrderedAbiText
            harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash, body=data2)