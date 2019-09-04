import re
import json
import requests
from harvest import Harvest
harvester = Harvest()

# RAW text of ABIs for sorting and hashing
abiUrls = []
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/mixed_ordered_erc20_abis_for_testing/master/vanilla.txt")
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/type_and_name_reversed.txt.txt")
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/mixed_ordered_erc20_abis_for_testing/master/anonymous_and_inputs_reversed.txt")


outputHashes = []
for singleAbiUrl in abiUrls:
    print("Processing: " + singleAbiUrl)
    singleAbiString = requests.get(singleAbiUrl).content
    singleAbiJSON = json.loads(singleAbiString)
    singleHash = harvester.shaAnAbi(singleAbiJSON)
    outputHashes.append(singleHash)
print("Output hashes are as follows, these should all be exactly the same")
for singleHash in outputHashes:
    print(singleHash)
