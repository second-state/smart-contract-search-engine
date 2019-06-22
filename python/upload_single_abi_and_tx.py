import json
import requests
from harvest import Harvest
harvester = Harvest()
abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750&format=raw"
txHash = "0xd4dc35a1fe48db820b9a5b24f278c732cd624971dd1279dabbd24e347649ba2b"
abiData = requests.get(abiUrl).content
abiJSON = json.loads(abiData)
harvester.processSingleTransaction(abiJSON, txHash)

