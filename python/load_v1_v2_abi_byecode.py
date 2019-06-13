import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

#v1
abiUrl1 = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
abiData1 = requests.get(abiUrl1).content
abiData1JSON = json.loads(abiData1)
theDeterministicHash1 = harvester.shaAnAbi(abiData1JSON)
cleanedAndOrderedAbiText1 = harvester.cleanAndConvertAbiToText(abiData1JSON)


data1 = {}
data1['indexInProgress'] = "false"
data1['epochOfLastUpdate'] = int(time.time())
data1['abi'] = cleanedAndOrderedAbiText1
harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash1, body=data1)


#v2
abiUrl2 = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.abi"
abiData2 = requests.get(abiUrl2).content
abiData2JSON = json.loads(abiData2)
theDeterministicHash2 = harvester.shaAnAbi(abiData2JSON)
cleanedAndOrderedAbiText2 = harvester.cleanAndConvertAbiToText(abiData2JSON)

data2 = {}
data2['indexInProgress'] = "false"
data2['epochOfLastUpdate'] = int(time.time())
data2['abi'] = cleanedAndOrderedAbiText2
harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash2, body=data2)

#v1
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCode = re.sub(r"[\n\t\s]*", "", byteCode)
byteCodeSha = harvester.web3.toHex(harvester.web3.sha3(text=byteCode))
print(byteCode)
print(byteCodeSha)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
harvester.es.index(index=harvester.bytecodeIndex, id=byteCodeSha, body=data)
#v2
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCode = re.sub(r"[\n\t\s]*", "", byteCode)
byteCodeSha = harvester.web3.toHex(harvester.web3.sha3(text=byteCode))
print(byteCode)
print(byteCodeSha)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
harvester.es.index(index=harvester.bytecodeIndex, id=byteCodeSha, body=data)