import json
import requests
from harvest import Harvest

harvester = Harvest()

# Two ABI Contract
#abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x0d8775f648430679a709e98d2b0cb6250d2887ef&format=raw"
#txHash = "0x3bf792736cea9760b7cb604dc5b6527f5b9ddd3d3f7db046fa4103ac489d7626"

abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750&format=raw"
txHash = "0xd4dc35a1fe48db820b9a5b24f278c732cd624971dd1279dabbd24e347649ba2b"

abiData = requests.get(abiUrl).content
abiJSON = json.loads(abiData)

print(abiJSON)
print("\n")
print(txHash)

harvester.processSingleTransaction(abiJSON, txHash)

