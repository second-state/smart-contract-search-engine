import json
import requests
from harvest import Harvest

harvester = Harvest()

#BAT 
abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x0d8775f648430679a709e98d2b0cb6250d2887ef&format=raw"
abiData = requests.get(abiUrl).content


officialAbiJSON = json.loads(abiData)
theDeterministicHash = harvester.shaAnAbi(officialAbiJSON)
cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(officialAbiJSON)
erc20Hashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedAbiText))
# print("\nThe original ABI is as follows:")
# print(officialAbiJSON)
# print("\nThe cleaned and ordered ABI is as follows:")
# print(cleanedAndOrderedAbiText)
# print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicHash)
# print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
# print(erc20Hashes)



txReceipt = harvester.web3.eth.getTransactionReceipt("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
tx = harvester.web3.eth.getTransaction("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
#print("Transaction is as follows:")
#print(tx)
batInstance = harvester.web3.eth.contract(abi=officialAbiJSON, address=harvester.web3.toChecksumAddress("0x0d8775f648430679a709e98d2b0cb6250d2887ef"))
#print(batInstance.abi)

networkAbiJSON = json.dumps(batInstance.abi)
networkAbiObject = json.loads(networkAbiJSON)
networkDeterministicHash = harvester.shaAnAbi(networkAbiObject)
print(networkDeterministicHash)
cleanedAndOrderedNetworkAbiText = harvester.cleanAndConvertAbiToText(officialAbiJSON)
functionDataHashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedNetworkAbiText))
#print(functionDataHashes)

