import json
import requests
from harvest import Harvest
harvester = Harvest()
#abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750&format=raw"
abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x4c383bdcae52a6e1cb810c76c70d6f31a249ec9b&format=raw"

#txHash = "0xd4dc35a1fe48db820b9a5b24f278c732cd624971dd1279dabbd24e347649ba2b"
txHash = "0x47db6ed6f6ee6d757daf72620b052525523d4e5710d8df524fa4a9d7aa38db5c"

abiData = requests.get(abiUrl).content
abiJSON = json.loads(abiData)
harvester.processSingleTransaction(abiJSON, txHash)

