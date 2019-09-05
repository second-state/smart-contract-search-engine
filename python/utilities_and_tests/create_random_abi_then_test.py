import re
import json
import random
import requests
from harvest import Harvest
harvester = Harvest()

def compareItems(a, b):
    list = []
    list.append(True)
    list.append(False)
    try:
        #print("Comparing " + str(a['type']) + " and " + str(b['type']))
        if str(a['type']) > str(b['type']) or str(a['type']) == str(b['type']) and str(a['name']) > str(b['name']) :
            #print("Returning True")
            return random.choice(list)
        else:
            #print("Returning ?")
            return random.choice(list)
    except:
        # Caters for cases where the name is not present i.e. a fallback function
        #print("Comparing " + str(a['type']) + " and " + str(b['type']))
        if str(a['type']) > str(b['type']):
            #print("Returning ?")
            return True
        else:
            #print("Returning ?")
            return random.choice(list)

def sortJson(_json):
    #print(_json)
    for passnum in range(len(_json)-1,0,-1):
        for item in range(len(_json) - 1):
            if compareItems(_json[item], _json[item+1]) == True:
                temp = _json[item]
                _json[item] = _json[item+1]
                _json[item+1] = temp
    return _json

def sortABIKeys(_abi):
    for item in range(len(_abi)):
        itemKeys = list(_abi[item])
        random.shuffle(itemKeys)
        sortedDict = {}
        for key in itemKeys:
            sortedDict[key] = _abi[item][key]
        _abi[item] = sortedDict
    return _abi

def sortInternalListsInJsonObject(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            #print("Processing " + str(v) +  " which has a type of " + str(type(v)))
            # Qualify the value as a list of JSON objects
            if type(v) not in (str, bool, int):
                # Qualify list as needing sorting (contains more than one item)
                if len(v) > 1:
                    #print("\nSORTING")
                    # Qualify the sortable data is JSON
                    if type(v[0]) is dict:
                        #print("Processing:" + str(v))
                        v = sortJson(v)
                        #print("Sorted    :" + str(v) + "\n")
                else:
                    print("Not enough items in the list to sort, moving on")
            else:
                print(str(v) + " is not a list, moving on ...")
    return _abi

def sanitizeString(_dirtyString):
    cleanString = re.sub(r"[\n\t\s]*", "", _dirtyString)
    return cleanString

def randomizeAndConvertAbiToText(_theAbi):
    theAbiWithSortedLists = sortInternalListsInJsonObject(_theAbi)
    theAbiWithSortedKeys = sortABIKeys(theAbiWithSortedLists)
    theAbiFullySorted = sortJson(theAbiWithSortedKeys)
    sanitizedAbiString = sanitizeString(json.dumps(theAbiFullySorted, sort_keys=False))
    return sanitizedAbiString

randomAbis = []
abiUrl = "https://raw.githubusercontent.com/tpmccallum/mixed_ordered_erc20_abis_for_testing/master/vanilla.txt"
singleAbiString = requests.get(abiUrl).content
singleAbiJSON = json.loads(singleAbiString)
for i in range(20):
    string = randomizeAndConvertAbiToText(singleAbiJSON)
    randomAbis.append(string)

outputHashes = []
print("Hashes of random ABIs")
for rItem in randomAbis:
    hashToPrint = harvester.createHashFromString(rItem)
    print(hashToPrint)
    jsonAbi = json.loads(rItem)
    singleHash = harvester.shaAnAbi(jsonAbi)
    outputHashes.append(singleHash)

print("Output hashes are as follows, these should all be exactly the same")
print("Hashes of sorted ABIs ...")
for singleHash in outputHashes:
    print(singleHash)

# Output will look something like this 
# Hashes of random ABIs
# 0x43064f4849beb02ce7998480bf90ee4dd4123782c6f409da4e800f8021d9cef6
# 0x8375c0a54cc9f59f1b8b4d3dc217100b26ff4be1f487d7fa0220638c47df77af
# 0x58873a40bffb7101ec49f989e2c5dbf34a52a9e923aa09ca9aacf35880f42a91
# 0x8b7aa83fcfad46b2372161d6fbe40fda6fc45438d250b59db493f162bcd6b0b9
# 0xabe80b8b85acff2eb974259801bd046387cfd099fe7994c6965615eb83b60d3f
# 0xffebfc7c425a8a83d2b3001244b25f50d653c27e2bb4fee67ff949a20b9d1755
# 0x6e28a954cb2b60ea83eaf8a7ed3d78ec3c6b0ed857e6faf3aef05e383fcd613a
# 0x12ef421163f667909c79177ebaa9f089f8d769bd81721e6720ecdca6326ab7b0
# 0x1cf4624f8f29a653cb229bfa0e98fb8fd0b4f0a2137a5ae49cd3667c76e58eea
# 0x3666407c593e5685d94a3cd1c0c54218b640abc1f1e98cf6a33f8eff04bb14fb
# 0xf021beb3ed994918d799717a6a64160df12044485dd44bec79abcbf929a88e3a
# 0xf98711c9ba1423288689196e39462df3831683a34d435926985c2c4d5ec89b8f
# 0x795dbf82fcb0bf27f5f69e791f4b29764c82c5974955d01da3a45dfbfbb082c5
# 0x85610b4ac1a76e8abe56bdb814618b886be1918ae70cb8f93dd93080f97b58aa
# 0x5e621dbf325f711f3bff38991cce0cc77896d829ad200f71f612b372c4536cc3
# 0xc1cb5ce434a43098ca92aaf1595e8febd0a285194e689a067cb3e38951e4cc7b
# 0x788dab717ecfbaa13d2f7cbd546891f461937729d673d109ca22b87811ae5728
# 0x4ecea2a1006f29e6278567b39e736fc1a67142d2b6523ba32844df3eef3de3c6
# 0x02ad8681ea982c5633938b99a3b92c4e63c77839331cbe8bd04fa388a17aa092
# 0x449b1639a6fe50280856dea0fbb7a34d4b273997c34c60382be68f67a98c8cdf
# Output hashes are as follows, these should all be exactly the same
# Hashes of sorted ABIs ...
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb
# 0xfa9452aa0b9ba0bf6eb59facc534adeb90d977746f96b1c4ab2db01722a2adcb






