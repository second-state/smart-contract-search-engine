import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

#BAT ABI
abiUrl1 = "https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/erc20abi.txt"
abiData1 = requests.get(abiUrl1).content
abiData1JSON = json.loads(abiData1)
theDeterministicHash1 = harvester.shaAnAbi(abiData1JSON)
cleanedAndOrderedAbiText1 = harvester.cleanAndConvertAbiToText(abiData1JSON)


data1 = {}
data1['indexInProgress'] = "false"
data1['epochOfLastUpdate'] = int(time.time())
data1['abi'] = cleanedAndOrderedAbiText1
harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash1, body=data1)