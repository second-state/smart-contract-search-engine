import re
import json
import requests
from harvest import Harvest
harvester = Harvest()

# RAW text of ABIs for sorting and hashing
abiUrls = []
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/erc20abi.txt")
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/erc20Abi2.txt")


outputHashes = []
for singleAbiUrl in abiUrls:
    singleAbiString = requests.get(singleAbiUrl).content
    singleAbiJSON = json.loads(singleAbiString)
    singleHash = harvester.shaAnAbi(singleAbiJSON)
    outputHashes.append(singleHash)
print("Output hashes are as follows, these should all be exactly the same")
for singleHash in outputHashes:
    print(singleHash)
