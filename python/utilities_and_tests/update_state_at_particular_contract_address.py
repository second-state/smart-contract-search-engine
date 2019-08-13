import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

# This is an address from devchain.secondstate.io blockhain
address = "0x3cb71a43c6d9d08b35b48236b759ee201de27679"
# This is a simple parent contract which we are using for demonstrations
abiUrl1 = "https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/parent_abi.txt"
abiData1 = requests.get(abiUrl1).content
abiData1JSON = json.loads(abiData1)

harvester.updateStateOfContractAddress(abiData1JSON, address)
harvester.getDataUsingAddressHash(address)
