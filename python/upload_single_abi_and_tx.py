import json
import requests
from harvest import Harvest
harvester = Harvest()
#abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750&format=raw"
#abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6&format=raw"
#CMT
abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0xf85feea2fdd81d51177f6b8f35f0e6734ce45f5f&format=raw"

#txHash = "0xd4dc35a1fe48db820b9a5b24f278c732cd624971dd1279dabbd24e347649ba2b"
#txHash = "0xa1d92948229a76e4c386d070355e0adec2736e68ff939ce2c77c65d2e702e3d1"
txHash = "0x4e950082ac6360c6f8152331a30cbad0c7d08525c4c3914d5236d6fc15f684e8"

abiData = requests.get(abiUrl).content
abiJSON = json.loads(abiData)
harvester.processSingleTransaction(abiJSON, txHash)

