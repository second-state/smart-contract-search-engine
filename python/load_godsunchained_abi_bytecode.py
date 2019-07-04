import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()


abiUrl1 = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x6EbeAf8e8E946F0716E6533A6f2cefc83f60e8Ab&format=raw"
abiData1 = requests.get(abiUrl1).content
abiData1JSON = json.loads(abiData1)
theDeterministicHash1 = harvester.shaAnAbi(abiData1JSON)
cleanedAndOrderedAbiText1 = harvester.cleanAndConvertAbiToText(abiData1JSON)


data1 = {}
data1['indexInProgress'] = "false"
data1['epochOfLastUpdate'] = int(time.time())
data1['abi'] = cleanedAndOrderedAbiText1
harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash1, body=data1)

