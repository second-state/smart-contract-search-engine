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
        print("Comparing " + str(a['type']) + " and " + str(b['type']))
        if str(a['type']) > str(b['type']) or str(a['type']) == str(b['type']) and str(a['name']) > str(b['name']) :
            print("Returning True")
            return random.choice(list)
        else:
            print("Returning ?")
            return random.choice(list)
    except:
        # Caters for cases where the name is not present i.e. a fallback function
        print("Comparing " + str(a['type']) + " and " + str(b['type']))
        if str(a['type']) > str(b['type']):
            print("Returning ?")
            return True
        else:
            print("Returning ?")
            return random.choice(list)


def sortJson(_json):
    print(_json)
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
        itemKeys.sort()
        sortedDict = {}
        for key in itemKeys:
            sortedDict[key] = _abi[item][key]
        _abi[item] = sortedDict
    return _abi

def sortInternalListsInJsonObject(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            print("Processing " + str(v) +  " which has a type of " + str(type(v)))
            # Qualify the value as a list of JSON objects
            if type(v) not in (str, bool, int):
                # Qualify list as needing sorting (contains more than one item)
                if len(v) > 1:
                    print("\nSORTING")
                    # Qualify the sortable data is JSON
                    if type(v[0]) is dict:
                        print("Processing:" + str(v))
                        v = sortJson(v)
                        print("Sorted    :" + str(v) + "\n")
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
for i in range(10):
    string = randomizeAndConvertAbiToText(singleAbiJSON)
    randomAbis.append(string)
    print(harvester.shaAnAbi(json.loads(string)))


outputHashes = []
for singleAbi in randomAbis:
    singleAbiJSON = json.loads(singleAbi)
    singleHash = harvester.shaAnAbi(singleAbiJSON)
    outputHashes.append(singleHash)
print("Output hashes are as follows, these should all be exactly the same")

print("Hashes of random ABIs")
for string in randomAbis:
    print(harvester.shaAnAbi(json.loads(string)))
    
print("Hashes of sorted ABIs")
for singleHash in outputHashes:
    print(singleHash)







